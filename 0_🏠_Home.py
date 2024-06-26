import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🌉",
)
st.logo("./assets/b2plogo.png")
st.sidebar.header("Home")
st.write("# Welcome to Bridges to Prosperity's Bridge Planning Tool")

st.markdown(
    """
    Welcome to the Rural Infrastructure Design Tool. Bridges to Prosperity has developed this page to help you identify the most appropriate crossing structure based on your project and budget.
    
    **👈 Select a tool from the sidebar** to help plan your bridge projects and estimate your project's budget.
"""
)
