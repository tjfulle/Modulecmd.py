import os
import pytest

import tools


class TestCollection(tools.TestBase):
    def write_data(self):
        dirs, files = [], []
        for i in range(1, 4):
            dirs.append(tools.t_make_temp_directory(self.datadir))
            files.append(os.path.join(dirs[-1], 'f{0}.py'.format(i)))
            with open(files[-1], 'w') as fh:
                fh.write("setenv('VAR_{0}', 'VAL_{0}')\n".format(i))
                fh.write("setenv('VAR_C', 'VAL_C_{0}')\n".format(i))
        dirs.append(tools.t_make_temp_directory(self.datadir))
        i = len(dirs)
        files.append(os.path.join(dirs[-1], 'f{0}.py'.format(i)))
        with open(files[-1], 'w') as fh:
            fh.write("add_option('+x', action='store')\n")
            fh.write("opts = parse_opts()\n")
            fh.write("setenv('VAR_{0}', opts.x)\n".format(i))
            fh.write("setenv('VAR_C', 'VAL_C_{0}')\n".format(i))
        return dirs, files

    @pytest.mark.unit
    def test_collection(self):

        dirs, files = self.write_data()

        modulepath = ':'.join(dirs)
        mc = tools.t_controller(modulepath=modulepath)

        n = len(files)
        for (i, filename) in enumerate(files, start=1):
            if i != n:
                mc.loadfile(filename)
                # try to load again, should do nothing
                mc.loadfile(filename)
                key, val = 'VAR_{0}'.format(i), 'VAL_{0}'.format(i)
            else:
                name = os.path.splitext(os.path.basename(filename))[0]
                mc.load(name, options=['+x=baz'])
                key, val = 'VAR_{0}'.format(i), 'baz'
            assert mc.environ[key] == val
        assert mc.environ['VAR_C'] == 'VAL_C_{0}'.format(len(files))

        name = 'test'
        mc.save_collection(name)
        assert name in mc.collections
        mc.purge()

        for i in range(1, len(files)+1):
            key, val = 'VAR_{0}'.format(i), 'VAL_{0}'.format(i)
            assert mc.environ.get(key) is None
        assert mc.environ.get('VAR_C') is None

        mc.restore_collection(name)

        for i in range(1, len(files)+1):
            if i != n:
                key, val = 'VAR_{0}'.format(i), 'VAL_{0}'.format(i)
            else:
                key, val = 'VAR_{0}'.format(i), 'baz'
            assert mc.environ[key] == val
        assert mc.environ['VAR_C'] == 'VAL_C_{0}'.format(len(files))

        # Run a bunch of functions to get test coverage
        mc.show_available_collections()
        mc.show_available_collections(terse=True)
        mc.collections.describe()
        mc.show(name)
        mc.collections.describe(terse=True)
        mc.restore_collection('system')
        mc.restore_collection('foobar')

        mc.purge()
        os.remove(files[0])
        try:
            mc.restore_collection(name)
            assert False, 'Should have failed due to missing file'
        except:
            pass

