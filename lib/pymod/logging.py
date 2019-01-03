import sys

from .cfg import cfg
from .color import colorize

# --------------------------------------------------------------------------- #
# ---------------------------------- CONSOLE I/O ---------------------------- #
# --------------------------------------------------------------------------- #
def write_to_console(arg, minverbosity=1, end='\n'):
    """Write directly to the console if `minverbosity` is greater than the
    current global verbosity state"""
    if cfg.verbosity < minverbosity:
        return
    sys.stderr.write('{0}{1}'.format(arg, end))
    sys.stderr.flush()


class logging(object):  # pragma: no cover
    """General logging class"""
    @staticmethod
    def debug(*args, **kwargs):
        """Write to console if `cfg.verbosity` is >= 2"""
        if not cfg.debug:
            return
        string = colorize('Debug:', 'okblue')
        string += ' {0}'.format(join_args(*args))
        end = kwargs.get('end', '\n')
        write_to_console(string, cfg.verbosity)

    @staticmethod
    def info(arg, filename=None, end='\n'):
        """Write a message to console"""
        write_to_console('{0}'.format(arg), 1, end=end)

    @staticmethod
    def warning(arg, filename=None, end='\n', minverbosity=1):
        """Write a warning to console"""
        if not cfg.warn_all:
            return
        string = colorize('Warning:', 'magenta')
        string += ' {0}'.format(arg)
        if filename is not None:
            string += '\n   [Reported from {0!r}]'.format(filename)
        write_to_console(string, minverbosity=minverbosity, end=end)

    @staticmethod
    def error(arg, filename=None, end='\n', noraise=0):
        """Write an error to console"""
        string = colorize('Error:', 'red')
        string += ' {0}'.format(arg)
        if filename is not None:
            string += '\n   [Reported from {0!r}]'.format(filename)
        write_to_console('{0}{1}'.format(string, end), -100)
        if noraise:
            return
        if cfg.verbosity > 1:
            raise Exception(string)
        sys.exit(1)


def printc(*args, **kwargs):  # pragma: no cover
    if not cfg.debug:
        return
    end = kwargs.pop('end', '\n')
    s = [str(x) for x in args]
    sys.stderr.write('DEBUG: ' + ' '.join(s) + end)


