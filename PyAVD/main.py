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
from libraries import ac

"""
# PyAVD
### By AVD Group 11, Department of Aeronautics, Imperial College London.
"""

# Input a value for the number of passengers
st.sidebar.markdown("## Number of passengers")
passengers = st.sidebar.number_input("Number of passengers", value=4, min_value=1, max_value=1000)

# Input a value for the number of crew
st.sidebar.markdown("## Number of crew")
crew = st.sidebar.number_input("Number of crew", value=2, min_value=1, max_value=1000)

# Build a flight profile with multiselect - takeoff, cruise, landing, loiter
st.sidebar.markdown("## Target Flight Profile")
flight_profile = st.sidebar.multiselect("Flight profile", ["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"], default=["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"])

