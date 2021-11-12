from gpkit import Model, Variable, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Takeoff(Model):
    """Takeoff regime model

    Variables
    ---------
    TW                      [-]           Thrust to Weight
    TOP                     [kg/m^2]      Takeoff Parameter
    WS                      [N/m^2]       Wing Loading
    FL              1200    [m]           Field Length
    CL_max_TO               [-]           Maximum Lift Coefficient
    g               9.81    [m/s^2]       Gravitational Acceleration
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, CL_max=2.1, CL_clean=1.5):
        
        constraints = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        k1 = Variable('k', 37.5, 'ft^3/lb', 'Some Random Constant')
        constraints.update({"Takeoff Parameter" : [
                    TOP == FL / k1                                                    ]})
        
        # Aaand here
        constraints.update({"Lift Coeffcient @ Takeoff Equation" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})

        # Annnnnnd here
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= WS / ((CL_max * g * TOP) / 1.21)                            ]})
        
        # Returning all constraints
        return constraints
        

# Implement following models
# Climb
# Cruise
# Descent
# Loiter
# Landing


# General Segment model - couples aircraft model with flight segment and state
class Segment(Model):
    def setup(self, Aircraft):
        constraints = []
        return [constraints]

