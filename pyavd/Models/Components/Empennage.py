from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np



class H_TailAero(Model):
    """Horizontal Tailplane model

    Variables
    ---------
    CL_h                                [-]             Lift coefficient of Tailplane
    CL_alpha_h            3.66          [-]             Lift Curve Slope for Tailplane at current AoA
    S_h                   70.0          [ft^2]          Horizontal Tailplane Area
    eta_h                               [-]             Horizontal Tailplane Efficiency
    alpha_0                             [rad]           Zero-lift AoA
    delta_e                             [rad]           Elevator Deflection Angle
    CL_delta_e                          [-]             Lift Curve slope for Elevator at current AoA
    e_h                                 [-]             Oswald Efficiency Factor
    depsilon_dalpha                     [-]             Change of downwash wrt AoA
    """
    #TODO: make ac_h update as we change the tailplane position; i.e. define it as 0.20 of the tailplane chord pos and then get the x value of that

    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        
        aircraft    = self.aircraft
        state       = self.aircraft
        wing        = aircraft.wing

        constraints = {}
        components = self.components = []

        #TODO: airfoil class to re-use for tailplane, wing, cannard etc
        # airfoil = self.airfoil = NACA0015() or whatever

        if aircraft.emp_config     == "T-Tail":    constraints.update({"Tailplane efficiency": [eta_h == 1.0]})
        elif aircraft.emp_config   == "Low-Tail":  constraints.update({"Tailplane efficiency": [eta_h == 0.9]})

        return constraints



class H_Tail(Model):
    """Empennage model

    Variables
    ---------
    M                           [kg]          Mass
    AR              3.5         [-]           Horizontal Tailplane Aspect Ratio 
    b                           [m]           Tailplane Semi-Span
    x_cg             13.50      [m]           x Center of Gravity location
    z_cg             2.30       [m]           z Center of Gravity location
    

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Empennage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([M >= sum(comp.M for comp in components)])]


        return [constraints, components]

    dynamic = H_TailAero


######### MAKE SURE THESE ARE THE RIGHT PARAMETERS - just copied Htail ##############
class V_TailAero(Model):
    """Vertical Tailplane model

    Variables
    ---------
    CL_v                                [-]             Lift coefficient of Tailplane
    CL_alpha_v            3.66          [-]             Lift Curve Slope for Tailplane at current AoA
    S_v                   70.0          [ft^2]          Horizontal Tailplane Area
    eta_v                               [-]             Horizontal Tailplane Efficiency
    alpha_0                             [rad]           Zero-lift AoA
    delta_e                             [rad]           Elevator Deflection Angle
    CL_delta_e                          [-]             Lift Curve slope for Elevator at current AoA
    e_v                                 [-]             Oswald Efficiency Factor
    depsilon_dalpha                     [-]             Change of downwash wrt AoA

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        
        aircraft    = self.aircraft
        state       = self.aircraft
        wing        = aircraft.wing

        constraints = {}

        return constraints



class V_Tail(Model):
    """Empennage model

    Variables
    ---------
    M                           [kg]            Mass
    AR                          [-]             Vertical Tailplane Aspect Ratio 
    b           9.27            [ft]            Vertical Tailplane Span (bottom to top)
    x_cg        13.0            [m]             x Center of Gravity location
    z_cg        2.00            [m]             z Center of Gravity location
    
    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Empennage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([M >= sum(comp.M for comp in components)])]


        return [constraints, components]

    dynamic = V_TailAero
