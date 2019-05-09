import os
import re

from .shell import Shell

CSH_LIMIT = 4000

# --------------------------------------------------------------------------- #
# --  C  S  H    S  H  E  L  L----------------------------------------------- #
# --------------------------------------------------------------------------- #
class Csh(Shell):
    name = 'csh'

    def format_environment_variable(self, key, val=None):
        """Define variable in bash syntax"""
        if val is None:
            return 'unsetenv {0};'.format(key)
        else:
            # csh barfs on long env vars
            if len(val) > CSH_LIMIT:
                if key == 'PATH':
                    tty.warning('PATH exceeds {0} characters, truncating '
                                    'and appending /usr/bin:/bin...')
                    newval = '/usr/bin' + os.pathsep + '/bin'
                    for item in val.split(os.pathsep):
                        tmp = item + os.pathsep + newval
                        if len(tmp) < CSH_LIMIT:
                            newval = tmp
                        else:
                            break
                else:
                    msg = '{0} exceeds {1} characters, truncating...'
                    tty.warning(msg.format(key, CSH_LIMIT))
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
            return 'unalias {0} 2> /dev/null || true;'.format(key)
        val = val.rstrip(';')
        # Convert $n -> \!:n
        val = re.sub(r'\$([0-9]+)', r'\!:\1', val)
        # Convert $* -> \!*
        val = re.sub(r'\$\*', r'\!*', val)
        return "alias {0} '{1}';".format(key, val)

    def source_command(self, filename):
        return 'source {0}'.format(filename)
