from .Fuselage import Fuselage
from .Wing import Wing
from .Engine import Engine
from .UC import UC
from .Empennage import Empennage

from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class AircraftPerformance(Model):
    """Aircraft performance model

    Variables
    ---------

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        self.aircraft   = aircraft
        self.state      = state
        perf_models     = self.perf_models  = []

        perf_models     += aircraft.wing.dynamic(aircraft.wing, state)
        

        W               = aircraft.W
        S               = aircraft.wing.S
        V               = state.V
        rho             = state.rho


        # D = self.wing_aero.D
        # CL = self.wing_aero.CL
        
        return {"Performance": perf_models}



class Aircraft(Model):
    """The Aircraft model

    Variables
    ---------
    W                       [kg]            Weight

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        components      = self.components   = []
        systems         = self.systems      = []
        constraints     = self.constraints  = []

        fuse            = self.fuse         = Fuselage()
        wing            = self.wing         = Wing()
        engine          = self.engine       = Engine()
        empennage       = self.empennage    = Empennage()
        uc              = self.uc           = UC()
        
        components      += [fuse, wing, engine, empennage, uc]

        # Aircraft is the sum of its component masses
        constraints     += [Tight([ W >= sum(c.W for c in components) + sum(s.W for s in systems)])]

        return [constraints, components]
    
    # Dynamic performance model - creates instance of AircraftPerformance()
    dynamic = AircraftPerformance
