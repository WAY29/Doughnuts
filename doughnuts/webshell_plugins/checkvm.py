from libs.config import alias, color
from libs.myapp import is_windows
from libs.myapp import send, get_system_code

type_vm = ("Virtual", "KVM", "VMware", "HVM", "RHEV", "VMLite")


@alias()
def run():
    """
    checkvm

    Simply check whether the machine is a virtual machine.
    """
    if (is_windows()):
        commands = (get_system_code(
            'Systeminfo | findstr /i "System Model"', True))
    else:
        commands = (get_system_code(each, True) for each in (
            "dmidecode -s system-product-name", "lshw -class system", "dmesg | grep -i virtual", "lscpu"))
    for command in commands:
        result = send(command).r_text
        if (any(vm in result for vm in type_vm)):
            print(f"\nis VM: {color.green('True')}\n")
        else:
            print(f"\nis VM: {color.red('False')}\n")
