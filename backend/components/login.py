"""
Author: Akshay NS
This script fetches the last 5 emails from the user's Gmail inbox.
It uses the IMAP protocol to connect to Gmail's server and fetch the emails.
"""

import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_emails(limit=20):
    EMAIL = os.getenv('EMAIL_USER')
    APP_PASSWORD = os.getenv('EMAIL_PASSWORD')

    if not EMAIL or not APP_PASSWORD:
        print("Error: Missing environment variables for email credentials.")
        exit(1)

    # Connect to Gmail's IMAP server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")

    # Fetch latest emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    # Limit the number of emails to fetch
    email_ids = email_ids[-limit:]

    emails = []
    for e_id in email_ids:
        try:
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if "attachment" not in content_disposition:
                                if content_type == "text/plain":
                                    email_body = part.get_payload(decode=True).decode(errors="ignore")
                                    break
                                elif content_type == "text/html":
                                    email_body = part.get_payload(decode=True).decode(errors="ignore")
                    else:
                        email_body = msg.get_payload(decode=True).decode(errors="ignore")

                    emails.append({
                        "From": msg['From'],
                        "Subject": msg['Subject'],
                        "Date": msg['Date'],
                        "Body": email_body
                    })
        except Exception as e:
            print(f"Error processing email ID {e_id}: {e}")

    mail.logout()
    return emails

if __name__ == "__main__":
    emails = fetch_emails()
    for email in emails:
        print(f"From: {email['From']}\nSubject: {email['Subject']}\nDate: {email['Date']}\nBody: {email['Body']}\n")