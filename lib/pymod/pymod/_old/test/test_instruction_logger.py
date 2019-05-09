import tools
from pymod.instruction_logger import InstructionLogger
class TestInstructionLogger(tools.TestBase):
    def test_instruction_logger(self, capsys):
        IL = InstructionLogger
        IL.start_new_instructions('spam', 'baz')
        IL.append('foo')
        @IL.log_instruction
        def foo(a, b=None):
            pass
        foo(0)
        foo(1, b=2)
        IL.append_collection_instructions('spam', 'baz', 'instruction')
        IL.show()
        out, err = capsys.readouterr()

