# --------------------------------------------------------------------------- #
# --  B  A  S  E    S  H  E  L  L-------------------------------------------- #
# --------------------------------------------------------------------------- #
class Shell(object):
    name = None

    @staticmethod
    def initshell(*args):  #pragma no cover
        raise NotImplementedError

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_shell_function(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_alias(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def dump(self, envar_keys, envars,
             alias_keys=None, aliases=None,
             fcn_keys=None, fcns=None):
        string = []
        alias_keys = alias_keys or []
        fcn_keys = fcn_keys or []
        for key in envar_keys:
            string.append(self.format_environment_variable(key, envars[key]))
        for key in alias_keys:
            string.append(self.format_alias(key, aliases[key]))
        for key in fcn_keys:
            string.append(self.format_shell_function(key, fcns[key]))
        return '\n'.join(string)

    @staticmethod
    def onoff(arg):
        return {True: '1', False: '0'}[arg]

    def filter_environ(self):
        raise NotImplementedError
