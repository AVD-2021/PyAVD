"""
 _____ _              _ 
/  ___| |            | |
\ `--.| |_ ___  _ __ | |
 `--. \ __/ _ \| '_ \| |
/\__/ / || (_) | |_) |_|
\____/ \__\___/| .__/(_)
               | |      
               |_|      

 _   _                         _    _ _              _            _      _                   _        __                 _      _                 
| | | |                       | |  (_) |            | |          | |    (_)                 | |      / _|               | |    | |                
| | | |___  ___     __ _ _ __ | | ___| |_           | |_ ___  ___| |_    _ _ __  _   _ _ __ | |__   | |_ ___  _ __    __| | ___| |__  _   _  __ _ 
| | | / __|/ _ \   / _` | '_ \| |/ / | __|          | __/ _ \/ __| __|  | | '_ \| | | | '_ \| '_ \  |  _/ _ \| '__|  / _` |/ _ \ '_ \| | | |/ _` |
| |_| \__ \  __/  | (_| | |_) |   <| | |_           | ||  __/\__ \ |_ _ | | |_) | |_| | | | | |_) | | || (_) | |    | (_| |  __/ |_) | |_| | (_| |
 \___/|___/\___|   \__, | .__/|_|\_\_|\__|           \__\___||___/\__(_)|_| .__/ \__, |_| |_|_.__/  |_| \___/|_|     \__,_|\___|_.__/ \__,_|\__, |
                    __/ | |                 ______                      | |     __/ |                                                      __/ |
                   |___/|_|                |______|                     |_|    |___/                                                      |___/ 



=========================================================



  _____           __      _______  
 |  __ \         /\ \    / /  __ \ 
 | |__) |   _   /  \ \  / /| |  | |
 |  ___/ | | | / /\ \ \/ / | |  | |
 | |   | |_| |/ ____ \  /  | |__| |
 |_|    \__, /_/    \_\/   |_____/           |
         __/ |                               |
        |___/                                |
                                           .-'-.
                                          ' ___ '
                                ---------'  .-.  '---------
                _________________________'  '-'  '_________________________
                 ''''''-|---|--/    \==][^',_m_,'^][==/    \--|---|-''''''
                               \    /  ||/   H   \||  \    /
                                '--'   OO   O|O   OO   '--'

PyAVD - A Python package to pretty much -solve- aircraft conceptual design!


AVD Group 11, Department of Aeronautics, Imperial College London.

"""

import gpkit
import streamlit as st
from streamlit import session_state as sesh

from Models import *
from gpkit import Model, ureg
from gpkit.constraints.bounded import Bounded

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")

## For dodgy situations with signomial inequalities...
# with gpkit.SignomialsEnabled():

#     AC = Aircraft()
#     # print(AC)

#     MISSION = Mission(AC)
#     # print(MISSION)

#     M = Model(AC.M_0 * AC.T0_W0, [Bounded(MISSION), Bounded(AC)])
#     print(M)

#     print(M.variables_byname('AR'))

#     sol = M.localsolve(verbosity=1)
#     print(sol.table())

#     print(M.program.results)

AC = Aircraft()
# print(AC)

MISSION = Mission(AC)
# print(MISSION)

# M = Model(AC.M_0 * AC.T0_W0, [Bounded(MISSION), Bounded(AC)])
M = Model(AC.M_0 * AC.T0_W0, [MISSION, AC])
print(M)

print(M.variables_byname('AR'))

sol = M.solve(verbosity=1)
print(sol.table())