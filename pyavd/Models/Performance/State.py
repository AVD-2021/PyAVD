from gpkit import Model, Vectorize, VectorVariable, parse_variables,  ureg as u
from gpkit.constraints.tight import Tight
from gpkit.nomials.variables import Variable
import numpy as np
from ambiance import Atmosphere
# from .. import sealevel

'''
Notes:
- Need to add point thrust, velocity --> needed by trim analyses

'''

class State:
    """Context for evaluating flight physics

    """

    # Sealevel conditions shared across all instances of State so not in __init__()
    sealevel        = Atmosphere(0)
    rho0            = sealevel.density      * (u.kg / u.m**3)

    def __init__(self, alt, vel, climb_gradient, rho0=rho0):
        h                   = self.h                    = alt
        U                   = self.U                    = vel
        climb_gradient      = self.climb_gradient       = climb_gradient

        # Standard atmosphere model for given altitude
        atmosphere  = Atmosphere(h.to(u.m).magnitude)

        # Maybe better to have a vector for atmospheric states?
        rho         = self.rho        = atmosphere.density              * (u.kg / u.m**3)
        mu          = self.mu         = atmosphere.dynamic_viscosity    * (u.kg / (u.m * u.s))
        sigma       = self.sigma      = rho / rho0

        # Re          = self.Re         = rho * u * aicraft.wing.b / mu

        print(U)
        print(rho)
        print(rho0)
        print(mu)
        print(sigma)
        return None