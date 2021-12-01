import logging
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

    Variables
    ---------
    h                     alt          [m]             Altitude
    U                     vel          [m/s]           Velocity
    climb_gradient        grad         [-]             Climb gradient
    rho                                [kg/m^3]        Air density
    mu                                 [kg/m/s]        Dynamic viscosity
    sigma                              [-]             Ratio of density to sea level density
    rho0                  1.225        [kg/m^3]        Sea level density
    """

    # Sealevel conditions shared across all instances of State so not in __init__()
    # sealevel        = Atmosphere(0)
    # # rho0            = sealevel.density      * (u.kg / u.m**3)
    # rho0 = Variable("rho0", sealevel.density, "kg/m^3", "Sea level air density")

    @parse_variables(__doc__, globals())
    def __init__(self, alt, vel, grad):
        # h                   = self.h                    = alt
        # U                   = self.U                    = vel
        # climb_gradient      = self.climb_gradient       = climb_gradient
        constraints = []

        # Standard atmosphere model for given altitude
        atmosphere  = Atmosphere(alt.to(u.m).magnitude)

        # Maybe better to have a vector for atmospheric states?
        # rho         = self.rho        = atmosphere.density              * (u.kg / u.m**3)
        # mu          = self.mu         = atmosphere.dynamic_viscosity    * (u.kg / (u.m * u.s))
        # sigma       = self.sigma      = rho / rho0

        rho     = Variable("rho",       atmosphere.density,                 "kg/m^3",           "Air density")
        mu      = Variable("mu",        atmosphere.dynamic_viscosity,       "kg/m/s",           "Dynamic viscosity")
        # sigma   = Variable("sigma",     rho / rho0,                         "",                 "Ratio of density to sea level density")
        constraints += [sigma == rho / rho0]

        # Debugging
        print(f'State: alt={alt}, vel={vel}, climb_gradient={grad}')
        
        return None