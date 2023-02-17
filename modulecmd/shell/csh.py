import os
import re

from .shell import Shell
import modulecmd.xio as xio

CSH_LIMIT = 4000


class Csh(Shell):
    name = "csh"

    def format_environment_variable(self, key, val=None):
        """Define variable in bash syntax"""
        if val is None:
            return "unsetenv {0};".format(key)
        else:
            # csh barfs on long env vars
            if len(val) > CSH_LIMIT:
                if key == "PATH":
                    val = self.truncate_path(val)
                else:
                    msg = "{0} exceeds {1} characters, truncating..."
                    xio.warn(msg.format(key, CSH_LIMIT))
                    val = val[:CSH_LIMIT]
        return 'setenv {0} "{1}";'.format(key, val)

    def format_shell_function(self, key, val=None):
        # Define or undefine a bash shell function.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        return self.format_alias(key, val)

    def format_alias(self, key, val=None):
        # Define or undefine a bash shell alias.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        if val is None:
            return "unalias {0} 2> /dev/null || true;".format(key)
        val = val.rstrip(";")
        # Convert $n -> \!:n
        val = re.sub(r"\$([0-9]+)", r"\!:\1", val)
        # Convert $* -> \!*
        val = re.sub(r"\$\*", r"\!*", val)
        return "alias {0} '{1}';".format(key, val)

    def format_source_command(self, filename):
        return "source {0}".format(filename)

    def truncate_path(self, path):
        xio.warn(
            "PATH exceeds {0} characters, truncating "
            "and appending /usr/bin:/bin".format(CSH_LIMIT)
        )
        truncated = ["/usr/bin", "/bin"]
        length = len(truncated[0]) + len(truncated[1]) + 1
        for (i, item) in enumerate(path.split(os.pathsep)):
            if (len(item) + 1 + length) > CSH_LIMIT:
                break
            else:
                length += len(item) + 1
                truncated.insert(-2, item)
        return os.pathsep.join(truncated)
