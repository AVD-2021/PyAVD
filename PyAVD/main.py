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
from libraries import Aircraft
import pandas as pd

# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")

"""
# PyAVD
### By AVD Group 11, Department of Aeronautics, Imperial College London.
"""

st.sidebar.markdown("## Number of passengers")
passengers = st.sidebar.number_input("Number of passengers", value=4, min_value=1, max_value=1000)

st.sidebar.markdown("## Number of crew")
crew = st.sidebar.number_input("Number of crew", value=2, min_value=1, max_value=1000)

# Build a flight profile with multiselect - takeoff, cruise, landing, loiter
st.sidebar.markdown("## Target Flight Profile")
flight_profile = st.sidebar.multiselect("Flight profile", ["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"],
                                        default=["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"])

if 'flight_profile' not in st.session_state:
  st.session_state.flight_profile = [["Takeoff"], ["Landing"]]

c = st.empty()

button2 = st.button("Add Climb")
if button2:
  st.session_state.flight_profile.insert(-1, "Climb")
  # a.write(st.session_state.b)

# Needs Breguet range
button3 = st.button("Add Cruise")
if button3:
  # Streamlit number input for cruise speed
  # speed = c.number_input("Cruise speed (kts)", value=0, min_value=0, max_value=1000)
  speed = float(input("Cruise speed (Mach): "))
  raaaaange = float(input("Cruise range (nm): "))
  altitude = float(input("Cruise altitude (ft): "))

  # if c != 0:
  st.session_state.flight_profile.insert(-1, ["Cruise", {"Speed": speed, "Range": raaaaange, "Altitude": altitude}])
    
  # a.write(st.session_state.b)

# Needs Breguet endurance
button4 = st.button("Add Loiter")
if button4:
  st.session_state.flight_profile.insert(-1, "Loiter")
  # a.write(st.session_state.b)

button5 = st.button("Add Descent")
if button5:
  st.session_state.flight_profile.insert(-1, "Descent")
  # a.write(st.session_state.b)

a = st.write(st.session_state.b)


# Create dataframe with the flight profile
# df = pd.DataFrame({"Flight Regime": st.session_state.b[:][:][0]})
# df = pd.DataFrame({""})

# st.dataframe(df)






# Creating a new Aircraft instance
ac = Aircraft(passengers, crew, flight_profile)

print("hello")