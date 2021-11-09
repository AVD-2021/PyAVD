"""
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

import streamlit as st
from streamlit import session_state as sesh

from Models import *
from gpkit import Model, ureg

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")


AC = Aircraft()
print(AC)
# MISSION = Mission(AC)

# M = Model(MISSION.takeoff_fuel, [MISSION, AC])
# print(M)
# sol = M.solve(verbosity=0)