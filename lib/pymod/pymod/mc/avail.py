import pymod.modulepath
import pymod.collection


def avail(terse=False, regex=None, show_all=False):
    avail = pymod.modulepath.avail(terse=terse, regex=regex)
    if show_all:
        avail += pymod.collection.avail(
            terse=terse, regex=regex)
        avail += pymod.clone.avail(terse=terse)
    return avail
