from ._baseclasses import TestbenchSignal as _TestbenchSignal
from ._baseclasses import TestbenchSequence as _TestbenchSequence
from .basetypes import Clock as _Clock
from .basetypes import RefName as _RefName
from ._baseclasses import CodeBlock as _CodeBlock
from ._baseclasses import BlockType as _BlockType

"""
Generate sequences for testbenches easily.
"""    

class Testbench:

    """
    Generates a full testbench of systemverilog, consisting on a group of sequences.
    """

    def __init__(self, testbench_name: str, testbench_element: str, module_elements: list[_TestbenchSignal | _TestbenchSequence | _RefName], external_elements: list[_TestbenchSignal | _TestbenchSequence], simulation_steps: int, filepath: str = ""):

        """
        - testbench_name = the name of the testbench. It becomes the name of the module that will have the testbench in systemverilog.
        - testbench_element = the name of the module to be testbenched.
        - module_elements = all the elements (inputs or outputs) that go to the module.
        - external_elements = all the elements that are not used in the dut, only for controlling purposes between others.
        - simulation_steps = the number of steps that the sequences will be generated to.
        - filepath = the result filepath of the testbench. By default is [testbench name].sv
        """

        self.testbench_name = testbench_name
        self.testbench_element = testbench_element
        self.module_elements = module_elements
        self.external_elements = external_elements
        self.simulation_steps = simulation_steps
        self.filepath = filepath

        self.code = ""

    def set_module_elements(self, module_elements: list[_TestbenchSignal | _TestbenchSequence]):

        self.module_elements = module_elements

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
        for module_element in self.module_elements:

            if type(module_element) == _Clock:
                
                module_element.generate_code(codeblocks)

        for module_element in self.module_elements:

            order_elements.append(module_element.name)

            if isinstance(module_element, _TestbenchSignal) and type(module_element) != _Clock:
                module_element.generate_code(codeblocks)
            elif isinstance(module_element, _TestbenchSequence):
                module_element.generate(self.simulation_steps)
                module_element.create_file()
                module_element.generate_code(codeblocks)

            #if another thing, it must be a clock, or directly ignored.

        for external_element in self.external_elements:

            external_element.generate_code(codeblocks) #simply generate the code, not include in order.

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

                final_str += "\n" #extra line jump at the end

            elif codeblock.blocktype == _BlockType.INITIAL:

                #create the block and add it to the final string
                final_str += "    " + "initial begin\n"
                for line in codeblock.codegen:
                    final_str += "    " * 2 + line + "\n"
                final_str += "    " + "end\n\n"

            elif codeblock.blocktype == _BlockType.ALWAYS:
                
                if "clock" in codeblock.metadata:
                    final_str += "    " + codeblock.codegen[0] + "\n" #put the first element "always @(posedge whatever)" directly
                    codeblock.codegen.pop(0) #pop the first element, so it doesn't appear in the next iteration

                    for line in codeblock.codegen:
                        final_str += "    " * 2 + line + "\n"
                    final_str += "    " + "end\n\n"

                else:

                    final_str += "    " + "always begin\n"
                    for line in codeblock.codegen:
                        final_str += "    " * 2 + line + "\n"
                    final_str += "    " + "end\n\n"

            else:
                raise NotImplementedError("Currently no more codeblock types implemented than EXTERN, INITIAL, and ALWAYS!")
            
        #add the endmodule and the dut
        final_str += "    " + self.testbench_element + " dut(" + ", ".join(order_elements) + ");\n"
        final_str += "endmodule"
            
        return final_str
    
    def _update_testbench_phase3(self, final_str: str):

        """
        The final phase of updating the testbench. Consisting on writing the string to the filepath
        """

        if self.filepath == "":
            with open(self.testbench_name + ".sv", "w") as file:
                file.write(final_str)
        else:
            with open(self.filepath, "w") as file:
                file.write(final_str)