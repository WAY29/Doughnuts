from itertools import chain
from sys import exc_info, stdout
from traceback import print_exception
from typing import List, Tuple, Union

from libs.config import gget

TUPLE_OR_LIST = Union[List, Tuple]


def get_min_string(wordlist):
    return "".join(chain.from_iterable(filter(lambda a: len(a) == 1, [set([chr(y[x]) for y in wordlist]) for x in
                                                                      range(len(min(wordlist, key=len)))])))


try:
    # POSIX system: Create and return a getch that manipulates the tty
    import termios
    import sys
    import tty

    def getch():
        ch = ""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    #  Read arrow keys correctly

    def getchar():
        firstChar = getch()
        if firstChar == '\x1b':
            secChar = getch()
            if (secChar == "["):
                ThrChar = getch()
                if (ThrChar.isdigit()):
                    return {"2~": "Ins", "3~": "Del", "5~": "PgUp",
                            "6~": "PgDn"}[ThrChar + getch()]
                return {"A": "up", "B": "down", "C": "right",
                        "D": "left", "H": "Home", "F": "End"}[ThrChar]
        else:
            return firstChar.encode()

    def print_cyan(text, end="\n"):
        stdout.write("\033[36m" + text + "\033[0m" + end)
        stdout.flush()

    def print_red(text, end="\n"):
        stdout.write("\033[31m" + text + "\033[0m" + end)
        stdout.flush()

except ImportError:
    # Non-POSIX: Return msvcrt's (Windows') getch
    from ctypes import windll
    from msvcrt import getch

    # Read arrow keys correctly

    def getchar():
        firstChar = getch()
        if firstChar == b'\xe0' or firstChar == b'\x00':
            return \
                {b"H": "up", b"P": "down", b"M": "right", b"K": "left", b"G": "Home", b"O": "End", b"R": "Ins", b"S": "Del",
                 b"I": "PgUp", b"Q": "PgDn"}[getch()]
        return firstChar

    def set_cmd_text_color(color):
        std_out_handle = windll.kernel32.GetStdHandle(-11)
        Bool = windll.kernel32.SetConsoleTextAttribute(std_out_handle, color)
        return Bool

    def resetColor():
        set_cmd_text_color(0x0c | 0x0a | 0x09)

    def print_cyan(text, end="\n"):
        set_cmd_text_color(0x0b)
        stdout.write(text + end)
        stdout.flush()
        resetColor()

    def print_red(text, end="\n"):
        set_cmd_text_color(0x0c)
        stdout.write(text + end)
        stdout.flush()
        resetColor()


class LovelyReadline:
    def __init__(self):
        self.STDIN_STREAM = b''
        self.CONTINUE_POINTER = None
        self.CONTINUE_WORDLIST = []
        self.HISTORY = []
        self.HISTORY_POINTER = 0
        self._wordlist = {}
        self._prefix_wordlist = {}
        self._exit_command = "quit"

    def init(self, wordlist: dict, prefix_wordlist: dict,
             exit_command: str = "quit"):
        self._wordlist = wordlist
        self._prefix_wordlist = prefix_wordlist
        self._exit_command = exit_command

    def get_wordlist(self) -> dict:
        return self._wordlist

    def get_prefix_wordlist(self) -> dict:
        return self._prefix_wordlist

    def get_history(self) -> list:
        return self.HISTORY

    def clean_history(self) -> bool:
        self.HISTORY = []
        return True

    def add_prefix_wordlist(self, key: str, value: TUPLE_OR_LIST) -> bool:
        if (isinstance(value, (list, tuple))):
            self._prefix_wordlist[key] = value
            return True
        return False

    def add_wordlist(self, key: str, value: TUPLE_OR_LIST) -> bool:
        if (isinstance(value, (list, tuple))):
            self._wordlist[key] = value
            return True
        return False

    def set_wordlist(self, value: dict) -> bool:
        if (isinstance(value, dict) and value != self._wordlist):
            self._wordlist = value
            return True
        return False

    def set_prefix_wordlist(self, value: dict) -> bool:
        if (isinstance(value, dict) and value != self._prefix_wordlist):
            self._prefix_wordlist = value
            return True
        return False

    def __call__(self, other_delimiter: bytes = b"", ) -> str:
        cmd = ''
        wordlist = self._wordlist
        wordlist["prefix_wordlist"] = []
        # wordlist -> {'command_wordlist'->[命令列表],'prefix_wordlist'->[]}
        # _prefix_wordlist -> {命令名称->[参数列表]}
        end = False
        completion = False

        if (self.CONTINUE_POINTER is not None):
            pointer = self.CONTINUE_POINTER
        else:
            pointer = 0

        history_line = b''
        remaining = ""
        old_stream_len = 0
        old_pointer = 0

        try:
            while True:
                ch, dch = b'', ''
                if (self.CONTINUE_POINTER is not None):
                    self.CONTINUE_POINTER = None
                    wordlist["prefix_wordlist"] = self.CONTINUE_WORDLIST
                else:
                    old_stream_len = len(self.STDIN_STREAM)
                    old_pointer = pointer
                    try:
                        ch = getchar()
                    except Exception:
                        print(f"\nGetline error\n")
                        cmd = ''
                        break

                if (isinstance(ch, bytes)):
                    try:
                        dch = ch.decode()
                    except UnicodeDecodeError:
                        continue

                if (ch == "Del"):
                    ch = b"\b"
                    dch = "\b"

                if (isinstance(ch, str)):
                    read_history = False

                    # switch(ch){ case 'up' case 'down' case 'left' case 'right' ... }
                    # up / down
                    if ch in ["up", "down"]:
                        history_len = len(self.HISTORY)
                        if ch == "up" and self.HISTORY_POINTER > -1:
                            self.HISTORY_POINTER -= 1
                            read_history = True
                        if ch == "down" and self.HISTORY_POINTER < history_len:
                            self.HISTORY_POINTER += 1
                            read_history = True
                        if read_history:
                            if - \
                                    1 < self.HISTORY_POINTER < history_len:  # self.HISTORY_POINTER ∈(1, history_len)
                                self.STDIN_STREAM = self.HISTORY[self.HISTORY_POINTER]
                                pointer = len(self.STDIN_STREAM)
                            else:
                                self.STDIN_STREAM = b''
                                pointer = 0
                    # left
                    if ch == "left" and pointer > 0:
                        pointer -= 1

                    # right
                    if ch == "right":
                        if pointer < len(self.STDIN_STREAM):
                            pointer += 1
                        else:
                            if not history_line and len(
                                    self.CONTINUE_WORDLIST) > 0:
                                # 若未单命令，则列出所有参数
                                history_line = map(
                                    str.encode, self.CONTINUE_WORDLIST)
                            completion = True

                    # home
                    if ch == "Home":  # Home
                        pointer = 0

                    # end
                    if ch == "End":  # End
                        pointer = len(self.STDIN_STREAM)

                    # switch(ch) end...

                # printable
                elif dch and 32 <= ord(dch) < 127:
                    if pointer == len(self.STDIN_STREAM):
                        self.STDIN_STREAM += ch
                    else:
                        self.STDIN_STREAM = self.STDIN_STREAM[:pointer] + \
                            ch + self.STDIN_STREAM[pointer:]
                    pointer += 1

                # enter
                elif ch == b'\r' or ch == b'\n':  # enter
                    end = True

                # \b
                elif (ch == b'\b' or (dch and ord(dch) == 127)) and pointer > 0:  # \b
                    if pointer == len(self.STDIN_STREAM):
                        self.STDIN_STREAM = self.STDIN_STREAM[:-1]
                    else:
                        self.STDIN_STREAM = self.STDIN_STREAM[:pointer -
                                                              1] + self.STDIN_STREAM[pointer:]
                    pointer -= 1

                # \t
                elif ch == b'\t':  # \t
                    if not history_line and len(self.CONTINUE_WORDLIST) > 0:
                        # 若未单命令，则列出所有参数
                        history_line = map(str.encode, self.CONTINUE_WORDLIST)
                    completion = True

                # ctrl+d
                elif dch and ord(dch) == 4:  # ctrl+d
                    print_cyan(self._exit_command)
                    cmd = 'quit'
                    break

                # ctrl+c
                elif dch and ord(dch) == 3:  # ctrl+c
                    print_cyan('^C')
                    break

                # ctrl+l
                elif dch and ord(dch) == 12:  # ctrl+l
                    cmd = 'cls'
                    break

                # 如果完成
                if completion:
                    completion = False
                    # 若历史行为一行命令则直接补全
                    if history_line and isinstance(history_line, bytes):
                        self.STDIN_STREAM = history_line
                        pointer = len(history_line)
                    # 若历史行为命令列表则列出
                    elif isinstance(history_line, list):
                        cmd = ''
                        self.CONTINUE_POINTER = pointer
                        word = self.STDIN_STREAM.split(b" ")[-1]
                        if other_delimiter:
                            word = word.split(other_delimiter)[-1]
                        stdout.write(
                            "\n" +
                            b"  ".join(
                                word +
                                last_word for last_word in history_line).decode() +
                            "\n")
                        break
                    # 若为参数补全
                    elif isinstance(history_line, map):
                        self.CONTINUE_POINTER = pointer
                        params = {"-": [], "--": []}

                        for param in history_line:
                            if param.startswith(b"--"):
                                params["--"].append(param)
                            else:
                                params["-"].append(param)

                        line = [a + b"/" + b for a,
                                b in zip(params["-"],
                                         params["--"])] + max(params["-"],
                                                              params["--"],
                                                              key=len)[len(min(params["-"],
                                                                               params["--"],
                                                                               key=len)):]
                        stdout.write(
                            "\n" +
                            b"  ".join(
                                last_word for last_word in line).decode() +
                            "\n")
                        break

                stream_len = len(self.STDIN_STREAM)
                history_len = len(self.HISTORY)
                remaining_len = len(remaining)
                clean_len = old_stream_len + remaining_len
                stdout.write(
                    "\b" *
                    old_pointer +
                    " " *
                    clean_len +
                    "\b" *
                    clean_len)  # 清空原本输入
                print_cyan(self.STDIN_STREAM.decode(), end="")
                if remaining:
                    remaining = ""
                if end:  # 结束输入
                    stdout.write('\n')
                    stdout.flush()
                    cmd = self.STDIN_STREAM.decode()
                    # 加入历史命令
                    if cmd and (not history_len or (
                            history_len and self.HISTORY[-1] != cmd.encode())):
                        self.HISTORY.append(cmd.encode())
                    self.HISTORY_POINTER = len(self.HISTORY)
                    break
                if history_line:
                    history_line = b''
                if not self.STDIN_STREAM:
                    continue
                temp_history_lines = [line[stream_len:] for line in reversed(self.HISTORY) if (
                    line.startswith(self.STDIN_STREAM) and self.STDIN_STREAM != line)]
                # 若有历史命令，输出剩余的部分
                if temp_history_lines and temp_history_lines[0]:
                    remaining = min(temp_history_lines, key=len)
                # 按 "[空格]" 分离命令/参数
                stream_list = self.STDIN_STREAM.split(b" ")
                # 获取命令
                command = b" ".join(
                    stream_list[:-1]).decode() if len(stream_list) > 1 else self.STDIN_STREAM.decode()
                # 若命令存在命令列表中
                if command in self._prefix_wordlist:
                    # 获取命令配置的参数
                    prefix_wordlist = self._prefix_wordlist.get(command, [])
                    if prefix_wordlist and wordlist["prefix_wordlist"] != prefix_wordlist:
                        wordlist["prefix_wordlist"] = prefix_wordlist
                        self.CONTINUE_WORDLIST = prefix_wordlist
                else:
                    self.CONTINUE_WORDLIST = []
                    command = b''
                # 若有补全单词，输出剩余的部分
                word = stream_list[-1]
                if other_delimiter:
                    word = word.split(other_delimiter)[-1]
                if word:
                    word_len = len(word)
                    # 找出以输入的字符开头的命令
                    temp_word_lines = [line[word_len:].encode() for line in set(
                        wordlist['command_wordlist' if not command else 'prefix_wordlist']) if
                        (line.startswith(word.decode()))]
                    if temp_word_lines and temp_word_lines[0]:
                        # 取出最短的命令关键字
                        temp_remaining = min(temp_word_lines, key=len)
                        temp_history_line = self.STDIN_STREAM + temp_remaining
                        # 再与历史命令做对比，最后取最短
                        if (not history_line or len(
                                temp_history_line) < len(history_line)):
                            remaining = temp_remaining
                else:
                    temp_word_lines = []
                if remaining:
                    # 罗列符合补全的所有命令
                    total_lines = temp_history_lines + temp_word_lines
                    # 在符合补全条件的命令中取出唯一最短，若存在多个最短则返回''
                    less_bytes = get_min_string(total_lines).encode()
                    stdout.write(
                        remaining.decode() +
                        "\b" *
                        len(remaining))  # 输出补全提示
                    if (less_bytes):  # 允许补全公共子串
                        history_line = self.STDIN_STREAM + less_bytes
                    elif (len(temp_word_lines) > 1):  # 多个候选词,保留输入流并返回
                        cmd = ''
                        history_line = temp_word_lines
                    else:
                        history_line = self.STDIN_STREAM + remaining
                stdout.write("\b" * (stream_len - pointer))
                stdout.flush()

        except Exception:
            print_red('Error')
            debug = gget("DEBUG.LOOP")
            exc_type, exc_value, exc_tb = exc_info()
            if debug:
                print_exception(exc_type, exc_value, exc_tb)
            cmd = ''

        if (self.CONTINUE_POINTER is None):
            self.STDIN_STREAM = b''
        log_filepath = gget("log_filepath")
        if (log_filepath):
            f = open(log_filepath, "a+")
            f.write(cmd + "\n")
            f.close()
        return cmd


if (__name__ == "__main__"):
    pass
