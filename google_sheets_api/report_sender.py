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

    msg.add_alternative (f"""\
        <!DOCTYPE html>
<html lang="en">
<body>
    <h3>
        Good evening,
    </h3>
    <p>
        The following exception ocurred during the program execution:
    </p>
    <blockquote style="border: 1px; background-color: aliceblue; color: red; text-align: center;">
        <p>
            {error_message}
        </p>
    </blockquote>
    <p>
        Sorry for the inconvenience. Please contact your software vendor to more information.
        <br><br>
        Sincerely,
        <br>
        Your Automation Process.
    </p>
</body>
</html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)
