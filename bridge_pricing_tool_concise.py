import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Simplify cost dictionary structure and calculations
cost = {
    "suspension": {
        "fixed": [7200000, 3500000, 12200000, 375000, 900000, 500000, 120000, 220000, 3000000, 1000000, 2000000, 2500000, 1100000, 5300000, 4250000, 2950000],
        "variable": [128000, 15000, 55000, 275000],
    },
    "suspended": {
        "fixed": [10700000, 820000, 0, 600000, 1100000, 1300000, 115000, 100000, 3000000, 0, 2000000, 1800000, 1100000, 6000000, 4250000, 2500000],
        "variable": [185000, 15000, 15000, 250000],
    },
}

st.set_page_config(page_title="Bridge Pricing", page_icon="🌉", layout="wide")

def update_b_cost(span, bridge_type):
    cost_data = cost[bridge_type]
    return sum(cost_data["fixed"]) + sum(cost_data["variable"]) * span

def create_chart(exchange_rate, span_units, bridge_type):
    span_list = list(range(40, 121))
    cost_list = [(update_b_cost(span, bridge_type) / (span if span_units == "Cost per meter" else 1) / exchange_rate) for span in span_list]
    df = pd.DataFrame({'Span (m)': span_list, 'Cost': cost_list})
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Span (m)'], y=df['Cost'], mode='lines', name=f'{bridge_type.title()} Bridge'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Bridge Span (m)', yaxis_title=f'{"Cost per Meter" if span_units == "Cost per meter" else "Total Cost"} ({exchange_rate})')
    return fig

st.markdown("# Bridge Cost Estimation Tool")

# Define bridge types to iterate over
bridge_types = ["suspension", "suspended"]

for bridge_type in bridge_types:
    with st.container():
        st.write(f"## {bridge_type.title()} Bridge Design")
        span = st.number_input(f"Estimated bridge span (m) for {bridge_type.title()} bridge", 40, 120, 90, key=f'span_{bridge_type}')
        exchange_rate = st.number_input("🇷🇼 RWF to 🇺🇸 USD exchange rate", 0.00, 1000000.00, 1273.00, key=f'exchange_rate_{bridge_type}')
        span_units = st.radio("Cost per meter or total cost?", ["Cost per meter", "Total cost"], key=f'span_units_{bridge_type}')
        exchange = st.radio("Currency?", ["RWF", "USD"], index=0 if exchange_rate == 1 else 1, key=f'currency_{bridge_type}')
        
        bridge_cost = update_b_cost(span, bridge_type)
        st.markdown(f"### Estimated Cost in RWF: 🇷🇼 {bridge_cost:,.2f} RWF")
        st.markdown(f"### Estimated Cost in USD: 🇺🇸 {bridge_cost / exchange_rate:,.2f} USD")
        
        chart_exchange_rate = 1 if exchange == "RWF" else exchange_rate
        st.plotly_chart(create_chart(chart_exchange_rate, span_units, bridge_type), use_container_width=True)
