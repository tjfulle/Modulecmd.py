import re
from external.llnl.util.tty.color import colorize

def grep_pat_in_string(string, pat, color='c'):
    regex = re.compile(pat)
    for line in string.split('\n'):
        for item in line.split():
            if regex.search(item):
                repl = colorize('@%s{%s}' % (color, item))
                string = re.sub(re.escape(item), repl, string)
    return string
