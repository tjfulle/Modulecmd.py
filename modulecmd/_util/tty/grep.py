import re
from modulecmd.util import colorize


def grep_pat_in_string(string, pat, color="cyan"):
    regex = re.compile(pat)
    for line in string.split("\n"):
        for item in line.split():
            if regex.search(item):
                repl = colorize("{%s}%s{endc}" % (color, item))
                string = re.sub(re.escape(item), repl, string)
    return string
