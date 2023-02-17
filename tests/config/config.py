import os
import modulecmd.paths
import modulecmd.config
import ruamel.yaml as yaml


def test_config_default():
    config = modulecmd.config.configuration()
    defaults = modulecmd.config.default_settings
    for (key, value) in defaults.items():
        assert config.get(key) == value
