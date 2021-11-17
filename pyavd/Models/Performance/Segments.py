import logging
from gpkit import Model, Variable, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Takeoff(Model):
    """Takeoff model

    Variables
    ---------
    TOP                             [kg/m^2]      Takeoff Parameter
    FL              fl              [m]           Field Length
    CL_max_TO                       [-]           Maximum Lift Coefficient | Takeoff
    g               9.81            [m/s^2]       Gravitational Acceleration
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None, CL_max=2.1, CL_clean=1.5, fl=1200):
        # Importing Aircraft() parameters - TODO: remove temporary exception
        try:
            TW          = self.TW           = aircraft.T0_W0
            WS          = self.WS           = aircraft.W0_S
            CL_max      = self.CL_max       = aircraft.CL_max
            CL_clean    = self.CL_clean     = aircraft.CL_clean

            logging.info("Aircraft() parameters are now linked")

        except AttributeError:
            logging.warning("Aircraft() object not found. Using default values.")
            
            TW          = self.TW           = Variable("TW",    "",         "Thrust to Weight ratio")
            WS          = self.WS           = Variable("WS",    "N/m^2",    "Wing Loading")
        
        # Constraints dictionary
        constraints     = self.constraints  = {}
        
        # Takeoff Parameter - TOP
        k1 = self.k1 = Variable('k', 37.5, 'ft^3/lb', 'Some Random Constant')
        constraints.update({"Takeoff Parameter" : [
                    TOP == FL / k1                                                        ]})
        
        # CL max at takeoff
        constraints.update({"Lift Coeffcient | Takeoff" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                     ]})

        # Thrust to Weight ratio
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= WS / ((CL_max_TO * g * TOP) / 1.21)                             ]})

        # Fuel fraction for takeoff
        self.fuel_frac = 0.97

        # Add bounding constraints
        self.boundaries()
        
        # Returning all constraints
        return constraints


    def boundaries(self):
        constraints = {}

        ### TODO: remove temporary bound constraints
        constraints.update({"Minimum Wing Loading" : [
                    self.WS >= 0.1 * u.N / u.m**2]})

        constraints.update({"Maximum Thrust to Weight" : [
                    self.TW <= 1]})

        self.constraints.update({"Boundaries": constraints})



class Climb(Model):
    """Climb model (general)
    Variables
    ---------
    CL                              [-]           Lift Coefficient | Climb
    CD                              [-]           Drag Coefficient | Climb
    LD                              [-]           Lift-Drag Ratio | Climb

    """
    @parse_variables(__doc__, globals())
    def setup(self, dCd0, de, climb_gradient, aircraft=None, CL_max=2.1, CL_clean=1.5, goAround=False):
        # Importing Aircraft() parameters - TODO: remove temporary exception
        try:
            self.aircraft = aircraft

            TW          = self.TW           = aircraft.T0_W0
            CL_max      = self.CL_max       = aircraft.CL_max
            CL_clean    = self.CL_clean     = aircraft.CL_clean
            AR          = self.AR           = aircraft.AR
            e           = self.e            = aircraft.e
            Cd0         = self.Cd0          = aircraft.Cd0
        
            logging.info("Aircraft() parameters are now linked")
        
        except AttributeError:
            logging.warning("Aircraft() object not found. Using default values.")

            TW          = self.TW           = Variable("TW",    "",     "Thrust to Weight ratio")
            AR          = self.AR           = Variable("AR",    "",     "Aspect Ratio")
            e           = self.e            = Variable("e",     "",     "Oswald Efficiency")
            Cd0         = self.Cd0          = Variable("Cd0",   "",     "Zero-Lift Drag Coefficient")

        Cd0_climb   = self.Cd0_climb   = Variable("Cd0_climb",      Cd0 + dCd0,     "",     "Variation in Cd0")
        e_climb     = self.e_climb     = Variable("e_climb",        e + de,         "",     "Variation in Oswald efficiency")
        
        constraints = self.constraints = {}
        
        # Switch between initial climb vs go-around climb
        CL_climb = {"Go-around CL|CLimb" : [CL == CL_max]} if goAround else {"Initial CL|Climb" : [CL == CL_clean + 0.7 * (CL_max - CL_clean)]}
        constraints.update(CL_climb)

        # Lift-Drag Ratio
        # constraints.update({"Total Drag Coefficient at Climb" : Tight([
        #             CD >= Cd0_climb + (CL ** 2)/(np.pi * AR * e_climb),
        #             CD <= Cd0_climb + (CL ** 2)/(np.pi * AR * e_climb)                   ])})

        # constraints.update({"Lift-Drag Ratio at Climb" : [
        #             LD == CL / CD                   ]})

        constraints.update({"Thrust to Weight constraint" : [
                    TW >= (Cd0_climb + (CL ** 2)/(np.pi * AR * e_climb)) / CL + climb_gradient/100                                    ]})

        # Fuel Fraction for climb
        self.fuel_frac = 0.985

        # Add bounding constraints
        self.boundaries()
        
        return constraints

    
    def boundaries(self):
        constraints = []

        ### TODO: remove temporary lower bound constraints
        constraints += [self.Cd0_climb >= 1e-6]
        constraints += [self.TW <= 1]
        # constraints += [self.AR <= 50]

        self.constraints.update({"Boundaries": constraints})



class Climb_GoAround(Climb):
    def setup(self, dCd0, de, climb_gradient, aircraft):
        return super().setup(dCd0, de, climb_gradient, aircraft, goAround=True)



class Cruise(Model):
    """Cruise model
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, dCd0, de, cruise_gradient, aircraft=None, CL_max=2.1, CL_clean=1.5):
        None



class Landing(Model):
    """Landing model

    Variables
    ---------
    V_stall                              [m/s]         Target Stall Speed | Landing
    FL                   1200            [m]           Field Length | Landing
    SL_density           1.225           [kg/m^3]      Sea Level Density | Landing

    """
    @parse_variables(__doc__, globals())
    def setup(self,aircraft=None,CL_max=2.1):
        # Importing Aircraft() parameters - TODO: remove temporary exception
        try:
            WS          = aircraft.W0_S
            CL_max      = aircraft.CL_max
        
        except AttributeError:
            WS          = Variable("WS",                        "N/m^2",    "Wing Loading")
            CL_max      = Variable("CL_max",                    "",         "Maximum Lift Coefficient")
        
        # Define emprical constant
        k = Variable('k', 0.5136, 'ft/kts^2', 'Landing Empirical Constant')

        # Define the constraint dictionary
        constraints =  {}

        # Define V_stall
        constraints.update({"Target Stall Speed" : [
                    V_stall == (FL / k) ** 0.5         ]})

        # Max Wing Loading constraint
        constraints.update({"Max Wing Loading" : [
                    WS <= (0.5 * SL_density * (V_stall**2) * CL_max)      ]})

        # Fuel Fraction for landing
        self.fuel_frac = 0.995
        
        # Returning all constraints
        return constraints


# TODO: Implement following models
# Descent
# Loiter


# General Segment model - couples flight segment with the aircraft model and state
class Segment(Model):
    def setup(self, Aircraft):
        constraints = []
        return [constraints]
