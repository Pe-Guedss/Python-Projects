import smtplib
import os

EMAIL_ADRESS = os.environ.get('GMAIL_USER')
EMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)

    subject = "Error in the Sheets Integration"
    body = "Error message"

    msg = f"Subject: {subject}\n\n{body}"

    smtp.sendmail(EMAIL_ADRESS, EMAIL_ADRESS, msg)
