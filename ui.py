import streamlit as st
from smtp_utils import send_outreach_email

def show_settings():
    st.sidebar.title("Settings")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", st.session_state.openai_api_key, type="password")
    if openai_api_key != st.session_state.openai_api_key:
        st.session_state.openai_api_key = openai_api_key

    st.sidebar.subheader("User Information")
    for key, label in st.session_state.user_info.items():
        st.session_state.user_info[key] = st.sidebar.text_input(label, st.session_state.user_info[key])

    st.sidebar.subheader("SMTP Configurations")
    smtp_configs = st.session_state.smtp_configs.copy()
    for i, config in enumerate(smtp_configs):
        with st.sidebar.expander(f"Configuration {i+1}"):
            for key in config:
                config[key] = st.text_input(f"{key.capitalize()} {i+1}", config[key], type="password" if key == "password" else "default")

            if st.button(f"Check Configuration {i+1}", key=f"check_config_{i}"):
                try:
                    smtp = smtplib.SMTP_SSL(config["server"], config["port"]) if config["port"] == 465 else smtplib.SMTP(config["server"], config["port"])
                    smtp.starttls() if config["port"] != 465 else None
                    smtp.login(config["username"], config["password"])
                    smtp.quit()
                    st.success(f"Configuration {i+1} is valid.")
                except smtplib.SMTPAuthenticationError:
                    st.error(f"Authentication failed for Configuration {i+1}.")
                except Exception as e:
                    st.error(f"Error checking Configuration {i+1}: {e}")
    
    st.session_state.smtp_configs = smtp_configs
    if st.sidebar.button("Add SMTP Configuration"):
        st.session_state.smtp_configs.append({"server": "", "port": 587, "username": "", "password": "", "sender_email": ""})

def show_domain_data():
    if st.session_state.domain_data:
        cols = st.columns(3)
        for i, data in enumerate(st.session_state.domain_data):
            with cols[i % 3].expander(data["domain"]):
                outreach_subject = st.text_input(f"Subject for {data['domain']}", f"Backlink Opportunity for {data['domain']}", key=f"subject_{data['domain']}")
                outreach_email = st.text_area(f"Outreach Email for {data['domain']}", data["outreach_email"], height=200, key=f"outreach_email_{data['domain']}")
                selected_email = st.text_input(f"Email to send outreach for {data['domain']}", data["suggested_email"], key=f"selected_email_{data['domain']}")
                send_email = st.checkbox(f"Send Email for {data['domain']}", key=f"send_email_{data['domain']}")
                if send_email:
                    send_outreach_email(data, outreach_subject, outreach_email, selected_email)
    else:
        st.warning("No domain data available. Please scrape some domains first.")
