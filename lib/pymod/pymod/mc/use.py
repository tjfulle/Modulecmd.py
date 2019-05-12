import os
import pymod.mc
import pymod.modulepath


def use(dirname, append=False, delete=False):
    """Add dirname to MODULEPATH"""
    dirname = os.path.expanduser(dirname)
    if delete:
        pymod.mc.unuse(dirname)
        return
    elif append:
        pymod.modulepath.append_path(dirname)
    else:
        _, lost_precedence = pymod.modulepath.prepend_path(dirname)
        for m1 in lost_precedence:
            if not m1.is_loaded:
                continue
            for attr in ('fullname', 'name'):
                m2 = pymod.modulepath.get(getattr(m1, attr))
                if m2 is not None:
                    break
            else:
                continue
            if m1.filename != m2.filename:
                # Filenames not same -> m2 has higher precedence, swap
                pymod.mc.swap_impl(m1, m2)
                pymod.mc.swapped_on_mp_change(m1, m2)
