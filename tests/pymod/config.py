import os
import pytest
import modulecmd.names
import modulecmd.paths

import modulecmd.config


@pytest.fixture()
def mock_test_config():
    os.environ.pop("MODULECMD_CONFIG_PATH", None)
    cfg = modulecmd.config.configuration()
    return cfg


def test_config_default(mock_test_config):
    cfg = mock_test_config
    assert cfg.get("debug") == False
    assert cfg.get("verbose") == False
    assert cfg.get("default_shell") == "bash"
    assert cfg.get("warn_all") == True
    assert cfg.get("stop_on_error") == True
    assert cfg.get("resolve_conflicts") == False
    assert cfg.get("editor") == "vi"
    assert cfg.get("load_after_purge") == []
    assert cfg.get("skip_add_devpack") == False
    assert cfg.get("color") == "auto"
