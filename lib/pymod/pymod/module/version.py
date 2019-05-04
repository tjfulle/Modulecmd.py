import re


class Version:
    """Class to represent a module's version

    Assumes module version is of form

    [major[.minor[.patch[-micro]]]]

    """
    def __init__(self, version_string=None):
        self.string = version_string
        self.major = self.minor = self.patch = self.micro = None
        if self.string is not None:
            try:
                version_string, self.micro = self.string.split('-')
            except:
                pass
            attrs = ('major', 'minor', 'patch', 'micro')
            for (i, part) in enumerate(version_string.split('.')):
                if not part.split():
                    continue
                setattr(self, attrs[i], try_int(part))

    def __gt__(self, other):
        if self.string is None:
            return False
        if other.string is None:
            return True
        if self.major > other.major:
            return True
        if self.minor > other.minor:
            return True
        if self.patch > other.patch:
            return True
        if self.micro > other.micro:
            return True
        return False

    def __lt__(self, other):
        return not self > other

    def __eq__(self, other):
        return self.string == other.string


def try_int(item):
    try:
        return int(item)
    except:
        return item
