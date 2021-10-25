import numpy as np
from pint.definitions import AliasDefinition
from .. import ureg

def T_a(altitude):

    if altitude < (11 * ureg.km):
        T = 288.15 * ureg.K - 0.0065 * (ureg.K/ureg.meter) * altitude
    
    elif altitude < (20 * ureg.km):
        T = 216.65 * ureg.K

    elif altitude < (32 * ureg.km):
        T = 216.65 + 0.001 * (ureg.K/ureg.meter) * altitude

    return T


def speed_of_sound(altitude):
    gamma = 1.4
    R = 287.1 * (ureg.N * ureg.m / (ureg.kg * ureg.K))
    return np.sqrt(gamma * R * T_a(altitude))