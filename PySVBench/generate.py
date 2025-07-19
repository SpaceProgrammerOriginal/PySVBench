from math import ceil
from dataclasses import dataclass as _dataclass
from typing import Generator as _Generator
from warnings import warn as _warn

"""
Generate sequences for testbenches easily.
"""

class Sequence:

    """
    Base class of all sequence types
    """

    def __init__(self, name: str, bits: int, sequence: list[str], generator: _Generator[str], sequence_lenght: int = -1):


        self.name = name
        self.bits = bits
        self.sequence = sequence
        self.generator = generator
        self.sequence_lenght = sequence_lenght

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

class Clock(Sequence):

    """
    A sequence representing a clock.
    """

    def __init__(self, name, period: int):

        def clock_generator():

            while True:
                yield "0"
                yield "1"

        self.period = period
        gen = clock_generator()

        super().__init__(name=name, bits=1, sequence=[], generator=gen, sequence_lenght=-1)

    def generate(self, lenght_override = -1):

        return super().generate(lenght_override)
    
class Testvector(Sequence):
    
    """
    A sequence representing a vector of values.
    """

    pass #literally is simply a direct wrapper of Sequence.

class Testbench:

    """
    Generates a full testbench of systemverilog, consisting on a group of sequences.
    """

    def __init__(self, testbench_name: str,  *sequences: Sequence, filepath: str = "", ):

        """
        - testbench_name = the name of the testbench. It becomes the name of the module that will have the testbench in systemverilog
        - *sequences = all the sequences you want for the testbench.
        - filepath = the result filepath of the testbench. By default is [testbench name].sv
        """

        self.testbench_name = testbench_name
        self.filepath = filepath
        self.sequences = list(sequences)

        self.code = ""

    def set_sequences(self, *sequences: Sequence):

        self.sequences = list(sequences)

    def update_testbench(self):

        """
        Creates (if not created) and updates the internal representation of the testbench
        """

        self.code = "module " + self.testbench_name + "();\n"

        initial_code = "initial begin\n"
        always_code = "always begin\n"

        for sequence in self.sequences:
            pass


        self.code += "    var logic"