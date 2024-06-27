import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bridge Design Helper", page_icon="🌉", layout="wide")

# Sidebar stuff
st.logo("./assets/b2plogo.png")
st.sidebar.header("Updated Bridge Design Helper")

# initial main page content
st.write("# Updated Bridge Design Helper")
st.write("Add information you know about your bride design")

max_weight_options = [ "🚶 🏍️  Pedestrian/Motorcycle (4kpa)", "🚗 Light Vehicle (10kpa)", "🚚 Heavy Vehicle (20kpa)"]
terrain_options = ["Steep", "Flat"]
bridge_data = {
    "Suspended Cable Bridge": {
        "name": "Suspended Cable Bridge",
        "Maximum Weight": max_weight_options[0],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 40,
        "Maximum Span": 120,
        "Approximate Cost": "💸",
    },
    "Suspension Bridge": {
        "name": "Suspension Bridge",
        "Maximum Weight": max_weight_options[0],
        "Terrain Profile": [terrain_options[0], terrain_options[1]],
        "Minimum Span": 40,
        "Maximum Span": 150,
        "Approximate Cost": "💸",
    },
    "Timber Log Footbridge": {
        "name": "Timber Log Footbridge",
        "Maximum Weight": max_weight_options[0],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 5,
        "Maximum Span": 15,
        "Approximate Cost": "💸",
    },
    "Single Cell Box Culvert": {
        "name": "Single Cell Box Culvert",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[1]],
        "Minimum Span": 5,
        "Maximum Span": 10,
        "Approximate Cost": "💸",
    },
    "Sawn Timber Bridge": {
        "name": "Sawn Timber Bridge",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 10,
        "Maximum Span": 20,
        "Approximate Cost": "💸",
    },
    "Single Span Masonry Stone Arch Bridge": {
        "name": "Single Span Masonry Stone Arch Bridge",
        "Maximum Weight": max_weight_options[2],
        "Terrain Profile": [terrain_options[0]],
        "Minimum Span": 5,
        "Maximum Span": 15,
        "Approximate Cost": "💸",
    },
    "Unvented Ford or Drift": {
        "name": "Unvented Ford or Drift",
        "Maximum Weight": max_weight_options[1],
        "Terrain Profile": [terrain_options[1]],
        "Minimum Span": 1,
        "Maximum Span": 10,
        "Approximate Cost": "💸",
    },
}

recommended_bridges = []
recommended_bridge_types = []
specs_chart = None
asterik_value = False
def recommended_bridge(selected_span, selected_traffic, selected_terrain):
    recommended_bridges = []
    for bridge, data in bridge_data.items():
        if selected_span >= data["Minimum Span"] and selected_span <= data["Maximum Span"]:
            if selected_traffic <= max_weight_options.index(data["Maximum Weight"]):
                if selected_terrain in data["Terrain Profile"]:
                    recommended_bridges.append(data["name"])
    return recommended_bridges

def asterik_adder(df, selected_span):
    asterik_value = False
    for i in range(len(df)):
        if df.index[i] == "Single Cell Box Culvert" or df.index[i] == "Single Span Masonry Stone Arch Bridge":
            if int(df.iloc[i]["Maximum Span"]) < selected_span:
                df.iloc[i, df.columns.get_loc("Maximum Span")] = df.iloc[i]["Maximum Span"] + "*"
                asterik_value = True
    return df, asterik_value

def generate_chart(bridge_data, rec_bridges, selected_span, selected_traffic, selected_terrain):
    df = pd.DataFrame(bridge_data).T
    df["Minimum Span"] = df["Minimum Span"].astype(str)
    df["Maximum Span"] = df["Maximum Span"].astype(str)
    df["Maximum Weight"] = df["Maximum Weight"].astype(str)
    df["Terrain Profile"] = df["Terrain Profile"]
    df["Approximate Cost"] = df["Approximate Cost"]
    df.index.name = "Bridge Type"
    df = df.drop(columns=["name"])

    # Apply asterisks before styling
    df, asterik_value = asterik_adder(df, selected_span)

    def highlight_row(s):
        is_rec_bridge = s.name in rec_bridges
        return ['background-color: #B3E2A7' if is_rec_bridge else '' for v in s]

    def highlight_cell(x):
        df_styled = pd.DataFrame('', index=x.index, columns=x.columns)
        for row in range(len(x)):
            if df.index[row] not in rec_bridges and selected_traffic > max_weight_options.index(df.iloc[row]["Maximum Weight"]):
                df_styled.iloc[row, df.columns.get_loc("Maximum Weight")] = 'background-color: #e2a7a7'
            if df.index[row] not in rec_bridges and selected_span > int(df.iloc[row]["Maximum Span"].rstrip('*')):  # Remove '*' for comparison
                df_styled.iloc[row, df.columns.get_loc("Maximum Span")] = 'background-color: #e2a7a7'
            if df.index[row] not in rec_bridges and selected_span < int(df.iloc[row]["Minimum Span"]):
                df_styled.iloc[row, df.columns.get_loc("Minimum Span")] = 'background-color: #e2a7a7'
            if df.index[row] not in rec_bridges and selected_terrain not in df.iloc[row]["Terrain Profile"]:
                df_styled.iloc[row, df.columns.get_loc("Terrain Profile")] = 'background-color: #e2a7a7'
        return df_styled

    styled_df = df.style.apply(highlight_row, axis=1).apply(highlight_cell, axis=None)

    return styled_df, asterik_value


col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### **Terrain Profile**")
    selected_terrain = st.radio(
        "Select the terrain profile of the bridge location", options=terrain_options
    )
    with st.popover("More information"):
        st.markdown("Terrain profiles can have a significant impact on the type of bridge that is most suitable. the pictures below show examples of different terrain profiles.")
        image1, image2, image3, image4 = st.columns(4)
        with image1:
            st.image("https://placehold.co/500x500")
            st.image("https://placehold.co/500x500", caption="Narrow & Steep Terrain")
        with image2:
            st.image("https://placehold.co/500x500")
            st.image("https://placehold.co/500x500", caption="Narrow & Wide Terrain")
        with image3:
            st.image("https://placehold.co/500x500")
            st.image("https://placehold.co/500x500", caption="Wide & Steep Terrain")
        with image4:
            st.image("https://placehold.co/500x500")
            st.image("https://placehold.co/500x500", caption="Wide & Flat Terrain")
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
    if st.button("**Recommend Bridge Type**", type="primary", use_container_width=True):
        recommended_bridge_types = recommended_bridge(int(selected_span), max_weight_options.index(selected_traffic), selected_terrain)
        specs_chart, asterik_value = generate_chart(bridge_data, recommended_bridge_types, int(selected_span), max_weight_options.index(selected_traffic), selected_terrain)

    if not recommended_bridge_types:
        recommended_bridge_types = [None]


if recommended_bridge_types:
    if None in recommended_bridge_types:
        st.write("There is not a bridge type that matches your selected criteria. Review the table below for more information around the constraints of different bridge types.")
    else:
        st.write("Based on the information you provided, we recommend the following bridge types: " + ", ".join([f"**{bridge}**" for bridge in recommended_bridge_types]))
        
        # Create columns based on the number of recommended bridge types
        columns = st.columns(len(recommended_bridge_types))

        # Place each bridge image in its own column
        for i, bridge in enumerate(recommended_bridge_types):
            with columns[i]:
                st.image("./assets/"+bridge+".png", caption=bridge_data[bridge]["name"])


if specs_chart is not None:
    st.write(specs_chart)
    if asterik_value is True:
        st.write("*_Longer bridging structures can be created using this deisgn by adding further spans back-to-back. This would require foundations in the river bed necessitating specialist input._")

    st.warning("Please consult with a structural engineer to confirm the recommended bridge type.")
