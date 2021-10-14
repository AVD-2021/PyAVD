
'''
Aircraft base class

Includes subclasses Spec(), Config() and Constraints()

'''

class Aircraft:

    def __init__(ac, spec, config, constraints):
        ac.Spec = spec
        ac.Config = config
        ac.Constraints = constraints

        
