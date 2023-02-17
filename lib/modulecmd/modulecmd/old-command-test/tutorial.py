from modulecmd.main import PymodCommand


def test_command_tutorial():
    tutorial = PymodCommand("tutorial")
    tutorial("basic")
    tutorial("teardown")
