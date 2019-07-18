import sys

modulepath = 'MODULEPATH'

loaded_modules = 'LOADEDMODULES'
loaded_module_files = '_LMFILES_'
initial_env = '_LMX0_'
loaded_module_cellar = '_LMX1_'
loaded_module_meta = lambda key: '_LMX2_{0}'.format(key)
serialized_key = lambda key, i: '{0}_{1}'.format(key, i)

tutorial_save_env = '_LMT0_'
tutorial_root_path = 'PYMOD_TUTORIAL_ROOT_PATH'

sourced_files = 'PYMOD_SOURCED_FILES'

family_name = lambda key: 'MODULE_FAMILY_{0}'.format(key.upper())
family_version = lambda key: 'MODULE_FAMILY_{0}_VERSION'.format(key.upper())

default_user_collection = 'default'

config_file_basename = 'config.yaml'

ld_preload = 'LD_PRELOAD'
ld_library_path = 'LD_LIBRARY_PATH'
platform_ld_library_path = ('DYLD_LIBRARY_PATH' if sys.platform == 'darwin'
                            else 'LD_LIBRARY_PATH')

# Files to store collections and clones.  Paths relative to dot_dir.
aliases_file_basename = 'aliases.yaml'
collections_file_basename = 'collections.json'
clones_file_basename      = 'clones.json'
user_env_file_basename    = 'user.py'
cache_file_basename       = 'cache.json'
