load = 'load'
unload = 'unload'
whatis = 'whatis'
help = 'help'
load_partial = 'load_partial'
null = '<>'

def assert_known_mode(mode):
    assert mode in (load, unload, whatis, load_partial, help, null)
