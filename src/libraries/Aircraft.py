
'''
Aircraft base class definition for PyAD

- Incorporates subclasses Spec(), BaselineConfig() and Constraints()

'''


class Aircraft:

    def __init__(ac, spec, config, constraints):
        ac.Spec = spec
        ac.Config = config
        ac.Constraints = constraints

        # On first iteration, approximate aircraft W0 from Baseline Configuration
        ac.W0 = ac.Config.approx_W0()


    def iterate_W0(ac):
        '''
        Uses latest operating empty weight and fuel weight fractions to compute gross takeoff weight
        '''

        # Equation S 1.1-3 - Weight fractions computed in the configuration class
        ac.W0 = ac.Spec.fixed_weight / (1 - ac.Config.WfW0() - ac.Config.WeW0(ac.W0))

    
