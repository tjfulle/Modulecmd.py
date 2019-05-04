import re


class Version:
    """Class to represent a module's version

    Assumes module version is of form

    [major[.minor[.patch[-micro]]]]

    """
    def __init__(self, version_string=None):
        self.tuple = tuple()
        self.string = version_string
        if self.string is None:
            self.major = self.minor = self.patch = self.micro = None
        else:
            try:
                version_string, micro = self.string.split('-')
            except ValueError:
                micro = None
            version_tuple = []
            for part in version_string.split('.'):
                if not part.split():
                    continue
                version_tuple.append(try_int(part))
            if micro is not None:
                version_tuple.append(try_int(micro))
            self.tuple = tuple(version_tuple)
            for (i, attr) in enumerate(('major', 'minor', 'patch', 'micro')):
                try:
                    value = self.tuple[i]
                except IndexError:
                    value = None
                setattr(self, attr, value)

    def __repr__(self):
        return self.string

    def __gt__(self, other):
        return self.tuple > other.tuple

    def __lt__(self, other):
        return not self > other

    def __eq__(self, other):
        return self.tuple == other.tuple


def try_int(item):
    try:
        return int(item)
    except:
        return item
