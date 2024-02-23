import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bridge Pricing", page_icon="🌉", layout="wide")
bridge_cost = 0
cost = {"suspension": {
        "a_concrete_works": 7200000,
        "b_steel_reinforcement": 3500000,
        "c_tower_system": 8200000+4000000,
        "d_steel_decking_crossbeams": 110000 + 18000 + 70000,
        "e_fencing_system": 15000,
        "f_ramp_post_system": 375000,
        "g_restraint_handrail_wires": 55000,
        "h_cables_clips": 275000,
        "i_temporary_works": 900000,
        "j_misc_building_materials": 500000,
        "k_sign_for_bridge": 120000,
        "l_certificates_manuals_printing": 220000,
        "m_safety_equipment": 3000000,
        "n_scaffolding_rental": 1000000,
        "o_tools": 2000000,
        "p_transportation_site_setup": 2500000,
        "q_survey_warehouse_misc": 1100000,
        "r_laborers_operatives": 5300000,
        "s_site_supervision_foreman_eng": 4250000,
        "t_expenses": 2950000,
        "u_expropriation": 0,
        "v_b2p_staff_inc_engineering": 0,
        "w_indirect_company_costs": 0,
        },
        "suspended": {
        "a_concrete_works": 10700000,
        "b_steel_reinforcement": 820000,
        "c_tower_system": 0,
        "d_steel_decking_crossbeams": 115000 + 70000,
        "e_fencing_system": 15000,
        "f_ramp_post_system": 600000,
        "g_restraint_handrail_wires": 15000,
        "h_cables_clips": 250000,
        "i_temporary_works": 1100000,
        "j_misc_building_materials": 1300000,
        "k_sign_for_bridge": 115000,
        "l_certificates_manuals_printing": 100000,
        "m_safety_equipment": 3000000,
        "n_scaffolding_rental": 0,
        "o_tools": 2000000,
        "p_transportation_site_setup": 1800000,
        "q_survey_warehouse_misc": 1100000,
        "r_laborers_operatives": 6000000,
        "s_site_supervision_foreman_eng": 4250000,
        "t_expenses": 2500000,
        "u_expropriation": 0,
        "v_b2p_staff_inc_engineering": 0,
        "w_indirect_company_costs": 0,
}}


def update_b_cost(span, bridge_type):
    # use dictionary to update the cost of the bridge
    span_independent_costs = cost[bridge_type]["a_concrete_works"] + cost[bridge_type]["b_steel_reinforcement"] + cost[bridge_type]["c_tower_system"] + cost[bridge_type]["f_ramp_post_system"] + cost[bridge_type]["i_temporary_works"] + cost[bridge_type]["j_misc_building_materials"] + cost[bridge_type]["k_sign_for_bridge"] + cost[bridge_type]["l_certificates_manuals_printing"] + \
        cost[bridge_type]["m_safety_equipment"] + cost[bridge_type]["n_scaffolding_rental"] + cost[bridge_type]["o_tools"] + cost[bridge_type]["p_transportation_site_setup"] + \
        cost[bridge_type]["q_survey_warehouse_misc"] + cost[bridge_type]["r_laborers_operatives"] + \
        cost[bridge_type]["s_site_supervision_foreman_eng"] + \
        cost[bridge_type]["t_expenses"]
    span_dependent_costs = cost[bridge_type]["d_steel_decking_crossbeams"] + cost[bridge_type]["e_fencing_system"] + \
        cost[bridge_type]["g_restraint_handrail_wires"] + \
        cost[bridge_type]["h_cables_clips"]
    return span_dependent_costs*span + span_independent_costs


def create_chart(exchange, span_units):
    span_list = list(range(40, 121, 1))
    if span_units == 1:
        suspension_cost_list = [
            ((update_b_cost(x, "suspension")/1)/exchange) for x in span_list]
        suspension_df = pd.DataFrame(
            {'Span (m)': span_list, 'Cost': suspension_cost_list})
        suspended_cost_list = [
            ((update_b_cost(x, "suspended")/1)/exchange) for x in span_list]
        suspended_df = pd.DataFrame(
            {'Span (m)': span_list, 'Cost': suspended_cost_list})
    else:
        suspension_cost_list = [
            ((update_b_cost(x, "suspension")/x)/exchange) for x in span_list]
        suspension_df = pd.DataFrame(
            {'Span (m)': span_list, 'Cost': suspension_cost_list})
        suspended_cost_list = [
            ((update_b_cost(x, "suspended")/x)/exchange) for x in span_list]
        suspended_df = pd.DataFrame(
            {'Span (m)': span_list, 'Cost': suspended_cost_list})

# Create a Plotly figure
    fig = go.Figure()

    # Add the line plot
    # Add the line plot for the suspension bridge
    fig.add_trace(go.Scatter(
        x=suspension_df['Span (m)'],
        y=suspension_df['Cost'],
        mode='lines',
        name='Suspension Bridge',
        line=dict(color='#448AD4', width=3),
    ))
    fig.add_trace(go.Scatter(
        x=suspended_df['Span (m)'],
        y=suspended_df['Cost'],
        mode='lines',
        name='Suspended Bridge',
        line=dict(color='#A0D4FF', width=3),
    ))

    # Add a dot for the selected span and its cost
    fig.add_trace(go.Scatter(
        x=[span],  # Current span as x-coordinate
        # Current cost per meter as y-coordinate
        y=[(bridge_cost/exchange)/span_units],
        mode='markers',
        name='Selected Span',
        marker=dict(color='#FF6060', size=12,line=dict(width=3, color='#d44e4e')),
    ))

    if exchange == 1 and span_units == 1:
        y_title = 'Bridge Cost (RWF)'
    elif exchange == 1 and span_units != 1:
        y_title = 'Cost per Meter (RWF)'
    elif exchange != 1 and span_units == 1:
        y_title = 'Bridge Cost (USD)'
    else:
        y_title = 'Cost per Meter (USD)'

    fig.update_layout(  # Hide the mode bar
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        xaxis=dict(
            title='Bridge Span (m)',
            showline=True,
            showgrid=False,  # No grid lines
            linecolor='#636363',
            title_font=dict(family="Source Sans Pro",
                            size=16, color='#636363'),
            tickfont=dict(family="Source Sans Pro", size=12, color='#636363'),
        ),
        yaxis=dict(
            title=y_title,
            showline=True,
            showgrid=False,  # No grid lines
            linecolor='#636363',
            title_font=dict(family="Source Sans Pro", size=16, color='#636363'),
            tickfont=dict(family="Source Sans Pro", size=12, color='#636363'),
        ),
        font=dict(family="Source Sans Pro", size=14,
                  color="black"),  # Global font settings
        margin=dict(l=20, r=20, t=20, b=20),  # Tighter layout margins
        legend=dict(x=0.5, y=1, xanchor='right', yanchor='top'),
        
    )

    return fig
    
def data_category(bridge_type):
    categories = {
        "materials": cost[bridge_type]["a_concrete_works"] + cost[bridge_type]["b_steel_reinforcement"] + cost[bridge_type]["c_tower_system"] + (cost[bridge_type]["d_steel_decking_crossbeams"]*span) + (cost[bridge_type]["e_fencing_system"]*span) + cost[bridge_type]["f_ramp_post_system"] + (cost[bridge_type]["g_restraint_handrail_wires"]*span) + cost[bridge_type]["j_misc_building_materials"] + cost[bridge_type]["k_sign_for_bridge"] + cost[bridge_type]["l_certificates_manuals_printing"],
        "in_kind": (cost[bridge_type]["h_cables_clips"]*span),
        "tools_and_equipment": cost[bridge_type]["i_temporary_works"]+cost[bridge_type]["m_safety_equipment"] + cost[bridge_type]["n_scaffolding_rental"] + cost[bridge_type]["o_tools"] + cost[bridge_type]["p_transportation_site_setup"],
        "labour": cost[bridge_type]["r_laborers_operatives"],
        "supervision": cost[bridge_type]["s_site_supervision_foreman_eng"]+cost[bridge_type]["t_expenses"],
        "overheads": cost[bridge_type]["q_survey_warehouse_misc"]+cost[bridge_type]["v_b2p_staff_inc_engineering"]+cost[bridge_type]["w_indirect_company_costs"],
        "other": cost[bridge_type]["u_expropriation"]
        }
    return categories

st.markdown("# Bridge Cost Estimation Tool")
st.markdown("This tool estimates the cost of building a bridge based on the span and the type of bridge. Note that this was produced using data from 2023 and all numbers are a general estimate.")
tab1, tab2 = st.tabs(["Suspension Bridge", "Suspended Bridge"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.write("## Suspension Bridge Design")
        span = st.number_input("Estimated bridge span (m)",
                               40, 120, 90, 1, key='span_input_suspension')
        exchange_rate = st.number_input(
            "🇷🇼 RWF to 🇺🇸 USD exchange rate", 0.00, 1000000.00, 1273.00, 0.01, key='exchange_rate_both_suspension')
        bridge_cost = update_b_cost(span, "suspension")
        cole, colf = st.columns(2)
        with cole:
            st.markdown(f"## Bridge Cost:")
            st.success(f"### 🇷🇼 {bridge_cost:,.0f} RWF \n ### 🇺🇸 {bridge_cost / exchange_rate:,.0f} USD")
        with colf:
            st.markdown(f"## Cost per Meter:")
            st.success(f"### 🇷🇼 {(bridge_cost/span):,.0f} RWF/m \n ### 🇺🇸 {((bridge_cost / exchange_rate)/span):,.0f} USD/m")
        
        # todo make a chart breaking down MATERIALS IN-KIND MATERIALS TOOLS AND EQUIPMENT LABOUR SUPERVISION OVERHEADS OTHER 
        suspension_data = data_category("suspension")

        data = [
            {'Category': 'Materials', 'Cost RWF': suspension_data["materials"] - 8200000, 'Cost USD': (suspension_data["materials"]- 8200000)/exchange_rate, "Percentage":str(round((suspension_data["materials"]/bridge_cost)*100))+"%"},
            {'Category': 'In-Kind', 'Cost RWF': suspension_data["in_kind"]+ 8200000, 'Cost USD': (suspension_data["in_kind"]+ 8200000)/exchange_rate, "Percentage":str(round((suspension_data["in_kind"]/bridge_cost)*100))+"%"},
            {'Category': 'Tools & Equipment', 'Cost RWF': suspension_data["tools_and_equipment"], 'Cost USD': suspension_data["tools_and_equipment"]/exchange_rate, "Percentage": str(round((suspension_data["materials"]/bridge_cost)*100))+"%"},
            {'Category': 'Labour', 'Cost RWF': suspension_data["labour"], 'Cost USD': suspension_data["labour"]/exchange_rate, "Percentage":str(round((suspension_data["labour"]/bridge_cost)*100))+"%"},
            {'Category': 'Supervision', 'Cost RWF': suspension_data["supervision"], 'Cost USD': suspension_data["supervision"]/exchange_rate, "Percentage":str(round((suspension_data["supervision"]/bridge_cost)*100))+"%"},
            {'Category': 'Overheads', 'Cost RWF': suspension_data["overheads"], 'Cost USD': suspension_data["overheads"]/exchange_rate, "Percentage":str(round((suspension_data["overheads"]/bridge_cost)*100))+"%"},
            {'Category': 'Total', 'Cost RWF': bridge_cost, 'Cost USD': round(bridge_cost/exchange_rate), "Percentage":''}
        ]
        breakdown_df = pd.DataFrame(data)
        breakdown_df.set_index('Category', inplace=True)
        st.write(breakdown_df)
        
    with col2:
        st.markdown("## Bridge Cost")
        cola, colb = st.columns(2)
        with cola:
            span_units = st.radio("Cost per meter or total cost?", ("Cost per meter", "Total cost"), key='span_units_suspension')
        with colb:
            exchange = st.radio("Currency?", ("RWF", "USD"), key='exchange_suspension')
        if exchange == "RWF" and span_units == "Cost per meter":
            st.plotly_chart(create_chart(1, span), use_container_width=True)
        elif exchange == "RWF" and span_units == "Total cost":
            st.plotly_chart(create_chart(1, 1), use_container_width=True)
        elif exchange == "USD" and span_units == "Cost per meter":
            st.plotly_chart(create_chart(exchange_rate, span), use_container_width=True)
        else:
            st.plotly_chart(create_chart(exchange_rate, 1), use_container_width=True)
    
    st.markdown("## Assumptions & Recommendations")
    st.info("""
        - Anchors and foundations are an averaged lump sum, whereas they are dependent on the length of the bridge. Complete a detailed study or provide tabulated ranges for different size foundations and lengths to come up with a better function of Concrete works vs. Length.
        - 10mm Steel Reinforcement used for suspenders is included in the reinforcement lump sum, whereas the 10mm suspender bars are a function of the length. Differentiate these in the future to determine quantities of 10mm suspenders and 10mm reinforcement used in foundations.
        - 10mm Wires used in the ramp fencing are included in the 10mm handrail/fixation cable costed per meter, but the 10mm wires used in the ramp are a lump sum. Differentiate these in the future.
        - Tower CHS Pipe costs are based on Budgeted cost, not Actual Cost, as are in-kind - data for actual cost needs to be investigated.
        - Towers are lump sum at the moment but need to be differentiated depending on the length of the bridge - bigger bridges mean bigger towers and more cost.
        - Steel Plates are put down as a line item but have an overlap between the steel plates for decking - these need further investigation to differentiate plates used for decking and steel plates used for the tower system.
        - Cables and clips are in-kind materials and are budgeted line items - data for actual costs need to be investigated.
        - Misc Building Materials weren't clearly assigned, so the 500K is an estimated figure; needs checking.
        - Transportation and site setup - needs further cost investigation as there's a huge variance between budget and actual. In the future, these costs could be based upon the distance from the capital.
        - Detailed costing of the engineering and B2P office Staff needs to be investigated.
        - Other B2P Overheads need to be budgeted / Rent / Office Costs etc., including Warehouse / surveying.
        """)


with tab2:

    col3, col4 = st.columns(2)
    with col3:
        st.write("## Suspended Bridge Design")
        span = st.number_input("Estimated bridge span (m)",
                               40, 120, 90, 1, key='span_input_suspended')
        exchange_rate = st.number_input(
            "🇷🇼 RWF to 🇺🇸 USD exchange rate", 0.00, 1000000.00, 1273.00, 0.01, key='exchange_rate_both_suspended')
        bridge_cost = update_b_cost(span, "suspended")
        colg, colh = st.columns(2)
        with colg:
            st.markdown(f"## Bridge Cost:")
            st.success(f"### 🇷🇼 {bridge_cost:,.0f} RWF \n ### 🇺🇸 {bridge_cost / exchange_rate:,.2f} USD")
        with colh:
            st.markdown(f"## Cost per Meter:")
            st.success(f"### 🇷🇼 {(bridge_cost/span):,.0f} RWF/m \n ### 🇺🇸 {((bridge_cost / exchange_rate)/span):,.0f} USD/m")
        
        suspended_data = data_category("suspended")
        data = [
            {'Category': 'Materials', 'Cost RWF': suspended_data["materials"], 'Cost USD': suspended_data["materials"]/exchange_rate, "Percentage":str(round((suspended_data["materials"]/bridge_cost)*100))+"%"},
            {'Category': 'In-Kind', 'Cost RWF': suspended_data["in_kind"], 'Cost USD': suspended_data["in_kind"]/exchange_rate, "Percentage":str(round((suspended_data["in_kind"]/bridge_cost)*100))+"%"},
            {'Category': 'Tools & Equipment', 'Cost RWF': suspended_data["tools_and_equipment"], 'Cost USD': suspended_data["tools_and_equipment"]/exchange_rate, "Percentage": str(round((suspended_data["materials"]/bridge_cost)*100))+"%"},
            {'Category': 'Labour', 'Cost RWF': suspended_data["labour"], 'Cost USD': suspended_data["labour"]/exchange_rate, "Percentage":str(round((suspended_data["labour"]/bridge_cost)*100))+"%"},
            {'Category': 'Supervision', 'Cost RWF': suspended_data["supervision"], 'Cost USD': suspended_data["supervision"]/exchange_rate, "Percentage":str(round((suspended_data["supervision"]/bridge_cost)*100))+"%"},
            {'Category': 'Overheads', 'Cost RWF': suspended_data["overheads"], 'Cost USD': suspended_data["overheads"]/exchange_rate, "Percentage":str(round((suspended_data["overheads"]/bridge_cost)*100))+"%"},
            {'Category': 'Total', 'Cost RWF': bridge_cost, 'Cost USD': round(bridge_cost/exchange_rate), "Percentage":''}
        ]
        breakdown_df = pd.DataFrame(data)
        breakdown_df.set_index('Category', inplace=True)
        st.write(breakdown_df)

        
    with col4:
        st.markdown("## Bridge Cost Per Meter")
        colb, colc = st.columns(2)
        with colb:
            span_units = st.radio("Cost per meter or total cost?", ("Cost per meter", "Total cost"), key='span_units_suspended')
        with colc:
            exchange = st.radio("Currency?", ("RWF", "USD"), key='exchange_suspended')
        if exchange == "RWF" and span_units == "Cost per meter":
            st.plotly_chart(create_chart(1, span), use_container_width=True)
        elif exchange == "RWF" and span_units == "Total cost":
            st.plotly_chart(create_chart(1, 1), use_container_width=True)
        elif exchange == "USD" and span_units == "Cost per meter":
            st.plotly_chart(create_chart(exchange_rate, span), use_container_width=True)
        else:
            st.plotly_chart(create_chart(exchange_rate, 1), use_container_width=True)
        
    st.markdown("## Assumptions & Recommendations")
    st.info("""
    - Anchors and foundations and Ramps are an averaged lump sum, whereas they are dependent on the length of bridge2. A complete detailed study or tabulated ranges for different size foundations and lengths is needed to come up with a better function of Concrete works vs. Length.
    - The Number of Tiers vs. Length of bridge needs to be further investigated/studied to differentiate. Similar to the point above.
    - 10mm Steel Reinforcement used for suspenders is included in the reinforcement lump sum, whereas the 10mm suspender bars are a function of the length. Differentiate these in the future to determine quantities of 10mm suspenders and 10mm reinforcement used in foundations.
    - 10mm Wires used in the ramp fencing are included in the 10mm handrail/fixation cable costed per meter, but the 10mm wires used in the ramp are a lump sum. Differentiate these in the future.
    - Steel Plates and Decking Cost: The cost of Decking per meter and steel plates needs to be verified.
    - Cables and clips are in-kind materials and are budgeted line items - data for actual costs need to be investigated.
    - Misc Building Materials weren't clearly assigned so the 1300K is an estimated figure; needs checking.
    - Transportation and site setup - needs further cost investigation as there is a huge variance between budget and actual. In the future, these costs could be based upon the distance from the capital.
    - Detailed costing of the engineering and B2P office Staff needs to be investigated.
    - Other B2P Overheads need to be budgeted - Rent / Office Costs etc., including Warehouse / surveying.
    """)