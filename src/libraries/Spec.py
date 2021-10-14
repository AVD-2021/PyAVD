
'''
Airfract Specification class

Handles the requirements for the Target Mission Profile and fixed masses

'''

class Spec:

    def __init__(self, spec_dict):
        self.spec_dict = spec_dict

    def load_fixed_weights(self):
        return self.spec_dict['fixed_weight']

    def load_profile(self):
        return self.spec_dict['target_mission_profile']