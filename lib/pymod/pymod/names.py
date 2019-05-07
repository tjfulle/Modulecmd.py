import sys

modulepath = 'MODULEPATH'

loaded_modules = 'LOADEDMODULES'
loaded_module_files = '_LMFILES_'
loaded_module_meta = lambda key: '_LMMETA_{}'.format(key)
loaded_module_refcount = '_LMREFCNT_'
loaded_module_opts = '_LMOPTS_'

sourced_files = 'PYMOD_SOURCED_FILES'
allow_dup_entries = 'PYMOD_ALLOW_DUPLICATE_PATH_ENTRIES'

family_name = lambda key: 'MODULE_FAMILY_{}'.format(key.upper())
family_version = lambda key: 'MODULE_FAMILY_{}_VERSION'.format(key.upper())

default_user_collection = 'default'
default_sys_collection = 'system'

config_filename = 'config.yaml'
config_file_envar = 'PYMOD_CONFIG_FILE'

ld_library_path = ('DYLD_LIBRARY_PATH' if sys.platform == 'darwin'
                   else 'LD_LIBRARY_PATH')
ld_preload = 'LD_PRELOAD'
