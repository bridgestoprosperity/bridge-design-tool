import streamlit as st

st.set_page_config(page_title="Bridge Pricing", page_icon="🌉", layout="wide")

st.markdown("# Bridge Cost Estimation Tool")
tab1, tab2 = st.tabs(["Suspension Bridge", "Suspended Bridge"])
# st.markdown(" ## Suspension Bridge Design")

with tab1:
    col1, col2 = st.columns(2)

    bridge_cost = 0

    a_concrete_works = 7200000
    b_steel_reinforcement = 3500000
    c_tower_system = 12200000
    d_steel_decking_crossbeams = 110000+18000+70000
    e_fencing_system = 150
    f_ramp_post_system = 375000
    g_restraint_handrail_wires = 55000
    h_cables_clips = 275000
    i_temporary_works = 900000
    j_misc_building_materials = 500000
    k_sign_for_bridge = 120000
    l_certificates_manuals_printing = 220000
    m_safety_equipment = 3000000
    n_scaffolding_rental = 1000000
    o_tools = 2000000
    p_transportation_site_setup = 2500000
    q_survey_warehouse_misc = 1100000
    r_laborers_operatives = 5300000
    s_site_supervision_foreman_eng = 4250000
    t_expenses = 2950000
    u_expropriation = None
    v_b2p_staff_inc_engineering = None
    w_indirect_company_costs = None

    # returns an updated bridge cost
    def update_bridge_cost(span):
        span_independent_costs = a_concrete_works + b_steel_reinforcement + c_tower_system + f_ramp_post_system + i_temporary_works + j_misc_building_materials + k_sign_for_bridge + l_certificates_manuals_printing + m_safety_equipment + n_scaffolding_rental + o_tools + p_transportation_site_setup + q_survey_warehouse_misc + r_laborers_operatives + s_site_supervision_foreman_eng + t_expenses
        span_dependent_costs = d_steel_decking_crossbeams + e_fencing_system + g_restraint_handrail_wires + h_cables_clips
        return span_dependent_costs*span + span_independent_costs

    with col1:
        span = st.number_input("Estimated bridge span (m)", 40, 160, 120, 1)
        currency = st.radio(
            "Which Currency would you like to use?",
            ["🇺🇸 USD", "🇷🇼 RWF", "Both"]
            )

        if currency == '🇷🇼 RWF':
            exchange_rate = 1
            bridge_cost = update_bridge_cost(span)
            st.markdown(f"## Estimated cost: {bridge_cost:,.2f} RWF")
        elif currency == '🇺🇸 USD':
            exchange_rate = st.number_input("🇷🇼 RWF to 🇺🇸 USD exchange rate", 0.00, 1000000.00,1273.00, 0.01)
            bridge_cost = update_bridge_cost(span)
            st.markdown(f"## Estimated cost: {bridge_cost/exchange_rate:,.2f} USD")
        else:
            exchange_rate = st.number_input("🇷🇼 RWF to 🇺🇸 USD exchange rate", 0.00, 1000000.00,1273.00, 0.01)
            bridge_cost = update_bridge_cost(span)
            st.markdown(f"## Estimated Bridge Cost: {bridge_cost:,.2f} RWF")
            st.markdown(f"## Estimated Bridge Cost: {bridge_cost/exchange_rate:,.2f} USD")

    with col2:
        import pandas as pd

        span_list = list(range(40, 161, 5))
        cost_list = [update_bridge_cost(x) for x in span_list]
        df = pd.DataFrame({'Span (m)': span_list, 'Cost (RWF)': cost_list})
        st.line_chart(df, x="Span (m)", y="Cost (RWF)",)

with tab2:
    st.write("## Suspended Bridge Design")
    st.write("This is a work in progress")