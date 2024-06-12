import smtplib
from email.mime.text import MIMEText
import streamlit as st

def send_outreach_email(domain_data, outreach_subject, outreach_email, selected_email):
    success_count = 0
    for smtp_config in st.session_state.smtp_configs:
        try:
            smtp = smtplib.SMTP_SSL(smtp_config["server"], smtp_config["port"]) if smtp_config["port"] == 465 else smtplib.SMTP(smtp_config["server"], smtp_config["port"])
            smtp.starttls() if smtp_config["port"] != 465 else None
            smtp.login(smtp_config["username"], smtp_config["password"])
            msg = MIMEText(outreach_email)
            msg['Subject'] = outreach_subject
            msg['From'] = smtp_config["sender_email"]
            msg['To'] = selected_email
            smtp.send_message(msg)
            success_count += 1
            smtp.quit()
            st.success(f"Email sent successfully using SMTP configuration: {smtp_config['server']}, {smtp_config['username']}")
        except smtplib.SMTPAuthenticationError:
            st.warning(f"Authentication failed for SMTP configuration: {smtp_config['server']}, {smtp_config['username']}")
        except Exception as e:
            st.error(f"Error sending email with SMTP configuration {smtp_config['server']}, {smtp_config['username']}: {e}")

    if success_count > 0:
        st.success(f"Email sent successfully!")
