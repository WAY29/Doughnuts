from libs.config import alias, color
from libs.myapp import is_windows
from libs.myapp import send, get_system_code

vm_keywords = ("Virtual", "KVM", "VMware", "HVM", "RHEV", "VMLite")


@alias(_type="DETECT")
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
    isvm = False

    # detect vm by keyword
    for command in commands:
        result = send(command).r_text
        if (any(vm in result for vm in vm_keywords)):
            isvm = True
            break
    print(f"\nis VM: {color.red('False') if (not isvm) else color.green('True')}\n")
