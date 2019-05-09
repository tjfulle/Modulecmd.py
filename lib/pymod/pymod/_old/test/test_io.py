import tools
from pymod.config import cfg
from pymod.logging import logging, write_to_console
class TestIO(tools.TestBase):
    def test_write_to_console(self):
        string = 'string'
        write_to_console(string)
        write_to_console(string, end='')
        write_to_console(string, minverbosity=cfg.verbosity+1)
        write_to_console(string, end='', minverbosity=cfg.verbosity+1)
        logging.info('arg')
        logging.debug('arg')
        logging.warning('arg')
        cfg.verbosity = 5
        logging.info('arg', filename='foo')
        logging.debug('arg', filename='foo')
        logging.warning('arg', filename='foo')
        try:
            logging.error('arg', filename='foo')
            assert False
        except:
            pass

