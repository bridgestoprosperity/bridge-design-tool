import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Bridge Design Helper", page_icon="🌉", layout="wide")
st.logo("./assets/b2plogo.png")


st.sidebar.header("Updated Bridge Design Helper")
st.write("# Updated Bridge Design Helper")

st.write("Add information you know about your bride design")

max_weight_options = [ "🚶 Pedestrian (1kpa)","🏍️ Motorcycle (4kpa)", "🚗 Automobile (10kpa)", "🚚 Commercial Truck (20kpa)"]
terrain_options = ["Narrow & Steep", "Narrow & Flat", "Wide & Steep", "Wide & Flat"]
bridge_data = {
    "Suspended Cable Bridge": {
        "name": "Suspended Cable Bridge",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[2]],
        "Minimum Span": 40,
        "Maximum Span": 120,
    },
    "Suspension Bridge": {
        "name": "Suspension Bridge",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[2]],
        "Minimum Span": 40,
        "Maximum Span": 150,
    },
    "Timber Log Footbridge": {
        "name": "Timber Log Footbridge",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 5,
        "Maximum Span": 15,
    },
    "Box Culvert": {
        "name": "Box Culvert",
        "Maximum Weight": max_weight_options[2],
        "Terrain Profile": [terrain_options[1], terrain_options[3]],
        "Minimum Span": 5,
        "Maximum Span": 10,
    },
    "Sawn Timber Bridge": {
        "name": "Sawn Timber Bridge",
        "Maximum Weight": max_weight_options[2],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 10,
        "Maximum Span": 20,
    },
    "Masonry Stone Arch Bridge": {
        "name": "Masonry Stone Arch Bridge",
        "Maximum Weight": max_weight_options[3],
        "Terrain Profile": [terrain_options[1], terrain_options[3]],
        "Minimum Span": 5,
        "Maximum Span": 15,
    },
    "Unvented Ford/Drift": {
        "name": "Unvented Ford/Drift",
        "Maximum Weight": max_weight_options[2],
        "Terrain Profile": [terrain_options[1], terrain_options[3]],
        "Minimum Span": 1,
        "Maximum Span": 10,
    },
}

# make sure to pass in index of the max weight
recommended_bridges = []
recommended_bridge_types = []
specs_chart = None
def recommended_bridge(selected_span, selected_traffic, selected_terrain):
    recommended_bridges = []
    for bridge, data in bridge_data.items():
        print ("bridge: ", bridge)
        if selected_span >= data["Minimum Span"] and selected_span <= data["Maximum Span"]:
            print ("selected_span: ", selected_span)
            if selected_traffic <= max_weight_options.index(data["Maximum Weight"]):
                print ("selected_traffic: ", selected_traffic)
                if selected_terrain in data["Terrain Profile"]:
                    print ("selected_terrain: ", selected_terrain)
                    recommended_bridges.append(data["name"])
    return recommended_bridges

def generate_chart(bridge_data, rec_bridges):
    df = pd.DataFrame(bridge_data).T
    df["Minimum Span"] = df["Minimum Span"].astype(str)
    df["Maximum Span"] = df["Maximum Span"].astype(str)
    df["Maximum Weight"] = df["Maximum Weight"].astype(str)
    df["Terrain Profile"] = df["Terrain Profile"]
    df.index.name = "Bridge Type"
    df = df.drop(columns=["name"])
    
    def highlight_row(s):
        is_rec_bridge = s.name in rec_bridges
        return ['background-color: #D1FFBD' if is_rec_bridge else '' for v in s]

    styled_df = df.style.apply(highlight_row, axis=1)
    return styled_df

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### **Terrain Profile**")
    selected_terrain = st.radio(
        "Select the terrain profile of the bridge location", options=terrain_options
    )
    with st.popover("More information"):
        st.markdown("here are images of typical terrain profiles")
with col2:
    st.markdown("### **Traffic Crossing**")
    selected_traffic = st.radio(
        "Select the heaviest traffic you want the bridge to accomodate", options=max_weight_options
    )
with col3:
    st.markdown("### **Approximate Span**")
    selected_span = st.number_input(
        "Enter the estimated span of the bridge in meters",
        min_value=1,
        max_value=300,
        value=50,
    )
    # add a button
    if st.button("**Recommend Bridge Type**", type="primary", use_container_width=True):
        print(selected_span, selected_traffic, selected_terrain)
        recommended_bridge_types = recommended_bridge(int(selected_span), max_weight_options.index(selected_traffic), selected_terrain)
        if recommended_bridge_types == []:
            recommended_bridge_types = [None]
        specs_chart = generate_chart(bridge_data, recommended_bridge_types)
        print(recommended_bridge_types)




if recommended_bridge_types:
    if None in recommended_bridge_types:
        st.write("There is not a bridge type that matches your selected criteria. Review the table below for more information around the constraints of different bridge types.")
    else:
        st.write(f"Based on the information you provided, we recommend the following bridge types:")
        for bridge in recommended_bridge_types:
            st.write(f"🌉 {bridge}")
        st.write("Please consult with a structural engineer to confirm the recommended bridge type")
if specs_chart:
    st.write(specs_chart)
