import os

LM_KEY = 'LOADEDMODULES'
LM_OPTS_KEY = '_LMOPTS_'
MP_KEY = 'MODULEPATH'
MH_KEY = 'MODULESHOME'
LM_FILES_KEY = '_LMFILES_'
DEFAULT_USER_COLLECTION_NAME = 'default'
DEFAULT_SYS_COLLECTION_NAME = 'system'
def LM_REFCNT_KEY(name=None):
    key = '_LMREFCNT_'
    if name is None:
        return key
    return '{0}{1}_'.format(key, name.upper())
