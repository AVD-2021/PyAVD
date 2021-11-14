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
                    TOP == FL / k1                                                    ]})
        
        # CL max at takeoff
        constraints.update({"Lift Coeffcient @ Takeoff Equation" : [
                    CL_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})

        # Thrust to Weight ratio
        constraints.update({"Thrust to Weight constraint" : [
                    TW >= WS / ((CL_max_TO * g * TOP) / 1.21)                         ]}) 
        
        # Returning all constraints
        return constraints


class Climb(Model):
    """Climb regime model

    Variables
    ---------
    Cl_max_TO               [-]           Maximum Lift Coefficient
    LD                      [-]           Lift-Drag Ratio at climb stage
    Cd0_TO                  [-]           Zero Lift Drag Coefficient for takeoff
    e_TO                    [-]           Oswald Efficiency for takeoff
    Cd0_L                   [-]           Zero Lift Drag Coefficient Landing
    e_L                     [-]           Oswald Efficiency Landing

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None, AR=7.5, Cd0=0.017, e=0.9, CL_max=2.1, CL_clean=1.5):
        try:
            TW = aircraft.T0_W0
            WS = aircraft.W0_S
        except AttributeError:
            TW = Variable("TW",     "",         "Thrust to Weight ratio")
            WS = Variable("WS",     "N/m^2",    "Wing Loading")
        
        #Climb1
        constraints1 = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints1.update({"Takeoff Cd0" : [
                    Cd0_TO == Cd0 + 0.04                                                    ]})

        constraints1.update({"Takeoff e" :[
                    e_TO == e - 0.05                                                   ]})

        
        constraints1.update({"Lift Coeffcient @ Takeoff Equation" : [
                    Cl_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})
        
        # Aaand here
        constraints1.update({"Lift-Drag Ratio at Climb" : [
                    LD == Cl_max_TO/(Cd0_TO + ((Cl_max_TO)**2)/(np.pi*AR*e_TO))                 ]})

        climb_gradient = Variable('climb_gradient', 0.1, '-', 'Climb Gradient')

        # Annnnnnd here
        constraints1.update({"Thrust to Weight constraint for Climb1" : [
                    TW >= ((1/LD) + climb_gradient/100) *2                          ]})


        #Climb2
        constraints2 = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints2.update({"Takeoff Cd0" : [
                    Cd0_TO == Cd0 + 0.02                                                    ]})

        constraints2.update({"Takeoff e" :[
                    e_TO == e - 0.05                                                   ]})

        
        constraints2.update({"Lift Coeffcient @ Takeoff Equation" : [
                    Cl_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})
        
        # Aaand here
        constraints2.update({"Lift-Drag Ratio at Climb" : [
                    LD == Cl_max_TO/(Cd0_TO + ((Cl_max_TO)**2)/(np.pi*AR*e_TO))                 ]})

        climb_gradient = Variable('climb_gradient', 2.4, '-', 'Climb Gradient')

        # Annnnnnd here
        constraints2.update({"Thrust to Weight constraint for Climb2" : [
                    TW >= ((1/LD) + climb_gradient/100)*2                            ]})


         #Climb3
        constraints3 = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints3.update({"Takeoff Cd0" : [
                    Cd0_TO == Cd0                                                     ]})

        constraints3.update({"Takeoff e" :[
                    e_TO == e                                                  ]})

        
        constraints3.update({"Lift Coeffcient @ Takeoff Equation" : [
                    Cl_max_TO == CL_clean + 0.7 * (CL_max - CL_clean)                 ]})
        
        # Aaand here
        constraints3.update({"Lift-Drag Ratio at Climb" : [
                    LD == Cl_max_TO/(Cd0_TO + ((Cl_max_TO)**2)/(np.pi*AR*e_TO))                 ]})

        climb_gradient = Variable('climb_gradient', 1.2, '-', 'Climb Gradient')

        # Annnnnnd here
        constraints3.update({"Thrust to Weight constraint for Climb3" : [
                    TW >= ((1/LD) + climb_gradient/100)  *2                          ]})
        
         #Climb4
        constraints4 = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints4.update({"Takeoff Cd0" : [
                    Cd0_L == Cd0 + 0.05                                                    ]})

        constraints4.update({"Landing e" :[
                    e_L == e - 0.1                                                   ]})

        
        # Aaand here
        constraints4.update({"Lift-Drag Ratio at Climb" : [
                    LD == Cl_max/(Cd0_L + ((Cl_max)**2)/(np.pi*AR*e_L))                 ]})

        climb_gradient = Variable('climb_gradient', 2.1, '-', 'Climb Gradient')

        # Annnnnnd here
        constraints4.update({"Thrust to Weight constraint" : [
                    TW >= ((1/LD) + climb_gradient/100) * 0.9 *2                           ]})
        

         #Climb5
        constraints5 = {}

        # Equations are handled as constraints! REPLACE WITH COMMENT ON CONSTRAINT
        constraints5.update({"Takeoff Cd0" : [
                    Cd0_L == Cd0 + 0.05                                                    ]})

        constraints5.update({"Landing e" :[
                    e_L == e - 0.1                                                   ]})
        
        # Aaand here
        constraints5.update({"Lift-Drag Ratio at Climb" : [
                    LD == Cl_max/(Cd0_L + ((Cl_max)**2)/(np.pi*AR*e_L))                 ]})

        climb_gradient = Variable('climb_gradient', 3.2, '-', 'Climb Gradient')

        # Annnnnnd here
        constraints5.update({"Thrust to Weight constraint" : [
                    TW >= ((1/LD) + climb_gradient/100) * 0.9                           ]})

        

        
        # Returning all constraints
        return [constraints1,constraints2,constraints3,constraints4,constraints5]

        

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

