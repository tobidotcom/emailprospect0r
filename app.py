import streamlit as st
from streamlit.components.v1 import html
from random import random
import requests
from bs4 import BeautifulSoup
import re
import openai

HOR_MATRIX_CSS = """
<style>
@import url(https://fonts.googleapis.com/css?family=Inconsolata);

html {
  min-height: 100%;
}

body {
  box-sizing: border-box;
  height: 100%;
  background-color: #000000;
  background-image: radial-gradient(#11581E, #041607), url("https://media.giphy.com/media/oEI9uBYSzLpBK/giphy.gif");
  background-repeat: no-repeat;
  background-size: cover;
  font-family: 'Inconsolata', Helvetica, sans-serif;
  font-size: 1.5rem;
  color: rgba(128, 255, 128, 0.8);
  text-shadow: 0 0 1ex #33ff33, 0 0 2px rgba(255, 255, 255, 0.8);
}

.matrix {
  line-height: 0.7;
  letter-spacing: -0.05em;
  margin: 0 auto;
  padding: 0;
  white-space: nowrap;
  animation: matrix 10s linear infinite alternate;
}

@keyframes matrix {
  0% {
    transform: translateY(-50%);
  }
  100% {
    transform: translateY(50%);
  }
}
</style>
"""

def generate_matrix_animation():
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    matrix_text = "".join([chars[int(len(chars) * random())] for _ in range(200)])
    matrix_html = f"<div class='matrix'>{matrix_text}</div>"
    return matrix_html

st.set_page_config(page_title="Matrix Animation", page_icon=":computer:")

# Add the CSS for the animation
st.markdown(HOR_MATRIX_CSS, unsafe_allow_html=True)

# Add the Matrix animation HTML
matrix_animation = generate_matrix_animation()
st.markdown(matrix_animation, unsafe_allow_html=True)

# User information
st.sidebar.title("User Information")
st.session_state.user_info = st.sidebar.text_input("Enter your user information in the format: 'name, business_name, website, business_description, email, phone_number'", value="John Doe, Acme Inc., https://acme.com, We provide top-notch widgets, john@acme.com, 555-1234")

# OpenAI API key
openai.api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

# Website URL input
domain_name = st.text_input("Enter the website URL you want to analyze")

if domain_name:
    try:
        # Fetch website content
        response = requests.get(domain_name)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract page title, meta description, and main text
        page_title = soup.title.string if soup.title else ""
        meta_description = soup.find("meta", attrs={"name": "description"}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else ""
        main_text = " ".join([p.get_text() for p in soup.find_all("p")])

        # Extract email addresses
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", str(soup))

        # Update the prompt for generating the personalized email
        prompt = f"Based on the following information about the website {domain_name}:\n\nTitle: {page_title}\nDescription: {meta_description}\nMain Text: {main_text[:500]}...\n\nCraft a personalized cold email to introduce our business and services to the website owners. The email should be professional, engaging, and highlight how our offerings can benefit their business. Keep the email concise and actionable, while avoiding any hard-sell tactics.\n\nAdditionally, please include a signature with the following details:\n\nName: {st.session_state.user_info['name']}\nBusiness Name: {st.session_state.user_info['business_name']}\nWebsite: {st.session_state.user_info['website']}\nBusiness Description: {st.session_state.user_info['business_description']}\nEmail: {st.session_state.user_info['email']}\nPhone Number: {st.session_state.user_info['phone_number']}"

        # Generate the personalized cold email using OpenAI
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )

        personalized_email = response.choices[0].text.strip()

        # Update the prompt for suggesting the best email address
        email_prompt = f"Here are the email addresses found on the website {domain_name}:\n\n{', '.join(emails)}\n\nBased on the website content and the personalized cold email, which email address would be the most appropriate to send the email to? Please make sure to only respond with the suggested email, nothing else!"

        # Suggest the best email address using OpenAI
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=email_prompt,
            max_tokens=64,
            n=1,
            stop=None,
            temperature=0.7,
        )

        suggested_email = response.choices[0].text.strip()

        # Display the personalized cold email and suggested email address
        st.subheader("Personalized Cold Email")
        st.write(personalized_email)

        st.subheader("Suggested Email Address")
        st.write(suggested_email)

    except Exception as e:
        st.error(f"An error occurred: {e}")
