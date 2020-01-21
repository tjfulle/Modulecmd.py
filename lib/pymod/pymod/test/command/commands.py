from pymod.main import PymodCommand


def test_command_commands_default():
    commands = PymodCommand("commands")
    commands()


def test_command_commands_rst():
    commands = PymodCommand("commands")
    commands("--format=rst")


def test_command_commands_subcommands():
    commands = PymodCommand("commands")
    commands("--format=subcommands")


def test_command_commands_names():
    commands = PymodCommand("commands")
    commands("--format=names")
