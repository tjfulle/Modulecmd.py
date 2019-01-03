import os
import pytest

import tools

from pymod.modulepath import Modulepath

def mark_loaded_modules(lmf):
    def inner(module):
        if module.filename in lmf:
            module.is_loaded = True
    return inner

class TestModulepath(tools.TestBase):

    @pytest.mark.unit
    def test_modulepath(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        f1 = tools.t_touch(os.path.join(d1, 'f1.py'))
        a1 = tools.t_touch(os.path.join(d1, 'a/1.0.py'))
        a2 = tools.t_touch(os.path.join(d1, 'a/2.0.py'))
        b1 = tools.t_touch(os.path.join(d1, 'b/1.0.py'))
        b2 = tools.t_touch(os.path.join(d1, 'b/2.0.py'))
        tools.t_symlink(b1, 'default', wipe_first=True)
        mp = Modulepath([d1])

        assert mp.get_module_by_name('f1').name == 'f1'
        assert mp.get_module_by_name('a').fullname == 'a/2.0'
        assert mp.get_module_by_name('b').fullname == 'b/1.0'
        m = mp.get_module_by_name('b').fullname == 'b/1.0'

        d2 = tools.t_make_temp_directory(self.datadir)
        tools.t_touch(os.path.join(d2, 'f1.py'))
        tools.t_touch(os.path.join(d2, 'a/1.0.py'))
        tools.t_touch(os.path.join(d2, 'a/2.0.py'))
        tools.t_touch(os.path.join(d2, 'b/1.0.py'))
        mp.append(d2)

        m = mp.get_module_by_name('a')
        print(d1)
        print(d2)
        print(m.filename)
        assert m.filename == os.path.realpath(os.path.join(d1, 'a/2.0.py'))
        m = mp.get_module_by_name('{0}/a/2.0'.format(os.path.basename(d2)))
        assert m.filename == os.path.realpath(os.path.join(d2, 'a/2.0.py'))

    @pytest.mark.unit
    def test_modulepath_through_controller(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        tools.t_touch(os.path.join(d1, 'f1.py'))
        tools.t_touch(os.path.join(d1, 'a/1.0.py'))
        tools.t_touch(os.path.join(d1, 'a/2.0.py'))
        b1 = tools.t_touch(os.path.join(d1, 'b/1.0.py'))
        tools.t_touch(os.path.join(d1, 'b/2.0.py'))
        tools.t_symlink(b1, 'default', wipe_first=True)
        mc = tools.t_controller(modulepath=d1)
        mp = mc.modulepath
        assert mp.get_module_by_name('f1').name == 'f1'
        assert mp.get_module_by_name('a').fullname == 'a/2.0'
        assert mp.get_module_by_name('b').fullname == 'b/1.0'

    def test_modulepath_default(self):
        """Test for default module availability"""

        sep = os.pathsep
        modulepath = []

        # Default should be highest version in directory -> version 3
        d1 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d1)
        for v in ('1.0', '2.0', '3.0'):
            tools.t_touch(os.path.join(d1, 'a/{0}.py'.format(v)))
        mp = Modulepath(modulepath)

        # Default should now be highest version across directories -> version 4
        d2 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d2)
        tools.t_touch(os.path.join(d2, 'a/4.0.py'))
        mp.append(d2)
        m = mp.get_module_by_name('a')
        assert m.version == '4.0', m.version


    def test_modulepath_linked_default(self):
        """Test for linked default module availability"""

        sep = os.pathsep
        modulepath = []

        # Default should be version linked to file 'default', regardless of version
        d1 = tools.t_make_temp_directory(self.datadir)
        for v in ('3.0', '2.0', '1.0'):
            f = tools.t_touch(os.path.join(d1, 'a/{0}.py'.format(v)))
        tools.t_symlink(f, 'default', wipe_first=True)
        modulepath.append(d1)
        mp = Modulepath(modulepath)
        m = mp.get_module_by_name('a')
        assert m.filename == os.path.realpath(f), m.filename
        assert m.is_default

        # Even after adding higher version, the default shouldn't change
        d2 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d2)
        tools.t_touch(os.path.join(d2, 'a/4.0.py'))
        mp.append(d2)
        m = mp.get_module_by_name('a')
        assert m.filename == os.path.realpath(f), m.filename
        assert m.is_default

    def test_modulepath_get(self):
        """Test for linked default module availability"""

        sep = os.pathsep
        modulepath = []

        # Default should be version linked to file 'default', regardless of version
        d1 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d1)

        f1 = os.path.join(d1, 'a/1.0.py')
        tools.t_touch(f1)
        tools.t_symlink(f1, 'default')
        f2 = os.path.join(d1, 'a/2.0.py')
        tools.t_touch(f2)
        f3 = os.path.join(d1, 'a/3.0.py')
        tools.t_touch(f3)

        mp = Modulepath(modulepath)

        m = mp.get_module_by_name('a')
        assert m.filename == os.path.realpath(f1), m.filename

        # More qualified name should work
        m = mp.get_module_by_name('a/2.0')
        assert m.version == '2.0', m.version
        assert m.filename == os.path.realpath(f2), m.filename

        # Version 2.0 is a duplicate, a more qualified path will get it
        d2 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d2)
        f2_2 = tools.t_touch(os.path.join(d2, 'a/2.0.py'))

        mp.append(d2)

        # Should get first file with version 2.0
        m = mp.get_module_by_name('a/2.0')
        assert m.version == '2.0', m.version
        assert m.filename == os.path.realpath(f2), m.filename

        # More qualified name should work
        d = os.path.basename(os.path.realpath(d2))
        m = mp.get_module_by_name(d+'/a/2.0')
        assert m is not None, d
        assert m.filename == os.path.realpath(f2_2), m.filename

    def test_modulepath_module_loaded(self):
        sep = os.pathsep
        modulepath = []

        d1 = tools.t_make_temp_directory(self.datadir)
        lm, lmf = [], []
        for v in ('3.0', '2.0', '1.0'):
            lm.append('a/{0}'.format(v))
            lmf.append(tools.t_touch(os.path.join(d1, lm[-1]+'.py')))
        modulepath.append(d1)

        mp = Modulepath(modulepath)
        mp.apply(mark_loaded_modules(lmf))

        m = mp.get_module_by_name('a/1.0')
        assert m.is_loaded
        m = mp.get_module_by_name('a/2.0')
        assert m.is_loaded
        m = mp.get_module_by_name('a/3.0')
        assert m.is_loaded

    def test_modulepath_describe(self):
        """Tests mp.describe, but only tests it doesn't fail"""
        sep = os.pathsep
        modulepath = []

        d1 = tools.t_make_temp_directory(self.datadir)
        modulepath.append(d1)
        lm, lmf = [], []
        for v in ('1.0', '2.0', '3.0'):
            lm.append('a/{0}'.format(v))
            lmf.append(tools.t_touch(os.path.join(d1, lm[-1]+'.py')))

        # Default should be version linked to file 'default', regardless of version
        mp = Modulepath(modulepath)
        mp.apply(mark_loaded_modules(lmf))
        s = mp.describe()
        s = mp.describe(terse=True)
        s = mp.describe(regex='a')
