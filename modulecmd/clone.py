import os
import json
from io import StringIO

import modulecmd.names
import modulecmd.paths
import modulecmd.environ
from modulecmd.util import singleton, terminal_size, colify


class Clones(object):
    def __init__(self, filename):
        self.filename = filename
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.read(self.filename)
        return self._data

    def get(self, name):
        return self.data.get(name)

    def read(self, filename):
        if os.path.isfile(filename):
            return dict(json.load(open(filename)))
        return dict()

    def write(self, clones, filename):
        with open(filename, "w") as fh:
            json.dump(clones, fh, indent=2)

    def save(self, name):
        """Clone current environment"""
        env = modulecmd.environ.copy(include_os=True)
        self.data[name] = env
        self.write(self.data, self.filename)
        return env

    def remove(self, name):
        self.data.pop(name, None)
        self.write(self.data, self.filename)


def factory():
    basename = modulecmd.names.clones_file_basename
    filename = modulecmd.paths.join_user(basename, cache=True)
    return Clones(filename)


clones = singleton(factory)


def save(name):
    return clones.save(name)


def remove(name):
    clones.remove(name)


def avail(terse=False):
    return clones.avail(terse)


def get(name):
    return clones.get(name)


def items():
    for item in clones.data.items():
        yield item
