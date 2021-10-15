
'''
Airfract Specification class for PyAVD

- Handles the target mission profile and fixed masses

'''

# from libraries import Constraints


class Spec:

    def __init__(spec, data):
        spec.Wpax = data['Wpax']
        spec.Wcrew = data['Wcrew']
        spec.Wpay = data['Wpay']
        spec.profile = data['target_mission_profile']

        spec.fixed_weight = spec.Wpax + spec.Wcrew + spec.Wpay

        # spec.Constraints = Constraints()