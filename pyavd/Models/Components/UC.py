from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class UC(Model):
    """Undercarriage model

    Variables
    ---------
    M                       [kg]        Mass
    X_cg                    [ft]        X position of centre of gravity
    Z_cg                    [ft]        Z position of centre of gravity
    X_mg                    [ft]        X position of main gear
    X_ng                    [ft]        X position of nose gear
    Y_mg                    [ft]        Y position of main gears
    h_nose                  [ft]        Height from ground to nose
    Fuselage_upsweep        [-]         Fuselage upsweep angle
    Fuselage_upsweep_length [ft]        Fuselage upsweep length
    H_UC                    [ft]        Height of UC from ground to base of fuselage



    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Undercarriage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([M >= sum(comp.M for comp in components)])]


        return [constraints, components]
    
    def placement(self):
        
        None

    def sizing(self):
        None

    def extreme_cg(self):
        None