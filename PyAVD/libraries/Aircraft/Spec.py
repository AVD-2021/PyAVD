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
    
    Methods
    -------
    We_parameters()
        Returns the We parameters

    WeW0(W0)
        Returns the operating empty weight fraction
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
    def We_parameters(spec):
        '''Returns A and C for the (We/W0) vs (W0) regression fit'''
        None


    def WeW0(spec, W0):
        '''Takes gross takeoff weight (W0), returns operating empty weight (OEW) fraction'''

        # Equation S 1.2-1 - Operating empty weight fraction
        return spec.We_parameters()[0] * W0 ** spec.We_parameters()[1]