import os
import json
from ordereddict_backport import OrderedDict

import modulecmd.modulepath
import modulecmd.names
import modulecmd.paths
import modulecmd.environ

import llnl.util.tty as tty


def upgrade(new, old, old_version):  # pragma: no cover
    if old_version is None:
        return upgrade_None_to_1_0(new, old)
    elif old_version != new.version:
        raise ValueError(
            "No known conversion from Collections version "
            "{0} to {1}".format(old_version, new.version)
        )


def upgrade_None_to_1_0(new, old, depth=[0]):

    depth[0] += 1
    if depth[0] > 1:
        raise ValueError("Recursion!")

    version_string = ".".join(str(_) for _ in new.version)
    tty.info(
        "Converting Modulecmd.py collections version 0.0 to "
        "version {0}".format(version_string)
    )
    new_collections = {}
    for (name, old_collection) in old.items():
        new_collection = OrderedDict()
        mp = modulecmd.modulepath.Modulepath([])
        for (path, m_descs) in old_collection:
            if new_collection is None:
                break
            if not os.path.isdir(path):
                tty.warn(
                    "Collection {0} contains directory {1} which "
                    "does not exist!  This collection will be skipped".format(
                        name, path
                    )
                )
                new_collection = None
                break
            avail = mp.append_path(path)
            if avail is None:
                tty.warn(
                    "Collection {0} contains directory {1} which "
                    "does not have any available modules!  "
                    "This collection will be skipped".format(name, path)
                )
                new_collection = None
                break
            for (fullname, filename, opts) in m_descs:
                m = mp.get(filename)
                if m is None:
                    tty.warn(
                        "Collection {0} requests module {1} which "
                        "can not be found! This collection will be skipped".format(
                            name, fullname
                        )
                    )
                    new_collection = None
                    break
                m.opts = opts
                m.acquired_as = m.fullname
                ar = m.asdict()
                new_collection.setdefault(m.modulepath, []).append(ar)

        if new_collection is None:
            tty.warn(
                "Skipping collection {0} because of previous " "errors".format(name)
            )
            continue

        new_collections[name] = list(new_collection.items())

    bak = new.filename + ".bak"
    with open(bak, "w") as fh:
        json.dump(old, fh, indent=2)

    new.write(list(new_collections.items()), new.filename)
    return new_collections
