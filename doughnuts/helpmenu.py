
from libs.config import add_namespace_callback, color, gget


def register_helpmenu():
    @add_namespace_callback
    def helpmenu():
        namespace = gget("namespace")
        if (namespace == "main"):
            print(color.yellow("[?|help]           ") + color.cyan(
                "Output the help document for the command or all help menu"))
            print(color.yellow("[s|show]           ") +
                  color.cyan("Show log webshells"))
            print(color.yellow("[se|show_encoders] ") +
                  color.cyan("Show available encoders"))
            print(color.yellow("[sw|switch]        ") +
                  color.cyan("(for input Non-alphanumeric) Switch input to raw input"))
            print(color.yellow("[gen|generate]     ") +
                  color.cyan("Generate a webshell using doughnuts encoding"))
            print(color.yellow("[l|load]           ") +
                  color.cyan("Load a webshell from log"))
            print(color.yellow("[c|connect]        ") +
                  color.cyan("Connect to a webshell"))
            print(color.yellow("[check]            ") +
                  color.cyan("Check if each webshell is alive"))
            print(color.yellow("[rm|remove]        ") +
                  color.cyan("Remove a webshell log"))
            print(color.yellow("[log]              ") +
                  color.cyan("(Only for *unix) Write input and output to the log"))
            print(color.yellow("[!|lsh]            ") +
                  color.cyan("Run a command on local machine"))
            print(color.yellow("[proxy]            ") +
                  color.cyan("Set proxy for requests"))
            print(color.yellow("[get]              ") +
                  color.cyan("Get variable(s), use #{varname} to use it"))
            print(color.yellow("[set]              ") +
                  color.cyan("Set variable, use #{varname} to use it"))
            print(color.yellow("[save]             ") +
                  color.cyan("Save the configuration of the variable(s) to variables.config"))
            print(color.yellow("[reload]           ") +
                  color.cyan("Reload a plugin"))
            print(color.yellow("[q|quit]           ") +
                  color.cyan("Quit this program"))
        elif (namespace == "webshell"):
            print("\n[COMMON]\n")
            print(color.yellow("[?|help]       ") + color.cyan(
                "Output the help document for the command or all help menu"))
            print(color.yellow("[i|info]       ") +
                  color.cyan("Show website information"))
            print(color.yellow("[env|getenv]   ") +
                  color.cyan("print PHP environment variables by ini_get"))
            print(color.yellow("[ls|dir]       ") +
                  color.cyan("List information about the files"))
            print(color.yellow("[cd]           ") +
                  color.cyan("Change the working directory"))
            print(color.yellow("[pdf]          ") +
                  color.cyan("Print disable functions"))
            print(color.yellow("[pwd]          ") +
                  color.cyan("Print the name of the current working directory"))
            print(color.yellow("[!|lsh]        ") +
                  color.cyan("Run a command on local machine"))
            print(color.yellow("[b|back]       ") +
                  color.cyan("Back to main menu"))
            print(color.yellow("[q|quit]       ") +
                  color.cyan("Quit this program"))
            print("\n[SHELL]\n")
            print(color.yellow("[bs|bindshell] ") + color.cyan(
                "Bind a port and wait for someone to connect to get a shell"))
            print(color.yellow("[re|reverse]   ") +
                  color.cyan("Reverse shell"))
            print(color.yellow("[rs|reshell]   ") + color.cyan(
                "(Only for both system is linux) (Testing command) Bind a local port and waiting for target connect back to get a full shell"))
            print(color.yellow("[s|shell]      ") + color.cyan(
                "Get a temporary shell of target system by system function or just run a shell command"))
            print(color.yellow("[ws|webshell]  ") + color.cyan(
                "Get a webshell of target system or just run a webshell command"))
            print(color.yellow("[exec|execute] ") +
                  color.cyan("Execute custom php code"))
            print("\n[FILE]\n")
            print(color.yellow("[c|cat]        ") + color.cyan("Read file(s)"))
            print(color.yellow("[w|write]      ") + color.cyan("Write file"))
            print(color.yellow("[e|edit]       ") + color.cyan("Modify file"))
            print(color.yellow("[u|upload]     ") + color.cyan("Upload file"))
            print(color.yellow("[mu|mupload]     ") + color.cyan("Upload file by Block compression and multi threads"))
            print(color.yellow("[d|download]   ") +
                  color.cyan("Download file"))
            print(color.yellow("[mv|move]      ") +
                  color.cyan("Rename file or move it to new_file_path"))
            print(color.yellow("[rm|remove]    ") +
                  color.cyan("Delete target system file(s)"))
            print(color.yellow("[chmod]        ") +
                  color.cyan("(Only for *unix) Changes file mode"))
            print(color.yellow("[t|touch]      ") + color.cyan(
                "Create an empty file or (Only for *unix) Specify a file whose modification time stamp is the same as a random file in the current directory"))
            print(color.yellow("[dump]         ") +
                  color.cyan("Package and compress files in a folder and download it"))
            print("\n[DETECT]\n")
            print(color.yellow("[search]       ") +
                  color.cyan("Search file(s) from target system (Support regular expression)"))
            print(color.yellow("[fwpf]         ") +
                  color.cyan("Search writable php file"))
            print(color.yellow("[fc]           ") +
                  color.cyan("Search config file"))
            print(color.yellow("[fl]           ") +
                  color.cyan("Search log file (access.log,error.log)"))
            print(color.yellow("[priv]         ") +
                  color.cyan("(Only for *unix) Find all files with suid belonging to root and try to get privilege escalation tips"))
            print(color.yellow("[checkvm]      ") +
                  color.cyan("Simply check whether the machine is a virtual machine"))
            print(color.yellow("[av]           ") +
                  color.cyan("(Only for windows) Detect anti-virus software running on the target system"))
            print("\n[DATABASE]\n")
            print(color.yellow("[db_init]      ") +
                  color.cyan("Initialize the database connection"))
            print(color.yellow("[db_info]      ") +
                  color.cyan("Output database information"))
            print(color.yellow("[db_use]       ") +
                  color.cyan("Change current database"))
            print(color.yellow("[db_dbs]       ") +
                  color.cyan("Output all databases"))
            print(color.yellow("[db_tables]    ") +
                  color.cyan("Output all tables of a database"))
            print(color.yellow("[db_columns]   ") +
                  color.cyan("Output all columns of a table"))
            print(color.yellow("[db_shell]     ") +
                  color.cyan("Get a temporary sql shell of target system"))
            print(color.yellow("[db_dump]      ") +
                  color.cyan("Dump a database to a file"))
            print("\n[OTHER]\n")
            print(color.yellow("[cls|clear]    ") + color.cyan("Clear screen"))
            print(color.yellow("[log]          ") +
                  color.cyan("(Only for *unix) Write input and output to the log"))
            print(color.yellow("[sw|switch]    ") +
                  color.cyan("(for input Non-alphanumeric) Switch input to raw input"))
            print(color.yellow("[get]          ") +
                  color.cyan("Get variable(s), use #{varname} to use it"))
            print(color.yellow("[set]          ") +
                  color.cyan("Set variable, use #{varname} to use it"))
            print(color.yellow("[reload]       ") +
                  color.cyan("Reload a plugin"))
            print(color.yellow("[ag|agent]     ") +
                  color.cyan("Intranet agent"))
            print(color.yellow("[bobd]         ") + color.cyan(
                "(Only for *unix) Try to bypass open_basedir by ini_set and chdir"))
            print(color.yellow("[bdf]          ") +
                  color.cyan("Try to bypass disable_functions"))
            print(color.yellow("[proxy]        ") +
                  color.cyan("Set proxy for requests"))
            print(color.yellow("[ps|portscan]  ") +
                  color.cyan("Scan intranet ports"))
            print(color.yellow("[socks]        ") + color.cyan(
                "(Only for *unix) Run a socks5 server on the target system by python"))
            print()
