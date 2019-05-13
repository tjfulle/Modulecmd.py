compiler_vendors = ['gcc', 'clang', 'intel', 'pgi', 'ucc']
mpi_vendors = ['openmpi', 'mpich', 'umpi']


class Namespace:
    def __init__(self):
        self.compiler_vendor = None
        self.compiler_version = None
        self.mpi_vendor = None
        self.mpi_version = None


def spec(module, loaded_modules):
    """Simple function which lets a module know about its dependents"""
    unlocked_by = module.unlocked_by(loaded_modules)

    ns = Namespace()
    if not unlocked_by:
        return ns

    for item in unlocked_by:
        if item.name in compiler_vendors:
            ns.compiler_vendor = item.name
            ns.compiler_version = item.version.string
        elif item.name in mpi_vendors:
            ns.mpi_vendor = item.name
            ns.mpi_version = item.version.string

    return ns
