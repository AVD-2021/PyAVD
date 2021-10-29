'''Top-level package for PyAVD.'''

import pint
ureg = pint.UnitRegistry(system='mks')      # Handles units in MKS system

from ambiance import Atmosphere
sealevel = Atmosphere(0)

from .Classes import *
from .Tools import *

'''Run this to check the MRO - used to determine the order of inheritance!
As of 28-10-21 --> (<class 'libraries.Classes.Aircraft.Aircraft'>,
                    <class 'libraries.Classes.Constraints.Constraints'>,
                    <class 'libraries.Classes.Config.Config'>,
                    <class 'libraries.Classes.Spec.Spec'>,
                    <class 'object'>)'''
# print(Aircraft.__mro__)
