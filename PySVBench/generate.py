from math import ceil

"""
Generate sequences for testbenches easily.
"""

class Sequence:

    """
    Represents a sequence of test vectors
    """

    def __init__(self, name_sequence : str = "test_sequence", bits : int = 8, sequence : list[str] = [], default_value : str = "0", sequence_lenght : int = -1):

        """
        Creates a sequence:
            - name_sequence: the name of the sequence
            - bits: the width in bits of the sequence
            - sequence: the sequence indeed, by default it is empty.
            - default_value: the default value that the sequence takes (if it has to fill values)
            - sequence_lenght: the lenght of the sequence, by default is undefined (the lenght of the list in fact)
        """

        self.name_sequence = name_sequence
        self.bits = bits
        self.sequence = sequence
        self.default_value = default_value
        self.sequence_lenght = sequence_lenght
    
    def add_elements(self, elements : list[str]):

        """
        Add an interable of elements to the sequence
        """

        self.sequence.extend(elements)

    def set_elements(self, elements : list[str]):

        """
        Sets the sequence to be equal to the iterable "elements"
        """

        self.sequence = elements

    def create_file(self):

        """
        Creates the test vector file of the sequence, in the specified codec.
        """

        print(str(self) + ":", "creating file")

        with open(self.name_sequence + ".mem", "w") as file:

            print(str(self) + ":", "File created")

            if self.sequence_lenght == -1:

                print(str(self) + ":", "adding full sequence")

                for element in self.sequence:

                    file.write(element.rjust(self.bits, "0") + "\n")
            else:
                print(str(self) + ":", "adding full sequence + default values")
                
                for x in range(self.sequence_lenght):
                    
                    if x < len(self.sequence):

                        file.write(self.sequence[x].rjust(self.bits, "0") + "\n")

                    else:
                        
                        file.write(self.default_value.rjust(self.bits, "0") + "\n")

        print(str(self) + ":", "file created")


    def __repr__(self):
        return "{Sequence: name_sequence: {" + self.name_sequence + "}, bits: {" + str(self.bits) + "}, sequence: {" + str(self.sequence) + "}}"
    
    def __str__(self):
        return "[Sequence: " + self.name_sequence + "]"