import os
import sys
import tools
from pymod.module2 import Module2, read_metadata
from pymod.config import cfg

class TestModule2(tools.TestBase):
    def test_module2_1(self):
        modulepath = tools.t_make_temp_directory(self.datadir)
        filename = os.path.join(modulepath, 'a.py')
        with open(filename, 'w') as fh:
            fh.write("setenv('spam', 'baz')")
        module = Module2('a', 'a', None, 'PY', filename, modulepath, False)
        assert not module.is_loaded

    def test_module2_2(self):
        # Check that warning is fired for non-symlink default
        modulepath = tools.t_make_temp_directory(self.datadir)
        filename = os.path.join(modulepath, 'a.py')
        cfg.verbosity = 5
        with open(filename, 'w') as fh:
            fh.write("setenv('spam', 'baz')")
        with open(os.path.join(modulepath, 'default'), 'w') as fh:
            fh.write('')
        module = Module2('a', 'a', None, 'PY', filename, modulepath, False)
        assert not module.is_loaded

    def test_module2_read_metadata(self):
        # Check metadata
        modulepath = tools.t_make_temp_directory(self.datadir)
        filename = os.path.join(modulepath, 'a.py')
        cfg.verbosity = 5
        with open(filename, 'w') as fh:
            fh.write("#pymod: enable_if=True, foo=str('baz'), "
                     "do_not_register=False, \nsetenv('spam', 'baz')")
        metadata = read_metadata(filename)
        assert metadata == {'enable_if': True, 'foo': 'baz',
                            'do_not_register': False}

    def test_module2_read_metadata_2(self):
        # Check metadata
        modulepath = tools.t_make_temp_directory(self.datadir)
        filename = os.path.join(modulepath, 'a.py')
        cfg.verbosity = 5
        with open(filename, 'w') as fh:
            # enable_if must be a bool
            fh.write("#pymod: enable_if='Foo'")
        try:
            metadata = read_metadata(filename)
            assert False
        except:
            pass
