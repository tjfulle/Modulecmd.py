import os

from .shell import Shell

# --------------------------------------------------------------------------- #
# --  P Y T H O N   S H E L L ----------------------------------------------- #
# --------------------------------------------------------------------------- #
class Python(Shell):
    name = 'python'

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        if val is None:
            return 'del os.environ[{0!r}]'.format(key)
        return 'os.environ[{0!r}] = {1!r}'.format(key, val)

    def format_shell_function(self, key, val=None):  # pragma: no cover
        return None

    def format_alias(self, key, val=None):  # pragma: no cover
        return None

    def dump(self, envar_keys, envars,
             alias_keys=None, aliases=None,
             fcn_keys=None, fcns=None):
        string = []
        for key in envar_keys:
            string.append(self.format_environment_variable(key, envars[key]))
        return '\n'.join(string)
