from .. import ureg as u

import numpy as np


class Spec:
    """
    Aircraft Specification class for PyAVD

    ---> Handles the target mission profile and fixed masses

    Attributes
    ----------
    Wpax : float
        Passenger weight [kg]

    Wcrew : float
        Crew weight [kg]

    Wpay : float
        Payload weight [kg]

    profile : dict
        Target mission profile

    fixed_weight : float
        Fixed weight [kg]
    
    Methods (Public)
    -------
    WeW0(W0)
        Returns the operating empty weight fraction

    """

    def __init__(spec, pax, crew, mission_profile):
        spec.Wpax = pax * 100 * u.kg
        spec.Wcrew = crew * 100 * u.kg
        spec.Wpay = pax * 23 * u.kg
        spec.profile = mission_profile

        spec.fixed_weight = spec.Wpax + spec.Wcrew + spec.Wpay
    
    
    def __We_parameters(spec):
        '''Returns A and C for the (We/W0) vs (W0) regression fit'''
        return [1.4, -0.1]


    def WeW0(spec, W0):
        '''Takes gross takeoff weight (W0), returns operating empty weight (OEW) fraction'''

        # Equation S 1.2-1 - Operating empty weight fraction
        return spec.__We_parameters()[0] * (W0.to(u.kg).magnitude ** spec.__We_parameters()[1])
    

    def __Breguet_range(self, segment_state, c, LD):
        '''Evaluates weight fraction for a given flight regime'''

        # Equation S 1.3-2 - Breguet range
        return np.exp(-segment_state["Range"] * c / (segment_state["Speed"] * LD))

    
    def __Breguet_endurance(self, segment_state, c, LD):
        return np.exp(- segment_state["Endurance"] * c / LD )


    def WfW0(spec, mission_profile, c, LD):
        '''Takes mission profile, returns fuel weight fraction (Wf/W0)'''

        # Equation S 1.3-1 - Fuel weight fraction
        aggregate = 1
        spec.fuel_fracs = []

        for i in range(len(mission_profile)):
            if mission_profile[i][0].lower() == "takeoff":
                aggregate *= 0.97
                spec.fuel_fracs.append(0.97)
                
            elif mission_profile[i][0].lower() == "climb":
                aggregate *= 0.985
                spec.fuel_fracs.append(0.985)
                
            elif mission_profile[i][0].lower() == "landing":
                aggregate *= 0.995
                spec.fuel_fracs.append(0.995)

            elif mission_profile[i][0].lower() == "cruise":
                cruise_frac = spec.__Breguet_range(mission_profile[i][1], c[0], LD[0])
                aggregate *= cruise_frac
                spec.fuel_fracs.append(np.round(cruise_frac.magnitude[0], 3))

            elif mission_profile[i][0].lower() == "descent":
                aggregate *= 0.99
                spec.fuel_fracs.append(0.99)

            elif mission_profile[i][0].lower() == "loiter":
                loiter_frac = spec.__Breguet_endurance(mission_profile[i][1], c[1], LD[1])
                aggregate *= loiter_frac
                spec.fuel_fracs.append(np.round(loiter_frac.magnitude, 3))
                
        spec.fuel_weight_fraction = 1.01 * (1 - aggregate)
        return spec.fuel_weight_fraction
