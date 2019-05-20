import pymod.modulepath
import pymod.collection


def avail(terse=False, fulloutput=False, regex=None):
    avail = pymod.modulepath.format_available(
        terse=terse, regex=regex, fulloutput=fulloutput)
    avail += pymod.collection.format_available(
        terse=terse, regex=regex)
    return avail
