import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bridge Design Helper", page_icon="🌉", layout="wide")

st.sidebar.header("Bridge Design Helper")
st.write("# Bridge Design Helper")
st.write("# Construction Considerations")
# set up three columns to work in
col1, col2 = st.columns(2)
materials = [
    "Concrete Blocks",
    "Earth & Gravel",
    "Gabions",
    "Masonry Stone",
    "Reinforced Concrete",
    "Steel Cables",
    "Structural Timber",
    "Timber Logs",
]
methods = [
    "Assembled On Site",
    "Built On Site",
    "Cast In-Situ",
    "Incremental Launch",
    "Precast",
    "Prefabricated",
]
traffic = ["🚶/🏍️ (4kpa)", "🚗 (10kpa)", "🚚 (20kpa)"]
with col1:
    st.markdown("#### **Principle Structural Material**")
    for i, material in enumerate(materials):
        st.checkbox(
            material,
            key=material,
            value=True,
        )

with col2:
    st.markdown("#### **Construction Method**")
    cola, colb = st.columns(2)
    for i, method in enumerate(methods):
        # put the first half of the methods in the first column
        if i < len(methods) / 2:
            cola.checkbox(method, key=method, value=True)
        # put the second half of the methods in the second column
        else:
            colb.checkbox(method, key=method, value=True)
    selected_traffic = st.select_slider(
        "#### **Weight Limit**", options=traffic, value=(traffic[2])
    )

# create a streamlit data frame, the rows should be bridge types [uspended Cable Bridge	Suspension Bridge	Timber Log Footbridge	Box Culvert	Sawn Timber Bridge	Masonry Stone Arch Bridge	Unvented Ford/Drift], the columns should be materials methods and traffic considerations
# Define the bridge types
bridge_types = [
    "Suspended Cable Bridge",
    "Suspension Bridge",
    "Timber Log Footbridge",
    "Box Culvert",
    "Sawn Timber Bridge",
    "Masonry Stone Arch Bridge",
    "Unvented Ford/Drift",
]

# Define the columns
columns = ["Essential Materials", "Construction Method Options", "Allowable Traffic"]

bridge_data = {
    "Bridge Type": bridge_types,
    "Materials": [
        [materials[5]],  # Suspended Cable Bridge
        [materials[5]],  # Suspension Bridge
        [materials[7]],  # Timber Log Footbridge
        [materials[4]],  # Box Culvert
        [materials[6]],  # Sawn Timber Bridge
        [materials[3]],  # Masonry Stone Arch Bridge
        [materials[4], materials[0], materials[1], materials[2]],  # Unvented Ford/Drift
    ],
    "Methods": [
        [methods[0]],  # Suspended Cable Bridge
        [methods[0]],  # Suspension Bridge
        [methods[1], methods[0], methods[5], methods[3]],  # Timber Log Footbridge
        [methods[4], methods[2]],  # Box Culvert
        [methods[1], methods[0], methods[5], methods[3]],  # Sawn Timber Bridge
        [methods[1]],  # Masonry Stone Arch Bridge
        [methods[1], methods[0]],  # Unvented Ford/Drift
    ],
    "Weight Limit": [
        [traffic[0]],  # Suspended Cable Bridge
        [traffic[0]],  # Suspension Bridge
        [traffic[0]],  # Timber Log Footbridge
        [traffic[2]],  # Box Culvert
        [traffic[2]],  # Sawn Timber Bridge
        [traffic[2]],  # Masonry Stone Arch Bridge
        [traffic[2]],  # Unvented Ford/Drift
    ],
}

bridge_df = pd.DataFrame(bridge_data).set_index("Bridge Type")
def check_materials(val):
    for i in val:
        # print (i)
        if i == "Steel Cables":
            color = '#D1605E50'
        else:
            color = ''
    
    return f'background-color: {color}'

def check_materials_row(row):
    # Check if "Steel Cables" is in any cell of the row
    print ("row_val", row.values)
    for i in row.values:
        if "Steel Cables" in i:
            return ['background-color: #D1605E50'] * len(row)
        else:
            return [''] * len(row)

styled_row_df = bridge_df.style.apply(check_materials_row, axis=1)
styled_df = bridge_df.style.applymap(check_materials)

st.dataframe(
    styled_df,
    use_container_width=True,
    column_config={
        "Materials": st.column_config.ListColumn(
            "Materials",
            width = "medium",
            help="The materials that are essential for the construction of the bridge",
        ),
        "Methods": st.column_config.ListColumn(
            "Methods",
            help="The construction methods that are suitable for the construction of the bridge",
        ),
        "Weight Limit": st.column_config.ListColumn(
            "Weight Limit",
            width = "small",
            help="The allowable traffic that the bridge can support",
        ),
    },
)
st.dataframe(
    styled_row_df,
    use_container_width=True,
    column_config={
        "Materials": st.column_config.ListColumn(
            "Materials",
            width = "medium",
            help="The materials that are essential for the construction of the bridge",
        ),
        "Methods": st.column_config.ListColumn(
            "Methods",
            help="The construction methods that are suitable for the construction of the bridge",
        ),
        "Weight Limit": st.column_config.ListColumn(
            "Weight Limit",
            width = "small",
            help="The allowable traffic that the bridge can support",
        ),
    },
)


st.dataframe(
    bridge_df,
    use_container_width=True,
    column_config={
        "Materials": st.column_config.ListColumn(
            "Materials",
            width = "medium",
            help="The materials that are essential for the construction of the bridge",
        ),
        "Methods": st.column_config.ListColumn(
            "Methods",
            help="The construction methods that are suitable for the construction of the bridge",
        ),
        "Weight Limit": st.column_config.ListColumn(
            "Weight Limit",
            width = "small",
            help="The allowable traffic that the bridge can support",
        ),
    },
)