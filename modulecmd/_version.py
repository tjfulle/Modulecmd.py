from .util import split, safe_int


class version:
    def __init__(self, version_string: str = None) -> None:
        major = minor = micro = patch = None
        if version_string is not None:
            version_string, *remainder = split(version_string, "-", 1)
            if remainder:
                patch = remainder[0]
            parts = split(version_string, ".", transform=safe_int)
            major = parts[0]
            if len(parts) > 1:
                minor = parts[1]
            if len(parts) > 2:
                micro = parts[2]
        self.version_info = (major, minor, micro, patch)

    def __str__(self):
        string = ""
        string = ".".join([str(_) for _ in self.version_info[:-1] if _ is not None])
        if self.version_info[-1] is not None:
            string += f"-{self.version_info[-1]}"
        return string

    def __eq__(self, other):
        if not isinstance(other, version):
            raise ValueError(f"Cannot compare version with {type(other).__name__}")
        return self.version_info == other.version_info

    def __lt__(self, other):
        return not self > other

    def __gt__(self, other):
        if not isinstance(other, version):
            raise ValueError(f"Cannot compare version with {type(other).__name__}")
        for (i, my_val) in enumerate(self.version_info):
            other_val = other.version_info[i]
            if my_val == other_val:
                continue
            if my_val is None:
                return False
            elif other_val is None:
                return True
            elif type(my_val) == type(other_val) and my_val > other_val:
                return True
            elif str(my_val) > str(other_val):
                return True
        return False

    @property
    def major(self):
        return self.version_info[0]

    @property
    def minor(self):
        return self.version_info[1]

    @property
    def micro(self):
        return self.version_info[2]

    @property
    def patch(self):
        return self.version_info[3]

    @property
    def string(self):
        return str(self)
