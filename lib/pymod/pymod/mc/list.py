from six import StringIO
import pymod.mc
from contrib.util.tty import grep_pat_in_string
from llnl.util.tty import terminal_size
from llnl.util.tty.colify import colified


def list(terse=False, show_command=False, regex=None):
    lm_cellar = pymod.mc.get_cellar()
    if not lm_cellar:
        return 'No loaded modules\n'

    sio = StringIO()
    loaded_modules = []
    for item in lm_cellar:
        fullname = item.fullname
        if item.opts:
            fullname += ' ' + ' '.join(item.opts)
        loaded_modules.append(fullname)

    if terse:
        sio.write('\n'.join(loaded_modules))
    elif show_command:
        for module in loaded_modules:
            sio.write('module load {0}\n'.format(module))
    else:
        sio.write('Currently loaded modules\n')
        loaded = ['{0}) {1}'.format(i+1, m) for i, m in enumerate(loaded_modules)]
        _, width = terminal_size()
        sio.write(colified(loaded, indent=4, width=max(100, width)))

    s = sio.getvalue()
    if regex:
        s = grep_pat_in_string(s, regex)

    return s