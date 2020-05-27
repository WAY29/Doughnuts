from libs.app import Loop_init, run_loop
from libs.myapp import banner
from libs.config import gget, color, add_namespace_callback


class My_Loop_init(Loop_init):
    def set_platforms(self) -> dict:
        return {"main": "main_plugins", "webshell": "webshell_plugins", "general": "general", "encode": "encode"}

    def set_prompts(self) -> dict:
        return {"main": ":>", "webshell": "=>"}


@add_namespace_callback
def change_prompt():
    namespace = gget("namespace")
    if (namespace == "main"):
        print(color.yellow("[?|help]           ") + color.cyan("Output the help document for the command or all help menu"))
        print(color.yellow("[s|show]           ") + color.cyan("Show log webshells"))
        print(color.yellow("[se|show_encoders] ") + color.cyan("Show available encoders"))
        print(color.yellow("[l|load]           ") + color.cyan("Load a webshell from log"))
        print(color.yellow("[c|connect]        ") + color.cyan("Connect to a webshell"))
        print(color.yellow("[check]            ") + color.cyan("Check if each webshell is alive"))
        print(color.yellow("[q|quit]           ") + color.cyan("Quit this program"))
    elif (namespace == "webshell"):
        print("\n[COMMON]\n")
        print(color.yellow("[?|help]       ") + color.cyan("Output the help document for the command or all help menu"))
        print(color.yellow("[i|info]       ") + color.cyan("Show website information"))
        print(color.yellow("[ls]           ") + color.cyan("List information about the files"))
        print(color.yellow("[b|back]       ") + color.cyan("Back to main menu"))
        print("\n[SHELL]\n")
        print(color.yellow("[bs|bindshell] ") + color.cyan("(Only for *unix) Bind a port and wait for someone to connect to get a shell"))
        print(color.yellow("[re|reverse]   ") + color.cyan("Reverse shell"))
        print(color.yellow("[rs|reshell]   ") + color.cyan("(Only for both system is linux) (Testing command) Bind a port and waiting for target connect back to get a full shell"))
        print(color.yellow("[s|shell]      ") + color.cyan("Enter interactive shell"))
        print(color.yellow("[ws|webshell]  ") + color.cyan("Enter interactive webshell"))
        print("\n[FILE]\n")
        print(color.yellow("[r|read]       ") + color.cyan("Read file/files"))
        print(color.yellow("[w|write]      ") + color.cyan("Write file"))
        print(color.yellow("[m|modify]     ") + color.cyan("Modify file"))
        print(color.yellow("[u|upload]     ") + color.cyan("Upload file"))
        print(color.yellow("[d|download]   ") + color.cyan("Download file"))
        print(color.yellow("[del|delete]   ") + color.cyan("Delete file/files"))
        print(color.yellow("[dump]         ") + color.cyan("Package and compress files in a folder and download it"))
        print("\n[SEARCH]\n")
        print(color.yellow("[search]       ") + color.cyan("Search file by glob, pattern support . * [...]"))
        print(color.yellow("[fwpf]         ") + color.cyan("Search writable php file"))
        print(color.yellow("[fc]           ") + color.cyan("Search config file"))
        print("\n[OTHER]\n")
        print(color.yellow("[ag|agent]     ") + color.cyan("Intranet agent"))
        print(color.yellow("[t|touch]      ") + color.cyan("Specify a file whose modification time stamp is the same as a random file in the current directory"))
        print(color.yellow("[pdf]          ") + color.cyan("Print disable functions"))
        print(color.yellow("[ps|portscan]  ") + color.cyan("Scan intranet ports"))
        print(color.yellow("[socks]  ") + color.cyan("(Only for *unix) Run a socks5 server on the target machine"))
        print()


if __name__ == "__main__":
    banner()
    run_loop(My_Loop_init(), leave_message="Bye! Doughnuts:)")
