def colorize(string, color):
    """Apply color to a string. `string` is any string and `code` is a color
    code"""
    colors = {'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
              'blue': 34, 'magenta': 35, 'cyan': 36, 'okblue': 94}
    code = colors[color]
    return '\033[1m\033[{0}m{1}\033[0m'.format(code, string)
