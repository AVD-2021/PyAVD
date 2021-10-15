
'''Top-level package for PyAVD.'''

from .Aircraft import *
from .Tools import *


# Creating a new Aircraft instance
ac = Aircraft()

# Run this to check the MRO - used to determine the order of inheritance!
# print(Aircraft.__mro__)