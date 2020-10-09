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
    pf = gget(f"{namespace}.pf")
    gpf = gget(f"general.pf")
    if (plugin_name in gpf):
        pf = gpf
        namespace = "general"
    if(pf.load(plugin_name)):
        print(f'\n{color.green(f"Reload {namespace}.{plugin_name} success")}\n')
    else:
        print(f'\n{color.red(pf.get_message(plugin_name))}\n')
