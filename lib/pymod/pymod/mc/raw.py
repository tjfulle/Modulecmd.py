import pymod.environ


def raw(*commands):
    """Run the commands given in `commands`"""
    for command in commands:
        pymod.environ.raw_shell_command(command)
