from .Fuselage import Fuselage
from .Payload import Payload
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

        perf_models     += aircraft.str_wing.dynamic(aircraft.str_wing, state)
        # perf_models     += aircraft.wing.dynamic(aircraft.wing, state)
        # TODO: add the empennage, fuselage, engine and UC performance models
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
    T0_W0                       [-]           Design Thrust to Weight ratio
    W0_S                        [N/m^2]       Design Wing Loading
    g               9.81        [m/s^2]       Gravitational Acceleration

    Upper Unbounded
    ---------------
    W0_S, T0_W0, M_dry

    Lower Unbounded
    ---------------
    W0_S, T0_W0, M_dry

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        components      = self.components   = []
        systems         = self.systems      = []
        constraints     = self.constraints  = {}

        # Note that {str_} = Starboard, {prt_} = Port
        payload         = self.payload      = Payload()
        # fuse            = self.fuse         = Fuselage()
        # str_wing        = self.str_wing     = Wing()
        # prt_wing        = self.prt_wing     = Wing()
        # str_engine      = self.str_engine   = Engine()
        # prt_engine      = self.prt_engine   = Engine()
        # empennage       = self.empennage    = Empennage()
        # uc              = self.uc           = UC()
        
        # components      += [fuse, str_wing, prt_wing, str_engine, prt_engine, empennage, uc]
        
        # Aircraft is the sum of its component masses
        # constraints.update({"Dry Mass" : Tight([
        #             M_dry >= sum(c.M for c in components) + sum(s.M for s in systems)])})
        
        # Payload mass
        M_payload       = self.M_payload    = payload.M_payload
        
        # Total mass
        constraints.update({"Total Mass" : [
                    M_0 >= M_fuel + M_payload]})

        # Add minimum payload mass constraint
        constraints.update({"Minimum Payload Mass" : [
                    M_payload >= 100 * u.kg]})

        # Add minimum fuel mass constraint
        constraints.update({"Minimum Fuel Mass" : [
                    M_fuel >= 1000 * u.kg]})

        # Add maximum total mass constraint
        constraints.update({"Maximum Total Mass" : [
                    M_0 <= 10000 * u.kg]})

        return [components, payload, constraints]
    
    # Dynamic performance model - clones AircraftPerformance()
    dynamic = AircraftPerformance
