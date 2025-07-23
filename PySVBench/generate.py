from ._baseclasses import TestbenchSignal as _TestbenchSignal
from ._baseclasses import TestbenchSequence as _TestbenchSequence
from .basetypes import Clock as _Clock
from .basetypes import OutputSignal as _OutputSignal
from ._baseclasses import CodeBlock as _CodeBlock
from ._baseclasses import BlockType as _BlockType

"""
Generate sequences for testbenches easily.
"""    

class Testbench:

    """
    Generates a full testbench of systemverilog, consisting on a group of sequences.
    """

    def __init__(self, testbench_name: str, testbench_element: str, input_elements: list[_TestbenchSignal | _TestbenchSequence], output_elements: list[_OutputSignal], simulation_steps: int, filepath: str = ""):

        """
        - testbench_name = the name of the testbench. It becomes the name of the module that will have the testbench in systemverilog.
        - testbench_element = the name of the module to be testbenched.
        - input_elements = all the sequences you want for the testbench.
        - output_elements = all the output elements of the testbench.
        - simulation_steps = the number of steps that the sequences will be generated to.
        - filepath = the result filepath of the testbench. By default is [testbench name].sv
        """

        self.testbench_name = testbench_name
        self.testbench_element = testbench_element
        self.input_elements = input_elements
        self.output_elements = output_elements
        self.simulation_steps = simulation_steps
        self.filepath = filepath

        self.code = ""

    def set_input_elements(self, input_elements: list[_TestbenchSignal | _TestbenchSequence]):

        self.input_elements = input_elements

    def update_testbench(self):

        """
        Creates (if not created) and updates the internal representation of the testbench
        """

        codeblocks, order_elements = self._update_testbench_phase1()
        final_str = self._update_testbench_phase2(codeblocks, order_elements)
        self._update_testbench_phase3(final_str)

    def _update_testbench_phase1(self):

        """
        The first phase of updating the testbench.

        Consists on creating codeblocks and propagating through all input_elements
        """

        codeblocks = [_CodeBlock(_BlockType.EXTERN), _CodeBlock(_BlockType.INITIAL), _CodeBlock(_BlockType.ALWAYS)] #the three basic codeblocks

        order_elements = []

        #generates the code for all clocks (because clocks define extra codeblocks and must be put before for avoiding errors)
        for input_element in self.input_elements:

            if type(input_element) == _Clock:
                
                input_element.generate_code(codeblocks)

        for input_element in self.input_elements:

            order_elements.append(input_element.name)

            if isinstance(input_element, _TestbenchSignal):
                input_element.generate_code()
            elif isinstance(input_element, _TestbenchSequence):
                input_element.generate(self.simulation_steps)
                input_element.create_file()
                input_element.generate_code(codeblocks)
            else:
                raise TypeError("Input element is neither TestbenchSignal nor TestbenchSequence")
            
        for output_element in self.output_elements:

            order_elements.append(output_element.name)
            output_element.generate_code(codeblocks)

        return codeblocks, order_elements
    
    def _update_testbench_phase2(self, codeblocks: list[_CodeBlock], order_elements: list[str]):

        """
        Second phase of updating testbench. Consists on generating the final string.
        """

        final_str = "module " + self.testbench_name + "();\n"

        for codeblock in codeblocks:

            if codeblock.blocktype == _BlockType.EXTERN:

                for line in codeblock.codegen:
                    final_str += "    " + line + "\n"

            elif codeblock.blocktype == _BlockType.INITIAL:

                #create the block and add it to the final string
                final_str += "    " + "initial begin\n"
                for line in codeblock.codegen:
                    final_str += "    " * 2 + line + "\n"
                final_str += "    " + "end\n"

            elif codeblock.blocktype == _BlockType.ALWAYS:
                
                if "clock" in codeblock.metadata:

                    final_str += "    " + "always @(posedge " + codeblock.metadata["clock"].name + ") begin\n"
                    for line in codeblock.codegen:
                        final_str += "    " * 2 + line + "\n"
                    final_str += "    " + "end\n"

                else:

                    final_str += "    " + "always begin\n"
                    for line in codeblock.codegen:
                        final_str += "    " * 2 + line + "\n"
                    final_str += "    " + "end\n"

            else:
                raise NotImplementedError("Currently no more codeblock types implemented than EXTERN, INITIAL, and ALWAYS!")
            
        #add the endmodule and the dut
        final_str += "    " + self.testbench_element + " dut(" + ",".join(order_elements) + ");\n"
        final_str += "endmodule"
            
        return final_str
    
    def _update_testbench_phase3(self, final_str: str):

        """
        The final phase of updating the testbench. Consisting on writing the string to the filepath
        """

        with open(self.filepath, "w") as file:
            file.write(final_str)