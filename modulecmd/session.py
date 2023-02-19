import os
import glob
import json
import time
import atexit
import random

import modulecmd.paths
import modulecmd.names
from modulecmd.util import singleton


class Session:
    def __init__(self):
        id = random.randint(10000, 99999)
        self.id = id
        self.savedir = os.path.join(modulecmd.paths.user_cache_path, "sessions")
        if not os.path.isdir(self.savedir):
            os.makedirs(self.savedir)
        self.file = os.path.join(self.savedir, "{0}.json".format(self.id))
        self.data = self.load()

    def load(self):
        if not os.path.isfile(self.file):
            return {}
        with open(self.file) as fh:
            return json.load(fh)

    def dump(self):
        with open(self.file, "w") as fh:
            json.dump(self.data, fh, indent=4)

    def save(self, **kwds):
        for (key, val) in kwds.items():
            self.data[key] = val

    def get(self, key):
        return self.data.get(key)

    def remove(self, key):
        self.data.pop(key, None)


def clean():
    # Remove session files more than 7 days old
    now = time.time()
    # dirname = session.savedir
    for filename in glob.glob(os.path.join(session.savedir, "*.json")):
        modified_time = os.stat(filename).st_mtime
        if modified_time < now - 7 * 24 * 60 * 60:
            os.remove(filename)


session = singleton(Session)


def save(**kwds):
    return session.save(**kwds)


def get(key):
    return session.get(key)


def load():
    return session.data


def dump():
    session.dump()


def id():
    return session.id()


def remove(key):
    session.remove(key)


atexit.register(dump)
