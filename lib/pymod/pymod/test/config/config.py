import os
import pymod.paths
import pymod.config
import ruamel.yaml as yaml

def test_config_default():
    config = pymod.config.factory()
    basename = pymod.names.config_file_basename
    default_config_file = os.path.join(pymod.paths.etc_path, 'defaults', basename)
    defaults = pymod.config.load_config(default_config_file)
    for (key, value) in defaults.items():
        assert config.get(key, scope='defaults') == value


def test_confing_user():
    basename = pymod.names.config_file_basename
    user_config_file = os.path.join(pymod.paths.user_config_platform_path, basename)
    user_config = """\
config:
  debug: true
  verbose: true
  warn_all: false
  stop_on_error: false
  resolve_conflicts: true
  allow_duplicate_path_entries: true"""
    with open(user_config_file, 'w') as fh:
        fh.write(user_config)
    user_config_dict = yaml.load(user_config)
    config = pymod.config.factory()

    for (key, value) in user_config_dict['config'].items():
        config_value = config.get(key)  # user has higher priority
        user_config_value = config.get(key, scope='user')
        assert config_value == user_config_value == value

        # The user values were made the opposite the default values
        defaults_config_value = config.get(key, scope='defaults')
        assert config_value == (not defaults_config_value)


def test_confing_admin():
    basename = pymod.names.config_file_basename
    admin_config_file = os.path.join(pymod.paths.etc_path, basename)
    admin_config = """\
config:
  debug: true
  verbose: true
  warn_all: false
  stop_on_error: false
  resolve_conflicts: true
  allow_duplicate_path_entries: true"""
    with open(admin_config_file, 'w') as fh:
        fh.write(admin_config)
    admin_config_dict = yaml.load(admin_config)
    config = pymod.config.factory()

    for (key, value) in admin_config_dict['config'].items():
        config_value = config.get(key)  # user has higher priority
        admin_config_value = config.get(key, scope='user')
        assert config_value == admin_config_value == value

        # The user values were made the opposite the default values
        defaults_config_value = config.get(key, scope='defaults')
        assert config_value == (not defaults_config_value)
    os.remove(admin_config_file)

def test_confing_env():
    config_dict = {
            'editor': 'env_vi',
            'load_after_purge': ['env_a', 'env_b'],
            'serialize_chunk_size': 400
        }
    for (key, value) in config_dict.items():
        if isinstance(value, list):
            value = ','.join(value)
        os.environ['PYMOD_{0}'.format(key.upper())] = str(value)

    # defaults
    config = pymod.config.factory()
    basename = pymod.names.config_file_basename
    default_config_file = os.path.join(pymod.paths.etc_path, 'defaults', basename)
    defaults = pymod.config.load_config(default_config_file)

    for key in config_dict:
        defaults_config_value = config.get(key, scope='defaults')
        env_config_value = config.get(key, scope='environment')
        config_value = config.get(key)
        assert config_value == env_config_value == config_dict[key]
        assert defaults_config_value == defaults[key]
        os.environ.pop('PYMOD_{0}'.format(key.upper()))


def test_confing_scopes():
    config_dict = {
        'command_line': {
            'editor': 'cli_vi',
            'load_after_purge': ['cli_a', 'cli_b'],
            'serialize_chunk_size': 300
        },
        'environment': {
            'editor': 'env_vi',
            'load_after_purge': ['env_a', 'env_b'],
            'serialize_chunk_size': 400
        },
        'user': {
            'editor': 'user_vi',
            'load_after_purge': ['user_a', 'user_b'],
            'serialize_chunk_size': 500
        }
    }

    # Write the user config
    basename = pymod.names.config_file_basename
    user_config_file = os.path.join(pymod.paths.user_config_platform_path, basename)
    user_config = """\
config:
  editor: {editor}
  load_after_purge: {load_after_purge}
  serialize_chunk_size: {serialize_chunk_size}""".format(**config_dict['user'])
    with open(user_config_file, 'w') as fh:
        fh.write(user_config)

    # Environment variables
    for (key, value) in config_dict['environment'].items():
        if isinstance(value, list):
            value = ','.join(value)
            print(value)
        os.environ['PYMOD_{0}'.format(key.upper())] = str(value)

    user_config_dict = yaml.load(user_config)
    config = pymod.config.factory()

    # Command line
    for (key, value) in config_dict['command_line'].items():
        config.set(key, value, scope='command_line')

    # defaults
    default_config_file = os.path.join(pymod.paths.etc_path, 'defaults', basename)
    defaults = pymod.config.load_config(default_config_file)

    for key in config_dict['user']:
        user_config_value = config.get(key, scope='user')
        defaults_config_value = config.get(key, scope='defaults')
        env_config_value = config.get(key, scope='environment')
        cli_config_value = config.get(key, scope='command_line')
        config_value = config.get(key)

        assert config_value == cli_config_value == config_dict['command_line'][key]
        assert defaults_config_value == defaults[key]
        assert user_config_value == config_dict['user'][key]
        assert env_config_value == config_dict['environment'][key]

        os.environ.pop('PYMOD_{0}'.format(key.upper()))

