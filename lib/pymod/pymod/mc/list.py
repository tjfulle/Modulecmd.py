from six import StringIO
import pymod.mc
from contrib.util.tty import grep_pat_in_string
from llnl.util.tty import terminal_size
from llnl.util.tty.colify import colified


def list(terse=False, show_command=False, regex=None):
    loaded_modules = pymod.mc.get_loaded_modules()
    if not loaded_modules:
        return 'No loaded modules\n'

    sio = StringIO()
    loaded_module_names = []
    for loaded in loaded_modules:
        fullname = loaded.fullname
        if loaded.opts:
            fullname += ' ' + ' '.join(loaded.opts)
        loaded_module_names.append(fullname)

    if terse:
        sio.write('\n'.join(loaded_module_names))
    elif show_command:
        for module in loaded_module_names:
            sio.write('module load {0}\n'.format(module))
    else:
        sio.write('Currently loaded modules\n')
        loaded = ['{0}) {1}'.format(i+1, m)
                  for (i, m) in enumerate(loaded_module_names)]
        _, width = terminal_size()
        sio.write(colified(loaded, indent=4, width=max(100, width)))

    s = sio.getvalue()
    if regex:
        s = grep_pat_in_string(s, regex, color='G')

    return s
