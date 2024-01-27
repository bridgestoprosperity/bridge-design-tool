import streamlit as st
import time
import numpy as np
st.set_page_config(page_title="Suspended Bridge", page_icon="🌉")
st.markdown("# Suspended Bridge Design Tool")
st.sidebar.header("Suspended Bridge")

bridge_layout = [
    "Span, L", "Deck Width", "Left Saddle Elevation", "Right Saddle Elevation",
    "Height Difference (ΔH)", "Lower Saddle", "Terrain Type",
    "High Water Elevation, HWL", "Freeboard (Fb)", "Handrail Cables",
    "Walkway Cables"]

hoisting_geometry = [
    "Hoisting Sag (Bh)", "hsag (Hoist)", "Lower tower to low point, fhoist"]
dead_load_geometry = ["Dead Load Sag (Bd)", "hsag (Dead)", "Left Tower to low point XLeft",
                      "Left Tower to low point YLeft", "Right Tower to low point XRight",
                      "Right Tower to low point YRight"]

def create_text_inputs(category_name, items):
    st.subheader(category_name)
    input_values = {}
    for item in items:
        input_values[item] = st.text_input(item, "")
    return input_values

# st.text_input(label, value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, *, placeholder=None, disabled=False, label_visibility="visible")
tab1, tab2 = st.tabs(["Input", "Bridge Design Document"])

with tab1:
    st.header("Header")
    community = st.text_input("Community", "")
    county = st.text_input("Municipality/Sector/County", "")
    region = st.text_input("Department/Province/Region", "")
    country = st.text_input("Country", "")
    st.header("Design Summary")
    bridge_layout_values = create_text_inputs("Bridge Layout", bridge_layout)
    hoisting_geometry_values = create_text_inputs("Hoisting Geometry", hoisting_geometry)
    dead_load_geometry_values = create_text_inputs("Dead Load Geometry", dead_load_geometry)


with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.image("./assets/b2p-full-logo.png", width=200)
    
    with col2:
        st.write("Community:", community)
        st.write("Municipality/Sector/County:", county)
        st.write("Department/Province/Region:", region)
        st.write("Country:", country)
        
    for category_values in [bridge_layout_values, hoisting_geometry_values, dead_load_geometry_values]:
        for item, value in category_values.items():
            st.write(f"{item}: {value}")
