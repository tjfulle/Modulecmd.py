import pymod.alias
import pymod.modulepath
import pymod.collection


def avail(terse=False, regex=None, show_all=False, long_format=False):
    avail = pymod.modulepath.avail(terse=terse, regex=regex, long_format=long_format)
    if show_all:
        avail += pymod.collection.avail(terse=terse, regex=regex)
        avail += pymod.clone.avail(terse=terse)
    return avail
