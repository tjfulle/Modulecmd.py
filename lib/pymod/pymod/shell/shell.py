from six import StringIO


class Shell(object):
    name = None

    def format_environment_variable(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_shell_function(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_alias(self, key, val=None):  # pragma: no cover
        raise NotImplementedError

    def format_source_command(self, filename):  # pragma: no cover
        raise NotImplementedError

    def switch(self):  # pragma: no cover
        raise NotImplementedError

    def format_output(
        self, environ, aliases=None, shell_functions=None, files_to_source=None
    ):
        sio = StringIO()

        for (envar, defn) in environ.items():
            sio.write(self.format_environment_variable(envar, defn) + "\n")

        if aliases is not None:
            for (alias, defn) in aliases.items():
                sio.write(self.format_alias(alias, defn) + "\n")

        if shell_functions is not None:
            for (fun, defn) in shell_functions.items():
                sio.write(self.format_shell_function(fun, defn) + "\n")

        if files_to_source:
            for (filename, args) in files_to_source:
                command = self.format_source_command(filename, *args)
            sio.write(command + ";\n")

        return sio.getvalue()

    def filter_env(self, environ):
        env = dict()
        for (key, val) in environ.items():
            if self.filter_key(key):
                continue
            env[key] = val
        return env

    def filter_key(self, key):
        return False
