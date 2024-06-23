import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langdetect import detect, DetectorFactory
from googletrans import Translator

DetectorFactory.seed = 0  # Ensure reproducibility

# URL of the JSON data
url = 'https://storage.googleapis.com/datacommons-feeds/claimreview/latest/data.json'

def fetch_data(url):
    # Fetch the JSON data from the URL
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
        return None

def filter_factchecks(data, keyword):
    # Filter the data to get fact-checks related to a specific keyword (e.g., India)
    filtered_factchecks = []
    for item in data.get("dataFeedElement", []):
        item_str = json.dumps(item).lower()
        if keyword.lower() in item_str:
            filtered_factchecks.append(item)
    return filtered_factchecks

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

def translate_to_hindi(text):
    translator = Translator()
    try:
        translation = translator.translate(text, src='auto', dest='hi')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_most_recent_factchecks(factchecks, count=10):
    # Sort the fact-checks by date and get the most recent ones
    sorted_factchecks = sorted(factchecks, key=lambda x: x.get('dateCreated', ''), reverse=True)
    return sorted_factchecks[:count]

def get_claim_source(url):
    # Determine the claim source based on the URL
    if "twitter.com" in url:
        return "Twitter"
    elif "facebook.com" in url:
        return "Facebook"
    elif "whatsapp.com" in url:
        return "WhatsApp"
    elif "news" in url or "newspaper" in url:
        return "News"
    else:
        return "Other"

def get_rating_color(rating):
    # Determine the text color based on the rating
    if rating.lower() in ["false", "misleading", "incorrect", "mostly false"]:
        return "red"
    elif rating.lower() in ["true", "mostly true"]:
        return "green"
    else:
        return "black"

def format_factchecks(factchecks):
    # Format the fact-checks in a regular, non-tabular way
    formatted_factchecks = []
    for factcheck in factchecks:
        claim_review = factcheck["item"][0]
        claim = claim_review.get("claimReviewed", "N/A")
        rating = claim_review.get("reviewRating", {}).get("alternateName", "N/A").capitalize()
        source = claim_review.get("author", {}).get("name", "N/A").title()
        claim_url = claim_review.get("itemReviewed", {}).get("appearance", [{}])[0].get("url", "N/A")
        factcheck_url = claim_review.get("url", "N/A")
        claim_source = get_claim_source(claim_url).title()
        rating_color = get_rating_color(rating)
        
        # Translate claim and rating to Hindi if the claim is not in Hindi
        if detect_language(claim) != 'hi':
            claim_hindi = translate_to_hindi(claim)
            rating_hindi = translate_to_hindi(rating)
            claim = f"{claim} (Translated: {claim_hindi})"
            rating = f"{rating} (Translated: {rating_hindi})"
        
        formatted_factcheck = (
            f"<p>"
            f"<strong>Claim:</strong> {claim}<br>"
            f"<strong>Rating:</strong> <span style='color: {rating_color};'>{rating}</span><br>"
            f"<strong>Source:</strong> {source}<br>"
            f"<strong>Claim URL:</strong> <a href='{claim_url}'>Link</a><br>"
            f"<strong>Factcheck URL:</strong> <a href='{factcheck_url}'>Link</a><br>"
            f"<strong>Claim Source:</strong> {claim_source}<br>"
            f"</p>"
        )
        
        formatted_factchecks.append(formatted_factcheck)
    return formatted_factchecks


def send_email(subject, body, bcc_emails, from_email, from_password):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Send individual emails to each BCC recipient
    for bcc_email in bcc_emails:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ''  # Leave the TO field empty
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        msg['Bcc'] = bcc_email  # Set BCC to the current recipient

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, [bcc_email], msg.as_string())
            server.quit()
            print(f"Email sent successfully to {bcc_email}")
        except Exception as e:
            print(f"Failed to send email to {bcc_email}. Error: {e}")

#def send_email(subject, body, bcc_emails, from_email, from_password):
#    # Set up the SMTP server
#    smtp_server = 'smtp.gmail.com'
#    smtp_port = 587

    # Create the email
#    msg = MIMEMultipart()
#    msg['From'] = from_email
#    msg['To'] = ''
#    msg['Subject'] = subject
#    msg.attach(MIMEText(body, 'html'))

    # Add Bcc recipients
#    msg['Bcc'] = ', '.join(bcc_emails)
    # Send the email
#    try:
#        server = smtplib.SMTP(smtp_server, smtp_port)
#        server.starttls()
#        server.login(from_email, from_password)
#        server.sendmail(from_email, bcc_emails, msg.as_string())
#        server.quit()
#        print("Email sent successfully")
#    except Exception as e:
#        print(f"Failed to send email. Error: {e}")

def main():
    # Fetch the data
    data = fetch_data(url)
    if not data:
        return

    # Filter the fact-checks related to India
    india_factchecks = filter_factchecks(data, "India")

    # Get the most recent fact-checks
    recent_factchecks = get_most_recent_factchecks(india_factchecks)

    # Format the most recent fact-checks
    formatted_factchecks = format_factchecks(recent_factchecks)
    email_body = "".join(formatted_factchecks)

    # Email details
    subject = "Recent Fact-Checks Related to India"
    bcc_emails = []
    from_email = ""  # Your Gmail address
    from_password = ""  # Your Gmail password or app-specific password

    # Send the email
    send_email(subject, email_body, bcc_emails, from_email, from_password)

if __name__ == "__main__":
    main()
