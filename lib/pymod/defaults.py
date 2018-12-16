import os

from .user import user_env, _dot_dir


def collections_filename():
    default = os.path.join(dot_dir(), 'collections.json')
    try:
        filename = user_env.collections_filename() or default
    except (TypeError, AttributeError):
        filename = default
    old_filename = os.path.join(dot_dir(), 'module.collections')
    if os.path.isfile(old_filename):
        assert not os.path.isfile(filename)
        os.rename(old_filename, filename)
    return filename


def clones_filename():
    default = os.path.join(dot_dir(), 'clones.json')
    try:
        filename = user_env.clones_filename() or default
    except (TypeError, AttributeError):
        filename = default
    return filename


dot_dir = _dot_dir
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
