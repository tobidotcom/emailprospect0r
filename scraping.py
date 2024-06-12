import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urlparse, urljoin
import streamlit as st

def scrape_domains(domains):
    domain_data = []
    for domain in domains.split("\n"):
        try:
            url = f"https://{domain}" if not urlparse(domain).scheme else domain
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            domain_name = urlparse(url).netloc
            page_title, meta_description = soup.find("title").get_text(), soup.find("meta", attrs={"name":"description"}).get("content", "")
            main_text = " ".join([p.get_text() for p in soup.find_all("p")])

            emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text))
            emails.update([link.get("href").replace("mailto:", "") for link in soup.find_all("a", href=re.compile(r"mailto:"))])
            for element in soup.find_all(text=re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), recursive=True):
                emails.add(element)
            for tag in soup.find_all(True):
                for attr in tag.attrs.values():
                    emails.update(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", str(attr)))
            for link in soup.find_all("a", string=re.compile(r"Contact( Us)?", re.IGNORECASE)):
                try:
                    contact_soup = BeautifulSoup(requests.get(urljoin(url, link.get("href"))).text, "html.parser")
                    emails.update(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", contact_soup.get_text()))
                except Exception as e:
                    st.warning(f"Error retrieving contact page for {domain_name}: {e}")

            prompt = f"""
            Based on the following information about the website {domain_name}:
            Title: {page_title}
            Description: {meta_description}
            Main Text: {main_text[:500]}...
            Craft a personalized email outreach for a backlink opportunity. 
            The email should be friendly, engaging, and highlight the relevance of the website's content to our business. 
            Keep the email concise and actionable.
            Additionally, please include a signature with the following details:
            Name: {st.session_state.user_info['name']}
            Business Name: {st.session_state.user_info['business_name']}
            Website: {st.session_state.user_info['website']}
            Business Description: {st.session_state.user_info['business_description']}
            Email: {st.session_state.user_info['email']}
            Phone Number: {st.session_state.user_info['phone_number']}
            """
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {st.session_state.openai_api_key}"}
            data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500, "n": 1, "stop": None, "temperature": 0.7}
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            outreach_email = response.json()["choices"][0]["message"]["content"].strip()

            email_prompt = f"Here are the email addresses found on the website {domain_name}:\n\n{', '.join(emails)}\n\nBased on the website content and the personalized outreach email, which email address would be the most appropriate to send the outreach to? Please make sure to only respond with the suggested email, nothing else!"
            email_data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": email_prompt}, {"role": "assistant", "content": outreach_email}], "max_tokens": 100, "n": 1, "stop": None, "temperature": 0.7}
            email_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=email_data)
            email_response.raise_for_status()
            suggested_email = email_response.json()["choices"][0]["message"]["content"].strip()

            domain_data.append({"domain": domain_name, "outreach_email": outreach_email, "suggested_email": suggested_email})
        except requests.exceptions.RequestException as e:
            st.error(f"Error scraping data for {domain}: {e}")
            logging.error(f"Error scraping {domain}: {e}")
        except Exception as e:
            st.error(f"Error scraping data for {domain}: {e}")
            logging.error(f"Error scraping {domain}: {e}")
    return domain_data
