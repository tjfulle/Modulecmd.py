from modulecmd.util import split


class Version:
    """Class to represent a module's version

    Assumes module version is of form

    [major[.minor[.patch[-variant]]]]

    """

    def __init__(self, version_string=None):
        self.tuple = tuple()
        self.string = version_string or ""
        if version_string is not None:
            try:
                version_string, variant = version_string.split("-")
            except ValueError:
                variant = None
            parts = [try_int(part) for part in split(version_string, ".")]
            if variant is not None:
                parts.append(try_int(variant))
            self.tuple = tuple(parts)
        for (i, attr) in enumerate(("major", "minor", "patch", "variant")):
            try:
                value = self.tuple[i]
            except IndexError:
                value = None
            setattr(self, attr, value)

    def __repr__(self):
        return self.string

    def __str__(self):  # pragma: no cover
        return self.string

    def __gt__(self, other):
        try:
            return self.tuple > other.tuple
        except TypeError:
            return self.string > other.string

    def __lt__(self, other):
        return not self > other

    def __eq__(self, other):
        if not isinstance(other, Version):
            other = Version(other)
        return self.tuple == other.tuple

    def __nonzero__(self):
        return self.major is not None

    def __bool__(self):
        return self.major is not None

    @property
    def info(self):
        return self.tuple


def try_int(item):
    try:
        return int(item)
    except:  # noqa: E722
        return item
