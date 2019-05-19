import sys

modulepath = 'MODULEPATH'

loaded_modules = 'LOADEDMODULES'
loaded_module_files = '_LMFILES_'
loaded_module_meta = lambda key: '_LMMETA_{0}'.format(key)
loaded_module_refcount = '_LMREFCNT_'
loaded_module_cellar = '_LMCELLAR_'

sourced_files = 'PYMOD_SOURCED_FILES'
allow_dup_entries = 'PYMOD_ALLOW_DUPLICATE_PATH_ENTRIES'
resolve_conflicts = 'PYMOD_RESOLVE_CONFLICTS'

family_name = lambda key: 'MODULE_FAMILY_{0}'.format(key.upper())
family_version = lambda key: 'MODULE_FAMILY_{0}_VERSION'.format(key.upper())

default_user_collection = 'default'

config_file_basename = 'config.yaml'
config_file_envar = 'PYMOD_CONFIG_FILE'

ld_library_path = ('DYLD_LIBRARY_PATH' if sys.platform == 'darwin'
                   else 'LD_LIBRARY_PATH')
ld_preload = 'LD_PRELOAD'

# Files to store collections and clones.  Paths relative to dot_dir.
collections_file_basename = 'collections.json'
clones_file_basename      = 'clones.json'
user_env_file_basename    = 'user.py'
