import pymod.alias
import pymod.modulepath
import pymod.collection


def avail(terse=False, regex=None, show_all=False):
    avail = pymod.modulepath.avail(terse=terse, regex=regex)
    avail += pymod.alias.avail(terse=terse)
    if show_all:
        avail += pymod.collection.avail(
            terse=terse, regex=regex)
        avail += pymod.clone.avail(terse=terse)
    return avail
