import os
from .shell import Shell
from ..user import pymod_env_key

# --------------------------------------------------------------------------- #
# --  B  A  S  H    S  H  E  L  L-------------------------------------------- #
# --------------------------------------------------------------------------- #
class Bash(Shell):
    name = 'bash'

    @staticmethod
    def initshell(moduleshome, modulecmd, modulepath, isolate):
        modulefun = '{ eval `python -B -E %s bash "$@";`; }' % modulecmd
        mh_key = pymod_env_key('MODULESHOME', isolate=isolate)
        mp_key = pymod_env_key('MODULEPATH', isolate=isolate)
        pymod_pkg = os.path.join(moduleshome, 'lib/pymod')
        l = ['export PYMOD_DIR={0}'.format(moduleshome),
             'export PYMOD_PKG_DIR={0}'.format(pymod_pkg),
             'export {0}={1}'.format(mh_key, moduleshome),
             'export PYMOD_CMD={0}'.format(modulecmd),
             'export {0}={1}'.format(mp_key, modulepath),
             'pymod() {0}'.format(modulefun),
             'export -f pymod',
             'export __PYMOD_ISOLATED__={0}'.format(Bash.onoff(isolate))]
        if not isolate:
            l.extend(['unset -f module',
                      'module() {0}'.format(modulefun),
                      'export -f module',
                      ])
        return '; '.join(l)

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

    def filter_environ(self, environ):
        env = {}
        skip = []
        for (key, val) in environ.items():
            if key.startswith('BASH_FUNC'):
                continue
            if key in skip:
                continue
            env[key] = val
        return env

