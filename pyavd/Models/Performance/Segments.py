from gpkit import Model, Variable, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Takeoff(Model):
    """Takeoff regime model

    Variables
    ---------
    TOP                     [kg/m^2]      Takeoff Parameter
    FL              1200    [m]           Field Length
    CL_max_TO               [-]           Maximum Lift Coefficient
    g               9.81    [m/s^2]       Gravitational Acceleration
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None, CL_max=2.1, CL_clean=1.5):
        # Importing Aircraft() parameters - TODO: remove temporary try/except
        try:
            TW = aircraft.TW
            WS = aircraft.WS
        except AttributeError:
            TW = Variable("TW",     "",         "Thrust to Weight ratio")
            WS = Variable("WS",     "N/m^2",    "Wing Loading")
        
        # Constraints dictionary
        constraints = {}

        # Equations are also handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        k1 = Variable('k', 37.5, 'ft^3/lb', 'Some Random Constant')
        constraints.update({"Takeoff Parameter" : [
                    TOP == FL / k1                                                    ]})
        
        # Aaand here
        constraints.update({"Lift Coeffcient @ Takeoff Equation" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})

        # Annnnnnd here
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= WS / ((CL_max_TO * g * TOP) / 1.21)                         ]}) 
        
        # Returning all constraints
        return constraints


class Climb(Model):
    """Climb regime model

    Variables
    ---------
    CL_max_TO               [-]           Maximum Lift Coefficient
    Cd0                     [-]           Zero Lift Drag Coefficient
    e                       [-]           Oswald Efficiency
    LD                      [-]           Lift-Drag Ratio at climb stage

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, dCd0, de, climb_gradient, AR, CL_max=2.1, CL_clean=1.5):
        
        constraints = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints.update({"Takeoff Cd0" : [
                    Cd0_TO == Cd0 + dCd0                                                    ]})

        constraints.update({"Takeoff Cd0" :[
                    e_TO == e + de                                                   ]})

        
        constraints.update({"Lift Coeffcient @ Takeoff Equation" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})
        
        # Aaand here
        constraints.update({"Lift-Drag Ratio at Climb stage" : [
                    LD == Cl_max_TO/(Cd0_TO + ((Cl_max_TO)**2)/(np.pi*AR*e_TO))                 ]})

        # Annnnnnd here
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= (1/LD) + climb_gradient/100                            ]})
        
        # Returning all constraints
        return constraints

        

# Implement following models
# Cruise
# Descent
# Loiter
# Landing


# General Segment model - couples flight segment with the aircraft model and state
class Segment(Model):
    def setup(self, Aircraft):
        constraints = []
        return [constraints]

