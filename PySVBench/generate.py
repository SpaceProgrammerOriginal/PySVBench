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