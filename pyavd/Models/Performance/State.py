from gpkit import Model, Vectorize, VectorVariable, parse_variables,  ureg as u
from gpkit.constraints.tight import Tight
from gpkit.nomials.variables import Variable
import numpy as np
from ambiance import Atmosphere
# from .. import sealevel

'''
temp - remove dis - state variables aint gpkit variables
    Variables
    ---------
    V            [knots]    True Airspeed
    alt          [m]        Altitude
'''

class State:
    """Context for evaluating flight physics

    """

    # Sealevel conditions shared across all instances of State so not in setup()
    sealevel    = Atmosphere(0 * u.ft)                 
    rho0        = sealevel.density      * (u.kg / u.m**3)

    # @parse_variables(__doc__, globals())
    def setup(self, alt, rho0):

        # Maybe better to have a vector for atmospheric states?
        # mu = Atmosphere(alt).dynamic_viscosity

        # Standard atmosphere model for given altitude
        atmosphere  = Atmosphere(alt.to(u.m).magnitude)

        rho         = self.rho        = atmosphere.density    * (u.kg / u.m**3)
        sigma       = self.sigma      = rho / rho0

        return None