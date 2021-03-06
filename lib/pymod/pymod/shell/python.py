from .shell import Shell


class Python(Shell):
    name = "python"

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        if val is None:
            return "del os.environ[{0!r}]".format(key)
        return "os.environ[{0!r}] = {1!r}".format(key, val)

    def format_shell_function(self, key, val=None):  # pragma: no cover
        return "shell_function_{0} = {1!r}".format(key, val)

    def format_alias(self, key, val=None):  # pragma: no cover
        return "alias_{0} = {1!r}".format(key, val)

