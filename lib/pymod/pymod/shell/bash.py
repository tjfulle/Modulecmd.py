import os
import re
from .shell import Shell

# --------------------------------------------------------------------------- #
# --  B  A  S  H    S  H  E  L  L-------------------------------------------- #
# --------------------------------------------------------------------------- #
class Bash(Shell):
    name = 'bash'

    def format_environment_variable(self, key, val=None):
        """Define variable in bash syntax"""
        if val is None:
            return 'unset {0};'.format(key)
        return '{0}="{1}";\nexport {0};'.format(key, val)

    def format_shell_function(self, key, val=None):
        # Define or undefine a bash shell function.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        if val is None:
            return 'unset -f {0} 2> /dev/null || true;'.format(key)
        val = val.rstrip(';')
        return '{0}() {{ {1}; }};'.format(key, val)

    def format_alias(self, key, val=None):
        # Define or undefine a bash shell alias.
        # Modify module definition of function so that there is
        # one and only one semicolon at the end.
        if val is None:
            return 'unalias {0} 2> /dev/null || true;'.format(key)
        val = val.rstrip(';')
        return "alias {0}='{1}';".format(key, val)

    def format_source_command(self, filename):
        return 'source {0}'.format(filename)

    def filter_key(self, key):
        return key.startswith(('BASH_FUNC',))

    def cloned_env(self, environ):  # pragma: no cover
        env = dict()
        for (key, val) in environ.items():
            match = re.search('BASH_FUNC_(?P<n>.*?)%%', key)
            if match:
                key = match.group('n')
                val = val[val.find('{')+1:val.rfind('}')].strip()
            env[key] = val
        return env
