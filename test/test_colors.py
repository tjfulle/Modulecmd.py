import tools
from pymod.color import colorize

class TestColors(tools.TestBase):
    def test_all_colors(self):
        string = 'string'
        colorize(string, 'blue')
        colorize(string, 'black')
        colorize(string, 'red')
        colorize(string, 'green')
        colorize(string, 'yellow')
        colorize(string, 'okblue')
        colorize(string, 'cyan')

