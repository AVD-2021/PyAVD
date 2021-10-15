
'''
Aircraft Specification class for PyAVD

---> Handles the target mission profile and fixed masses

'''

from ..Tools import stub


class Spec:

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
        None


    def WeW0(spec, W0):

        # Equation S 1.2-1 - Operating empty weight fraction
        return spec.We_parameters()[0] * W0 ** spec.We_parameters()[1]