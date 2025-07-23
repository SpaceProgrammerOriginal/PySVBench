from ._baseclasses import TestbenchSignal as _TestbenchSignal
from ._baseclasses import TestbenchSequence as _TestbenchSequence

from ._baseclasses import BlockType as _BlockType
from ._baseclasses import CodeBlock as _CodeBlock

"""
All the base class types needed for making a benchmark.
"""

#Signal and derivatives
class OutputSignal(_TestbenchSignal):

    """
    A signal that represents the output of the testbenched element.
    """

    pass #it is a wrapper of TestbenchSignal

class ConstantSignal(_TestbenchSignal):

    """
    A constant signal.
    """

    def __init__(self, name, datatype, bits, value: str):
        super().__init__(name, datatype, bits)

        self.value = value

    def generate_code(self, codeblocks):
        super().generate_code(codeblocks)

        #add to initial block:
        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == _BlockType.INITIAL:
                codeblock.codegen.append(self.name + " = " + str(self.bits) + "'b" + self.value + ";")
                done = True
                break

        if not done:
            raise ReferenceError("No INITIAL block has been found!")

class Clock(_TestbenchSignal):

    def __init__(self, name: str, period: int = 10, start_at: str = "0"):
        super().__init__(name, "logic", 1)

        self.period = period
        self.start_at = start_at

    def generate_code(self, codeblocks: list[_CodeBlock]):
        super().generate_code(codeblocks) #set up variables    

        self._generate_initial_block()
        self._generate_always_block()
        self._create_always_clocked()

    def _generate_initial_block(self):

        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == _BlockType.INITIAL:
                codeblock.codegen.append(self.name + " = 1'b" + str(self.start_at) + ";")
                done = True
                break

        if not done:
            raise ReferenceError("No INITIAL block has been found!")
        
    def _generate_always_block(self):

        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == _BlockType.ALWAYS and not "clock" in codeblock.metadata:
                codeblock.codegen.append("#" + str(self.period) + "; " + self.name + " = ~" + self.name + ";") #invert the clock every period
                done = True
                break

        if not done:
            raise ReferenceError("No ALWAYS block has been found!")


    def _create_always_clocked(self):
        
        for codeblock in self.codeblocks:
            
            if codeblock.blocktype == _BlockType.ALWAYS and "clock" in codeblock.metadata: #there is already a clocked always block
                raise ReferenceError("There is already a clocked always blocks. Only one is allowed per testbench")
            
        #there is no always clocked block, create one:
        self.codeblocks.append(
            _CodeBlock(
                blocktype=_BlockType.ALWAYS,
                metadata={"clock": self},
                codegen=["always @(posedge " + self.name + ") begin"]
            )
        )

class Iterator(_TestbenchSignal):

    def __init__(self, name, bits):
        super().__init__(name, "logic", bits)

    def generate_code(self, codeblocks):
        super().generate_code(codeblocks)

        for codeblock in codeblocks:

            if codeblock.blocktype == _BlockType.ALWAYS and "clock" in codeblock.metadata:

                codeblock.codegen.append(self.name + " += 1;")

#Sequence and derivatives
class Testvector(_TestbenchSequence):

    """
    A sequence representing a vector of values.
    """

    def __init__(self, name, datatype, bits, generator, iterator_name, sequence_lenght = -1):
        super().__init__(name, datatype, bits, [], generator, iterator_name, sequence_lenght)

