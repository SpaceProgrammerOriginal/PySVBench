from enum import Enum, auto
from warnings import warn as _warn
from typing import Generator as _Generator

"""
All the base class types needed for making a benchmark.
"""

class BlockType(Enum):

    EXTERN = auto()
    INITIAL = auto()
    ALWAYS = auto()
    ALWAYS_COMB = auto()
    ALWAYS_FF = auto()
    ALWAYS_LATCH = auto()

class CodeBlock:

    def __init__(self, blocktype: BlockType, metadata: dict = {}, codegen: list[str] = []):
        
        self.blocktype = blocktype
        self.metadata = metadata
        self.codegen = codegen

#Signal and derivatives
class TestbenchSignal:

    """
    Base class for all individual signals that can be used in a benchmark.
    """
    
    def __init__(self, name: str, datatype: str, bits: int):

        """
        - name: name of the signal.
        - datatype: the datatype in systemverilog >2018 ("logic", ...).
        - bits: of how many bits consists the signal
        """

        self.name = name

        self.datatype = datatype

        self.bits = bits

        assert self.bits >= 1, "Bits must be 1 or more!"

    def generate_code(self, codeblocks: list[CodeBlock]):

        """
        Performs code generation.

        - codeblocks: all the codeblocks that the testbench has.
        """

        self.codeblocks = codeblocks

        #does the declaration automatically:
        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == BlockType.EXTERN:

                if self.bits == 1:
                    codeblock.codegen.append("var " + self.datatype + " " + self.name + ";")
                else:
                    codeblock.codegen.append("var " + self.datatype + "["  + str(self.bits - 1) + ":0] " + self.name + ";")
                done = True
                break

        if not done:
            raise ReferenceError("No EXTERN block has been found!")

class OutputSignal(TestbenchSignal):

    """
    A signal that represents the output of the testbenched element.
    """

    pass #it is a wrapper of TestbenchSignal

class ConstantSignal(TestbenchSignal):

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

            if codeblock.blocktype == BlockType.INITIAL:
                codeblock.codegen.append(self.name + " = " + str(self.bits) + "'b" + self.value + ";")
                done = True
                break

        if not done:
            raise ReferenceError("No INITIAL block has been found!")

class Clock(TestbenchSignal):

    def __init__(self, name: str, period: int = 10, start_at: str = "0"):
        super().__init__(name, "logic", 1)

        self.period = period
        self.start_at = start_at

    def generate_code(self, codeblocks: list[CodeBlock]):
        super().generate_code(codeblocks) #set up variables    

        self._generate_initial_block()
        self._generate_always_block()
        self._create_always_clocked()

    def _generate_initial_block(self):

        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == BlockType.INITIAL:
                codeblock.codegen.append(self.name + " = 1'b" + str(self.start_at) + ";")
                done = True
                break

        if not done:
            raise ReferenceError("No INITIAL block has been found!")
        
    def _generate_always_block(self):

        done = False

        for codeblock in self.codeblocks:

            if codeblock.blocktype == BlockType.ALWAYS and not "clock" in codeblock.metadata:
                codeblock.codegen.append("#" + str(self.period) + "; " + self.name + " = ~" + self.name + ";") #invert the clock every period
                done = True
                break

        if not done:
            raise ReferenceError("No ALWAYS block has been found!")


    def _create_always_clocked(self):
        
        for codeblock in self.codeblocks:
            
            if codeblock.blocktype == BlockType.ALWAYS and "clock" in codeblock.metadata: #there is already a clocked always block
                raise ReferenceError("There is already a clocked always blocks. Only one is allowed per testbench")
            
        #there is no always clocked block, create one:
        self.codeblocks.append(
            CodeBlock(
                blocktype=BlockType.ALWAYS,
                metadata={"clock": self},
                codegen=["always @(posedge " + self.name + ") begin"]
            )
        )

class Iterator(TestbenchSignal):

    def __init__(self, name, bits):
        super().__init__(name, "logic", bits)

    def generate_code(self, codeblocks):
        super().generate_code(codeblocks)

        for codeblock in codeblocks:

            if codeblock.blocktype == BlockType.ALWAYS and "clock" in codeblock.metadata:

                codeblock.codegen.append(self.name + " += 1;")

#Sequence and derivatives
class TestbenchSequence:
    
    def __init__(self, name: str, datatype: str, bits: int, sequence: list[str], generator: _Generator[str], iterator_name: str, sequence_lenght: int = -1):


        self.name = name

        self.datatype = datatype
        self.bits = bits
        
        assert self.bits >= 1, "Bits must be 1 or more!"

        self.sequence = sequence
        self.generator = generator
        self.iterator_name = iterator_name
        self.sequence_lenght = sequence_lenght

    def create_file(self):

        with open(self.name + "_tv.mem", "w") as file:
            
            for element in self.sequence:

                file.write(element.rjust(self.bits, "0") + "\n")

    def generate_code(self, codeblocks: list[CodeBlock]):

        done = False

        #instantiate the variable
        for codeblock in codeblocks:

            if codeblock.blocktype == BlockType.EXTERN:
                
                if self.bits == 1:
                    codeblock.codegen.append("var " + self.datatype + " " + self.name + ";")
                    codeblock.codegen.append("var " + self.datatype + " " + self.name + "_tv[" + str(len(self.sequence)-1) + ":0];")
                else:
                    codeblock.codegen.append("var " + self.datatype + "[" + str(self.bits-1) + ":0] " + self.name + ";")
                    codeblock.codegen.append("var " + self.datatype + "[" + str(self.bits-1) + ":0] " + self.name + "_tv[" + str(len(self.sequence)-1) + ":0];")

                done = True

        if not done:
            raise ReferenceError("EXTERN block not found!")
        done = False

        #add the initialization
        for codeblock in codeblocks:

            if codeblock.blocktype == BlockType.INITIAL:

                codeblock.codegen.append("$readmemb(\"" + self.name + "_tv.mem" + "\", " + self.name + ");")
                done = True

        if not done:
            raise ReferenceError("INITIAL block not found!")
        done = False

        #always clocked block:
        for codeblock in codeblocks:

            if codeblock.blocktype == BlockType.ALWAYS and "clock" in codeblock.metadata:

                codeblock.codegen.append(self.name + " = " + self.name + "_tv[" + self.iterator_name + "];")
                done = True

        if not done:
            raise ReferenceError("ALWAYS clocked block not found!")

    def generate(self, lenght_override: int = -1):

        """
        Generates the sequence using the default sequence_lenght and generator. If lenght_override is positive, it will be used as lenght instead of sequence_lenght.
        """

        if lenght_override > 0:

            self.sequence = [next(self.generator) for _ in range(lenght_override)]

        else:

            if self.sequence_lenght > 0:

                self.sequence = [next(self.generator) for _ in range(self.sequence_lenght)]

            else:

                _warn("Sequence not generated because lenght would be infinite. Expected to be generated manually")

    def add_elements(self, elements: list[str]):

        self.sequence += elements

    def set_elements(self, elements: list[str]):

        self.sequence = elements

class Testvector(TestbenchSequence):

    """
    A sequence representing a vector of values.
    """

    pass #literally is simply a direct wrapper of TestbenchSequence.

