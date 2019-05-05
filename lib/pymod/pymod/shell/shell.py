import sys


# --------------------------------------------------------------------------- #
# --  B  A  S  E    S  H  E  L  L-------------------------------------------- #
# --------------------------------------------------------------------------- #
class Shell(object):
    name = None

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_shell_function(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_alias(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def source_command(self, filename):  # pragma: no cover
        raise NotImplementedError

    def dump(self, environ):
        sys.stdout.write(self.format_commands(environ))

    def format_commands(self, environ):
        string = []
        for (envar, defn) in environ.items():
            string.append(self.format_environment_variable(envar, defn))
        for (alias, defn) in environ.aliases.items():
            string.append(self.format_alias(alias, defn))
        for (fun, defn) in environ.shell_functions.items():
            string.append(self.format_shell_function(fun, defn))
        return '\n'.join(string)

    def filter(self, environ):
        pass
