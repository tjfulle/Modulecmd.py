import os
from configparser import ConfigParser
from io import StringIO

import modulecmd.names
import modulecmd.paths
from modulecmd.util import singleton, terminal_size, colify, colorize


class Aliases(object):
    """Provides mechanism for having aliases to other modules"""

    def __init__(self, filename):
        self.file = filename
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.read(self.file)
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
            fp = ConfigParser()
            fp.read(filename)
            if not fp.has_section("aliases"):
                return {}
            data = {}
            for (key, value) in fp.items("aliases"):
                name, attr = key.split(".", 1)
                data.setdefault(name, {})[attr] = value
            return data
        return dict()

    def write(self, aliases, filename):
        fp = ConfigParser()
        if os.path.isfile(filename):  # pragma: no cover
            fp.read(filename)
        if not fp.has_section("aliases"):
            fp.add_section("aliases")
        for (alias, item) in self.data.items():
            for (attr, value) in item.items():
                key = f"{alias}.{attr}"
                fp.set("aliases", key, value)
        with open(filename, "w") as fh:
            fp.write(fh)

    def save(self, target, name):
        """Save the alias 'name' to target"""
        self.data[name] = {
            "target": target.fullname,
            "filename": target.file,
            "modulepath": target.modulepath,
        }
        self.write(self.data, self.file)
        return

    def remove(self, name):
        self.data.pop(name, None)
        self.write(self.data, self.file)

    def avail(self, terse=False):
        if not self.data:  # pragma: no cover
            return ""

        keys = sorted(list(self.data.keys()))
        fun = lambda key: "{0} -> {1} ({2})".format(
            key,
            self.data[key]["target"],
            colorize("{cyan}%s{endc}" % self.data[key]["modulepath"]),
        )
        names = [fun(_) for _ in keys]

        sio = StringIO()
        if not terse:
            width = terminal_size().columns
            s = colify(names, width=width)
            sio.write("{0}\n{1}\n".format(" Aliases ".center(width, "-"), s))
        else:
            sio.write("{0}\n".format("\n".join(c for c in names)))
        string = sio.getvalue()
        return string


def factory():
    filename = modulecmd.config.config_file()
    return Aliases(filename)


aliases = singleton(factory)


def save(target, alias_name):
    return aliases.save(target, alias_name)


def remove(name):
    aliases.remove(name)


def get(name):
    return aliases.get(name)


def avail(terse=False):
    return aliases.avail(terse=terse)
