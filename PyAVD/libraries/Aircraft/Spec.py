from ..Tools import stub


class Spec:
    '''
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

    K_LD_lookup()
        Returns the K_LD lookup table value for the type of aircraft

    SFC_approx()
        Returns the SFC lookup table value for the type of aircraft
    '''

    def __init__(spec, data=None):
        # spec.Wpax = data['Wpax']
        # spec.Wcrew = data['Wcrew']
        # spec.Wpay = data['Wpay']
        # spec.profile = data['target_mission_profile']

        # spec.fixed_weight = spec.Wpax + spec.Wcrew + spec.Wpay

        # spec.Constraints = Constraints()
        None
    
    
    @stub
    def __We_parameters(spec):
        '''Returns A and C for the (We/W0) vs (W0) regression fit'''
        None


    def WeW0(spec, W0):
        '''Takes gross takeoff weight (W0), returns operating empty weight (OEW) fraction'''

        # Equation S 1.2-1 - Operating empty weight fraction
        return spec.__We_parameters()[0] * W0 ** spec.__We_parameters()[1]

    
    @stub
    def K_LD_lookup(self):
        return None


    @stub
    def SFC_approx(self):
        return None