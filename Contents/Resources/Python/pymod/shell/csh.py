import os
import re

from .shell import Shell
from ..user import pymod_env_key

CSH_LIMIT = 4000

# --------------------------------------------------------------------------- #
# --  C  S  H    S  H  E  L  L----------------------------------------------- #
# --------------------------------------------------------------------------- #
class Csh(Shell):
    name = 'csh'

    @staticmethod
    def initshell(moduleshome, modulecmd, modulepath, isolate):
        mh_key = pymod_env_key('MODULESHOME', isolate=isolate)
        mp_key = pymod_env_key('MODULEPATH', isolate=isolate)
        pymod_pkg = os.path.join(moduleshome, 'Contents/Resources/Python/pymod')
        l = ['setenv PYMOD_DIR {0}'.format(moduleshome),
             'setenv PYMOD_PKG_DIR {0}'.format(pymod_pkg),
             'setenv {0} {1}'.format(mh_key, moduleshome),
             'setenv PYMOD_CMD {0}'.format(modulecmd),
             'setenv {0} {1}'.format(mp_key, modulepath),
             'alias pymod eval `python -B -E {0} csh !*`'.format(modulecmd),
             'setenv __PYMOD_ISOLATED__ {0}'.format(Csh.onoff(isolate)),
             ]
        if not isolate:
            l.append('alias module eval `python -B -E {0} csh !*`'.format(modulecmd))
        return '; '.join(l)

    def format_environment_variable(self, key, val=None):
        """Define variable in bash syntax"""
        if val is None:
            return 'unsetenv {0};'.format(key)
        else:
            # csh barfs on long env vars
            if len(val) > CSH_LIMIT:
                if key == 'PATH':
                    logging.warning('PATH exceeds {0} characters, truncating '
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
                    logging.warning(msg.format(key, CSH_LIMIT))
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
