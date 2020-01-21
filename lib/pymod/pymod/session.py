import os
import sys
import json
import atexit
from llnl.util.lang import Singleton
from contrib.util import get_processes

import pymod.paths
import pymod.names


class Session:
    def __init__(self):
        self.savedir = os.path.join(pymod.paths.user_config_path, "sessions")
        if not os.path.isdir(self.savedir):
            os.makedirs(self.savedir)
        pid = Session.pid()
        self.filename = os.path.join(self.savedir, "{0}.json".format(pid))
        self.data = self.load()

    @staticmethod
    def pid():
        if pymod.names.session_id in os.environ:
            return os.environ[pymod.names.session_id]
        pid = os.getpid()
        procs = get_processes()
        while pid in procs:
            proc = procs[pid]
            pid = proc["ppid"]
        return proc["pid"]

    def load(self):
        if not os.path.isfile(self.filename):
            return {}
        with open(self.filename) as fh:
            return json.load(fh)

    def dump(self):
        with open(self.filename, "w") as fh:
            json.dump(self.data, fh, indent=4)

    def save(self, **kwds):
        for (key, val) in kwds.items():
            self.data[key] = val

    def get(self, key):
        return self.data.get(key)

    def remove(self, key):
        self.data.pop(key, None)


def clean():
    shell = os.path.basename(os.getenv("SHELL", "bash"))
    procs = get_processes()
    shell_procs = sorted(
        [pid for (pid, proc) in procs.items() if proc["name"].endswith(shell)]
    )
    dirname = session.savedir
    for filename in os.listdir(dirname):
        fpid = int(os.path.splitext(filename)[0])
        if fpid not in shell_procs:
            os.remove(os.path.join(dirname, filename))


session = Singleton(Session)


def save(**kwds):
    return session.save(**kwds)


def get(key):
    return session.get(key)


def load():
    return session.data


def dump():
    session.dump()


def pid():
    return session.pid()


def remove(key):
    session.remove(key)


atexit.register(dump)
