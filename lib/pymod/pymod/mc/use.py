import os
import pymod.mc
import pymod.modulepath


def use(dirname, append=False, delete=False):
    """Add dirname to MODULEPATH"""
    if delete:
        pymod.mc.unuse(dirname)
        return
    if dirname.startswith('~'):
        dirname = os.path.expanduser(dirname)
    if append:
        pymod.modulepath.append_path(dirname)
    else:
        _, bumped = pymod.modulepath.prepend_path(dirname)
        for m1 in bumped:
            if not m1.is_loaded:
                continue
            m2 = pymod.modulepath.get(m1.name)
            if m1.filename != m2.filename:
                assert m1.is_loaded
                pymod.mc.swap_impl(m1, m2)
                pymod.mc.register_swa
                on_mp_changed = self.m_state_changed.setdefault('MP', {})
                on_mp_changed.setdefault('Up', []).append((m1, m2))