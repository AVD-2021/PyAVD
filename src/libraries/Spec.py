
'''
Airfract Specification class for PyAVD

- Handles the requirements for the Target Mission Profile and fixed masses

'''


class Spec:

    def __init__(spec, data):
        spec.passengers = data['passengers']
        spec.crew = data['crew']
        spec.payload = data['payload']
        spec.profile = data['target_mission_profile']

        spec.fixed_weight = spec.passengers + spec.crew + spec.payload