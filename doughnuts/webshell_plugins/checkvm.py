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
        command = [get_system_code(
            'Systeminfo | findstr /i "System Model"', True)]
    else:
        command = [get_system_code(each, True) for each in [
            "dmidecode -s system-product-name", "lshw -class system", "dmesg | grep -i virtual", "lscpu"]]
    for line in command:
        result = send(line).r_text
        for vm in type_vm:
            if(vm in result):
                print(f"\nis VM: {color.green('True')}\n")
                return
    print(f"\nis VM: {color.red('False')}\n")
