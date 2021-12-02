from gpkit import Model, Variable, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Payload(Model):
    """Payload model

    Variables
    ---------
    M                           [kg]          Total Payload mass
    M_pax                       [kg]          Total Mass of passengers + crew
    M_luggage                   [kg]          Total Mass of luggage
    g                9.81       [m/s^2]       Gravitational Acceleration
    x_cg                        [m]           x Center of Gravity location
    z_cg                        [m]           z Center of Gravity location
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, pax=4, crew=2):
        # Constraints dictionary
        constraints = {}

        # Humans
        m_pax = Variable('m_pax', 100, 'kg', 'Assumed Passenger Weight')
        constraints.update({"Passengers + Crew Mass" : [
                    M_pax == m_pax * (pax + crew)                                    ]})

        # Luggage
        m_luggage = Variable('m_luggage', 27, 'kg', 'Assumed Luggage Weight')
        constraints.update({"Luggage Mass" : [
                    M_luggage == m_luggage * pax                                     ]})

        # Total Payload
        constraints.update({"Total Payload" : Tight([
                    M >= M_pax + M_luggage                                           ])})


        # Returning all constraints
        return constraints


'''
xcg of wing = 6.65m 5m
#xcg of horizontal tail = 13.5*m
#xcg of vertical tail = 13*
xcg of nose landing gear = 0.61m
xcg of main landing gear = 6.8m
#xcg of engine = 11
xcg of engine system = 11m
xcg of fuel system = 6m
xcg of flight control system = 1m
#xcg of hydraulic system = 10.5m
#xcg of pneumatic system = 10.5m
xcg of instruments = 1.5m
xcg of avionics = 1.5m
xcg of electronics = 1.5m
xcg of aircon = 10m
xcg of oxygen = 6.5m
xcg of antiicing = 10m
xcg of furnishing = 5.9m
xcg of luggage = 8m
xcg of cleanwatersystem = 9m
xcg of wastetank = 9m
xcg of passengers = 6.25m
xcg of crew = 2.4m
xcg of wingfuel = 6.65m
xcg of selfsealingfuel = 4.5m

#zcg of wing = -0.3m
#zcg of horizontal tail = 2.3m
#zcg of vertical tail = 2m
zcg of nose landing gear = -0.3m
zcg of main landing gear = -0.76m
#zcg of engine = 1.2m
zcg of engine system = 1.2m
zcg of fuel system = 0.24m
zcg of flight control system = 0.9m
#zcg of hydraulic system =0.245m
zcg of pneumatic sys0.9te0.2410.5m
zcg of instruments = m
zcg of avionics = 0.9m
zcg of electronics = 0.9m
zcg of aircon = 0.69m
zcg of oxygen = 1.64m
zcg of antiicing = 0.69m
zcg of furnishing = 0.48m
zcg of luggage = 0.42m
zcg of cleanwatersystem = -0.0511m
zcg of wastetank = -0.0511m
zcg of passengers = 0.6m
zcg of crew = 0.6m
zcg of wingfuel = 0m
zcg of selfsealingfuel = -0.0511m




'''