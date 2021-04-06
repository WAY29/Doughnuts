from libs.config import alias, gget, color


@alias(True, p="plugin_name", n="namespace")
def run(plugin_name: str, namespace: str = ""):
    """
    reload

    Reload a plugin.(for dev)

    eg: reload {plugin_name} {namespace=current_namespace}

    namespace:
     - main
     - webshell
    """
    namespace = namespace if namespace else gget("namespace")
    plugin_name = str(plugin_name)
    tpf = None
    npf = gget(f"{namespace}.pf")
    gpf = gget(f"general.pf")
    cpf = gget("custom.pf")
    if plugin_name in npf:  # 命令存在
        tpf = npf
    elif plugin_name in gpf:
        tpf = gpf
        namespace = "general"
    elif plugin_name in cpf:
        tpf = cpf
        namespace = "custom"
    if (not tpf):
        print(f'\n{plugin_name}: {color.red("Command Not Found")}\n')
        return
    if(tpf.load(plugin_name)):
        print(f'\n{color.green(f"Reload {namespace}.{plugin_name} success")}\n')
    else:
        print(f'\n{color.red(npf.get_message(plugin_name))}\n')
