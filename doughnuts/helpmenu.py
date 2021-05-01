
from libs.config import add_namespace_callback, gget


GENERAL_DOC = ""
MAIN_DOC = ""
WEBSHELL_DOC = ""
CUSTOM_WEBSHELL_DOC = ""


def register_helpmenu():
    @add_namespace_callback
    def helpmenu():
        global GENERAL_DOC, MAIN_DOC, WEBSHELL_DOC, CUSTOM_WEBSHELL_DOC
        namespace = gget("namespace")
        if (namespace == "main"):
            # print(gget("type_func_dict", namespace="general")["general"])
            if (not GENERAL_DOC):
                GENERAL_DOC = "\n".join(gget(func_name + ".helpdoc", namespace="general")
                                        for func_name in gget("type_func_dict", namespace="general")["general"])
            if (not MAIN_DOC):
                MAIN_DOC = "\n".join(gget(func_name + ".helpdoc", namespace=namespace)
                                     for func_name in gget("type_func_dict", namespace=namespace)["general"])
            print(GENERAL_DOC)
            print(MAIN_DOC + "\n")
        elif (namespace == "webshell"):
            if (not WEBSHELL_DOC):
                type_list = gget("type_list", namespace=namespace)
                type_list.sort()
                for _type in type_list:
                    WEBSHELL_DOC += "\n[%s]\n\n" % _type
                    WEBSHELL_DOC += "\n".join(gget(func_name + ".helpdoc", namespace=namespace)
                                              for func_name in gget("type_func_dict", namespace=namespace)[_type])
                    WEBSHELL_DOC += "\n"
            if (not CUSTOM_WEBSHELL_DOC):
                CUSTOM_WEBSHELL_DOC = "\n".join(gget(func_name + ".helpdoc", namespace="custom", default="")
                                                for func_name in gget("type_func_dict", namespace="custom", default={'general': ()})["general"])
            print("\n[GENERAL]\n")
            print(GENERAL_DOC)
            print(WEBSHELL_DOC + "\n")
            print("\n[CUSTOM]\n")
            print(CUSTOM_WEBSHELL_DOC + "\n")
