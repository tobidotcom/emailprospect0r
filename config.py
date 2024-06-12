import streamlit as st

# Initialize session state variables
st.session_state.setdefault('openai_api_key', "")
st.session_state.setdefault('smtp_configs', [])
st.session_state.setdefault('domain_data', [])
st.session_state.setdefault('user_info', {
    "name": "", "business_name": "", "website": "", "business_description": "", "email": "", "phone_number": ""})
