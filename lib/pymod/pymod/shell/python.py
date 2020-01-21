from .shell import Shell

# --------------------------------------------------------------------------- #
# --  P Y T H O N   S H E L L ----------------------------------------------- #
# --------------------------------------------------------------------------- #
class Python(Shell):
    name = "python"

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        if val is None:
            return "del os.environ[{0!r}]".format(key)
        return "os.environ[{0!r}] = {1!r}".format(key, val)

    def format_shell_function(self, key, val=None):  # pragma: no cover
        return None

    def format_alias(self, key, val=None):  # pragma: no cover
        return None
