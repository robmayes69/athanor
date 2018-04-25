from evennia.utils.utils import fuzzy_import_from_module


def import_property(path):
    """
    Frontend for Evennia's fuzzy_importer. This is largely used by the load process to load Validators.

    Args:
        path (str): A python path to the variable/class/function whatever you want out of a module.

    Returns:
        Hopefully, a function object or a variable or something of that sort.
    """
    module, thing = path.rsplit('.', 1)
    return fuzzy_import_from_module(module, thing)