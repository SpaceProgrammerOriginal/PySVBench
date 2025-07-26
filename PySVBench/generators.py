from random import randint as _randint

"""
Helper functions to make generators for testbenches easily.
"""

def random_binary_num(a: int, b: int):

    """
    Returns a random binary number in the range [a,b].
    """

    return bin(_randint(a, b)).removeprefix("0b")

def random_bits(bits: int):

    """
    Returns a random number of a certain number of bits.
    """

    return bin(_randint(0, 2**bits - 1)).removeprefix("0b")

