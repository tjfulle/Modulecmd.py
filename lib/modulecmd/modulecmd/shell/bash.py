import re
from .shell import Shell


class Bash(Shell):
    name = "bash"

    def format_environment_variable(self, key, val=None):
        """Define variable in bash syntax"""
        if val is None:
            return "unset {0};".format(key)
        return '{0}="{1}";\nexport {0};'.format(key, val)

    def format_shell_function(self, key, val=None):
        # Define or undefine a bash shell function.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        if val is None:
            return "unset -f {0} 2> /dev/null || true;".format(key)
        val = val.rstrip(";")
        return "{0}() {{ {1}; }};".format(key, val)

    def format_alias(self, key, val=None):
        # Define or undefine a bash shell alias.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        if val is None:
            return "unalias {0} 2> /dev/null || true;".format(key)
        val = val.rstrip(";")
        return "alias {0}='{1}';".format(key, val)

    def format_source_command(self, filename, *args):
        return "source {0} {1}".format(filename, " ".join(args)).strip()

    def filter_key(self, key):
        return key.startswith(("BASH_FUNC",))

    def cloned_env(self, environ):  # pragma: no cover
        env = dict()
        for (key, val) in environ.items():
            match = re.search("BASH_FUNC_(?P<n>.*?)%%", key)
            if match:
                key = match.group("n")
                val = val[val.find("{") + 1 : val.rfind("}")].strip()
            env[key] = val
        return env

    def switch(self):  # pragma: no cover
        """Switch the underlying module implementation"""
        import os
        from six import StringIO
        from modulecmd.util import filesystem

        for (key, val) in os.environ.items():
            if key.startswith("BASH_FUNC_module"):
                break
        else:
            raise Exception("Unable to find module bash function")
        current_module_implementation = "modulecmd" if "PYMOD_CMD" in val else "tcl"

        s = StringIO()
        if current_module_implementation == "modulecmd":
            if os.getenv("LMOD_CMD"):
                modulecmd = os.environ["LMOD_CMD"]
            else:
                modulecmd = filesystem.which("modulecmd")
                if modulecmd is None:
                    raise Exception("Unable to find modulecmd executable")
            s.write('module() { eval $(%s bash "$@"); };' % modulecmd)
            s.write("unset -f module;")
            s.write('modulecmd() { eval $(python -E $PYMOD_CMD bash "$@"); };')
            s.write("export -f modulecmd;")
            s.write('module() { eval $(%s bash "$@"); };' % modulecmd)
            s.write("export -f module;")
        else:
            s.write("unset -f module;")
            s.write("unset -f modulecmd;")
            s.write('module() { eval $(python -E $PYMOD_CMD bash "$@"); };')
            s.write("export -f module;")
        return s.getvalue()
