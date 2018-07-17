import os

import tools

class TestUserEnv(tools.TestBase):

    def test_load_user_env_no_exist(self):
        import pymod.user
        m = pymod.user.user_env
        assert m.empty()

    def test_load_user_env_exist(self):
        import pymod.user
        filename = os.path.join(self.dotdir, 'module.env')
        with open(filename, 'w') as fh:
            fh.write('spam = "baz"\n')
            fh.write('foo = 2\n')
        m = pymod.user.user_env
        assert m.empty()
        m.load(self.dotdir)
        assert hasattr(m, 'spam') and m.spam == 'baz'
        assert hasattr(m, 'foo') and m.foo == 2
        os.remove(filename)
