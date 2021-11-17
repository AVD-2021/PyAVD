from .Fuselage import Fuselage
from .Payload import Payload
from .Wing import Starboard_Wing, Port_Wing
from .Engine import Starboard_Engine, Port_Engine
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

        perf_models     += aircraft.str_wing.dynamic(aircraft.str_wing, state)
        perf_models     += aircraft.prt_wing.dynamic(aircraft.prt_wing, state)
        # TODO: add the empennage, fuselage, engine and UC aero + structural performance models
        # perf_models     += aircraft.empennage.dynamic(aircraft.empennage, state)
        # perf_models     += aircraft.fuselage.dynamic(aircraft.fuselage, state)
        # perf_models     += aircraft.engine.dynamic(aircraft.engine, state)
        # perf_models     += aircraft.uc.dynamic(aircraft.uc, state)
        

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
    M_0                         [kg]          Total Mass
    M_dry                       [kg]          Aircraft Dry Mass
    M_fuel                      [kg]          Starting Fuel Mass
    AR              7.50        [-]           Aspect Ratio
    T0_W0                       [-]           Design Thrust to Weight ratio
    W0_S                        [N/m^2]       Design Wing Loading
    g               9.81        [m/s^2]       Gravitational Acceleration

    Upper Unbounded
    ---------------
    W0_S, T0_W0, M_0

    Lower Unbounded
    ---------------
    T0_W0, W0_S

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        components      = self.components   = []
        systems         = self.systems      = []
        constraints     = self.constraints  = {}

        # Note that {str_} = Starboard, {prt_} = Port
        payload         = self.payload      = Payload()
        # fuse            = self.fuse         = Fuselage()
        # str_wing        = self.str_wing     = Starboard_Wing()
        # prt_wing        = self.prt_wing     = Port_Wing()
        # str_engine      = self.str_engine   = Starboard_Engine()
        # prt_engine      = self.prt_engine   = Port_Engine()
        # empennage       = self.empennage    = Empennage()
        # uc              = self.uc           = UC()
        
        # components      += [payload, fuse, str_wing, prt_wing, str_engine, prt_engine, empennage, uc]
        components      += [payload]
        
        constraints.update({"Dry Mass" : Tight([
                    M_dry >= sum(c.M for c in self.components) + sum(s.M for s in systems)])})
        
        constraints.update({"Total Mass" : Tight([
                    M_0 >= M_fuel + M_dry])})

        # Add bounding constraints - temporary
        self.boundingConstraints()

        return [constraints, components]

    # Dynamic performance model - clones AircraftPerformance()
    dynamic = AircraftPerformance



    def boundingConstraints(self):
        constraints = {}

        ### TODO: remove temporary lower bound constraints

        constraints.update({"Minimum Fuel Mass" : [
                    self.M_fuel >= 1000 * u.kg]})

        # constraints.update({"Maximum Total Mass" : [
        #             self.M_0 <= 100000 * u.kg]})

        # constraints.update({"Minimum Wing Loading" : [
        #             self.W0_S >= 0.1 * u.N / u.m**2]})

        # constraints.update({"Maximum Thrust to Weight" : [
        #             self.T0_W0 <= 1]})

        self.constraints.update({"Boundary Constraints": constraints})
        
    

