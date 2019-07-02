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
        self.data = self.read(filename)
        self.filename = filename

    def get(self, name):
        return self.data.get(name)

    def read(self, filename):
        if os.path.isfile(filename):  # pragma: no cover
            data = yaml.load(open(filename))
            aliases = data.pop('aliases', dict())
            if data:
                raise ValueError("Expected single top level key "
                                 "'aliases' in {0}".format(filename))
            return aliases
        return dict()

    def write(self, aliases, filename):
        with open(filename, 'w') as fh:
            yaml.dump({'aliases': aliases}, fh, default_flow_style=False)

    def save(self, target, name):
        """Save the alias 'name' to target"""
        self.data[name] = {
            'target': target.fullname,
            'filename': target.filename,
            'modulepath': target.modulepath,
            }
        self.write(self.data, self.filename)
        return

    def remove(self, name):
        self.data.pop(name, None)
        self.write(self.data, self.filename)

    def avail(self, terse=False):
        if not self.data:  # pragma: no cover
            return ''

        keys = sorted(list(self.data.keys()))
        fun = lambda key: '{0} -> {1} ({2})'.format(
            key,
            self.data[key]['target'],
            colorize('@C{%s}'%self.data[key]['modulepath']))
        names = [fun(_) for _ in keys]

        sio = StringIO()
        if not terse:
            _, width = terminal_size()
            s = colified(names, width=width)
            sio.write('{0}\n{1}\n'
                      .format(' Aliases '.center(width, '-'), s))
        else:
            sio.write('\n'.join(c for c in names))
        string = sio.getvalue()
        return string


def _aliases():
    basename = pymod.names.aliases_file_basename
    for dirname in (pymod.paths.user_config_platform_path,
                    pymod.paths.user_config_path):
        filename = os.path.join(dirname, basename)
        if os.path.exists(filename):  # pragma: no cover
            break
    else:
        filename = os.path.join(
            pymod.paths.user_config_platform_path,
            basename)

    # it is okay that we may not have found a config file, if it doesn't
    # exist, Aliases will create it
    return Aliases(filename)

aliases = Singleton(_aliases)


def save(target, alias_name):
    return aliases.save(target, alias_name)


def remove(name):
    aliases.remove(name)


def get(name):
    return aliases.get(name)


def avail(terse=False):
    return aliases.avail(terse=terse)
