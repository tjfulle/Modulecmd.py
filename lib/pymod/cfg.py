import sys
from .trace import trace_calls


# --------------------------------------------------------------------------- #
# ----------------------------- GLOBAL STATE -------------------------------- #
# --------------------------------------------------------------------------- #
class ConfigDict(dict):
    def __init__(self):
        dict.__init__(self, debug=False, verbosity=1,
                      warn_all=True, cache_avail=True, stop_on_error=True)
        self.pytest_in_progress = False
    def __setitem__(self, key, val):
        if key == 'verbosity' and val > 2:
            sys.settrace(trace_calls)
        dict.__setitem__(self, key, val)
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
cfg = ConfigDict()
