from .config import cfg
def colorize(string, color, bold=False):
    """Apply color to a string. `string` is any string and `code` is a color
    code"""
    if cfg.color == 'never':
        return string

    colors = {'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
              'blue': 34, 'magenta': 35, 'cyan': 36, 'okblue': 94}
    code = colors[color]
    #return '\033[1m\033[{0}m{1}\033[0m'.format(code, string)
    colored_string = '\033[{0}m{1}\033[0m'.format(code, string)
    if bold:
        colored_string = '\033[1m' + colored_string
    return colored_string
