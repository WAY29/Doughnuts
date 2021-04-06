from libs.config import alias, gget, order_alias, set_namespace
import inspect


@alias(True, func_alias="?", o="order")
def run(order: str = ""):
    """
    help

    Output the help document for the command or all help menu.

    eg: help {order}
    """
    if (order == ""):
        set_namespace(gget("namespace"), True, False)
        return
    tpf = None
    gpf = gget(f"general.pf")
    npf = gget(f"{gget('namespace')}.pf")
    cpf = gget(f"custom.pf")
    order = order_alias(order)
    if (order in npf):
        tpf = gpf
    elif (order in gpf):
        tpf = npf
    elif (order in cpf):
        tpf = cpf
    elif order:
        print("%s object is not command-function" % order)
        return
    api = gget("api")
    func = getattr(tpf[order], api)
    if (func.__doc__):
        print(func.__doc__)
    block = " " * 4
    block_two = block * 2
    sig = inspect.signature(func)
    folders_namespace = gget("folders_namespace")
    func_folder, func_name = func.__module__.split(".")
    func_reverse_alias = gget(
        "%s.reverse_alias" % func_name, folders_namespace[func_folder]
    )
    if (len(sig.parameters)):
        print("%sCommand Args:" % block)
    for k, v in sig.parameters.items():
        arg = "--%s" % k
        if k in func_reverse_alias:
            arg = "-%s,%s" % (func_reverse_alias[k], arg)
        desc = str(v).split(":")
        if len(desc) > 1:  # 存在参数类型
            desc = desc[1].split("=")
            if len(desc) > 1:  # 存在默认值
                desc = "[%s] %s (Default: %s)" % (
                    desc[0].strip(),
                    k,
                    desc[1].strip(),
                )
            else:
                desc = "[%s] %s" % (desc[0].strip(), k)
                arg = "%s(*)" % arg
        else:
            desc = "[?] %s" % desc[0]
            arg = "%s(?)" % arg
        print("%s%-25s%s%s\n" % (block_two, arg, block_two, desc))
