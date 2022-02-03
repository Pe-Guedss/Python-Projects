import smtplib
import os
from email.message import EmailMessage

EMAIL_ADRESS = os.environ.get('GMAIL_USER')
EMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

def send_error (error_message: str):
    msg = EmailMessage()
    msg["Subject"] = "Error in the Sheets Integration"
    msg["From"] = EMAIL_ADRESS
    msg["To"] = EMAIL_ADRESS
    msg.set_content(f"""\
        Good evening,

        {error_message}

        Sorry for the inconvenience. Please contact your software vendor to more information.

        Sincerely,

        Your Automation Process.
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)
