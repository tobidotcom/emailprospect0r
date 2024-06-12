import streamlit as st
from config import *
from ui import show_settings, show_domain_data
from scraping import scrape_domains

st.set_page_config(page_title="Domain Scraper", layout="wide")
show_settings()

st.title("Domain Scraper with Email Extraction and Personalized Outreach")
domains = st.text_area("Enter domains (one per line)")

if st.button("Scrape Domains"):
    st.session_state.domain_data = scrape_domains(domains)

show_domain_data()
