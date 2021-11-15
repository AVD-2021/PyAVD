from gpkit import Model, Variable, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Takeoff(Model):
    """Takeoff model

    Variables
    ---------
    TOP                             [kg/m^2]      Takeoff Parameter
    FL              1200            [m]           Field Length
    CL_max_TO                       [-]           Maximum Lift Coefficient
    g               9.81            [m/s^2]       Gravitational Acceleration
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None, CL_max=2.1, CL_clean=1.5):
        # Importing Aircraft() parameters - TODO: remove temporary exception
        try:
            TW = aircraft.T0_W0
            WS = aircraft.W0_S
        except AttributeError:
            TW = Variable("TW",     "",         "Thrust to Weight ratio")
            WS = Variable("WS",     "N/m^2",    "Wing Loading")
        
        # Constraints dictionary
        constraints = {}

        # Takeoff Parameter - TOP
        k1 = Variable('k', 37.5, 'ft^3/lb', 'Some Random Constant')
        constraints.update({"Takeoff Parameter" : [
                    TOP == FL / k1                                                                  ]})
        
        # CL max at takeoff
        constraints.update({"Lift Coeffcient | Takeoff" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                               ]})

        # Thrust to Weight ratio
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= WS / ((CL_max_TO * g * TOP) / 1.21)                                       ]}) 
        
        # Returning all constraints
        return constraints



class Climb(Model):
    """Climb model (general)
    Variables
    ---------
    CL                              [-]           Lift Coefficient | Climb
    LD                              [-]           Lift-Drag Ratio | Climb
    """
    @parse_variables(__doc__, globals())
    def setup(self, dCd0, de, climb_gradient, aircraft=None, goAround=False):
        # Importing Aircraft() parameters - TODO: remove temporary exception
        try:
            TW          = aircraft.T0_W0
            CL_max      = aircraft.CL_max
            CL_clean    = aircraft.CL_clean
            AR          = aircraft.AR
            e           = aircraft.e
            Cd0         = aircraft.Cd0
        
        except AttributeError:
            TW          = Variable("TW",        "",   "Thrust to Weight ratio")
            CL_max      = Variable("CL_max",    "",   "Maximum Lift Coefficient")
            CL_clean    = Variable("CL_clean",  "",   "Lift Coefficient at zero lift")
            AR          = Variable("AR",        "",   "Aspect Ratio")
            e           = Variable("e",         "",   "Oswald Efficiency")
            Cd0         = Variable("Cd0",       "",   "Zero-Lift Drag Coefficient")
        
        constraints = self.constraints = {}
        
        # Switch between initial climb vs go-around climb
        if goAround:    constraints.update({"Go-around CL|CLimb" : [CL == CL_max]})
        else:           constraints.update({"CL|Climb" : Tight([CL >= CL_clean + 0.7 * (CL_max - CL_clean)])})

        # Lift-Drag Ratio
        constraints.update({"Lift-Drag Ratio at Climb" : [
                    LD == CL / ((Cd0 + dCd0) + (CL ** 2)/(np.pi * AR * (e + de)))                   ]})

        # Annnnnnd here
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= (1/LD) + climb_gradient/100                                               ]})
        
        # Returning all constraints
        return constraints



class Climb_GoAround(Climb):
    def setup(self, dCd0, de, climb_gradient, aircraft):
        super().setup(dCd0, de, climb_gradient, aircraft, goAround=True)
        
        

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

