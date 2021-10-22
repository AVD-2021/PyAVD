'''Top-level package for PyAVD.'''

import pint
ureg = pint.UnitRegistry(system='mks')      # Handles units in MKS system

from .Aircraft import *
from .Tools import *

# Run this to check the MRO - used to determine the order of inheritance!
# print(Aircraft.__mro__)