
'''
Airfract Specification class for PyAVD

- Handles the requirements for the Target Mission Profile and fixed masses

'''


class Spec:

    def __init__(spec, data):
        spec.Wpax = data['Wpax']
        spec.Wcrew = data['Wcrew']
        spec.Wpay = data['Wpay']
        spec.profile = data['target_mission_profile']

        spec.fixed_weight = spec.Wpax + spec.Wcrew + spec.Wpay