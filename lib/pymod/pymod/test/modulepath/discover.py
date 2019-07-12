import os
import pytest
import pymod.modulepath

def test_modulepath_discover_root(mock_modulepath):
    with pytest.raises(ValueError):
        modules = pymod.modulepath.discover.find_modules('/')
    with pytest.raises(ValueError):
        mock_modulepath('/')
    assert pymod.modulepath.discover.find_modules('fake') is None
