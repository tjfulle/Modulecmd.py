import os
import ruamel.yaml as yaml
from six import StringIO

import pymod.names
import pymod.paths

from llnl.util.lang import Singleton
from llnl.util.tty import terminal_size
from llnl.util.tty.color import colorize
from llnl.util.tty.colify import colified


class Aliases(object):
    """Provides mechanism for having aliases to other modules"""

    def __init__(self, filename):
        self.filename = filename
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.read(self.filename)
        return self._data

    def get(self, name):
        if os.path.isdir(name):
            return self.getby_modulepath(name)
        else:
            return self.getby_name(name)

    def getby_name(self, name):
        return self.data.get(name)

    def getby_modulepath(self, dirname):
        value = []
        for (name, info) in self.data.items():
            if info["modulepath"] == dirname:
                value.append((name, info["target"]))
        return value or None

    def read(self, filename):
        if os.path.isfile(filename):  # pragma: no cover
            data = yaml.load(open(filename))
            aliases = data.pop("aliases", dict())
            if data:
                raise ValueError(
                    "Expected single top level key " "'aliases' in {0}".format(filename)
                )
            return aliases
        return dict()

    def write(self, aliases, filename):
        with open(filename, "w") as fh:
            yaml.dump({"aliases": aliases}, fh, default_flow_style=False)

    def save(self, target, name):
        """Save the alias 'name' to target"""
        self.data[name] = {
            "target": target.fullname,
            "filename": target.filename,
            "modulepath": target.modulepath,
        }
        self.write(self.data, self.filename)
        return

    def remove(self, name):
        self.data.pop(name, None)
        self.write(self.data, self.filename)

    def avail(self, terse=False):
        if not self.data:  # pragma: no cover
            return ""

        keys = sorted(list(self.data.keys()))
        fun = lambda key: "{0} -> {1} ({2})".format(
            key,
            self.data[key]["target"],
            colorize("@C{%s}" % self.data[key]["modulepath"]),
        )
        names = [fun(_) for _ in keys]

        sio = StringIO()
        if not terse:
            _, width = terminal_size()
            s = colified(names, width=width)
            sio.write("{0}\n{1}\n".format(" Aliases ".center(width, "-"), s))
        else:
            sio.write("{0}\n".format("\n".join(c for c in names)))
        string = sio.getvalue()
        return string


def factory():
    basename = pymod.names.aliases_file_basename
    filename = pymod.paths.join_user(basename)
    return Aliases(filename)


aliases = Singleton(factory)


def save(target, alias_name):
    return aliases.save(target, alias_name)


def remove(name):
    aliases.remove(name)


def get(name):
    return aliases.get(name)


def avail(terse=False):
    return aliases.avail(terse=terse)
