import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from simple_chalk import chalk

# Configuration
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
app_password = os.getenv("GOOGLE_APP_PW")
sender_email = os.getenv("GOOGLE_SENDER_EMAIL")
subject = "Your Etsy Report is Ready"

# SSL context
context = ssl.create_default_context()

def send_email_with_report(report_file_path: str, recipient_email: str, query: str = "your request"):
    """
    Send an email with the report attached.
    
    Parameters:
    - report_file_path: Full path to the .csv report
    - recipient_email: Email address of the recipient
    - query: Optional, for logging context
    """

    if not os.path.exists(report_file_path):
        print(chalk.red(f"[ERROR] Report file not found: {report_file_path}"))
        return False

    print(chalk.blue(f"[INFO] Attaching file: {report_file_path}"))

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Email body
    body = f"Here is your Etsy keyword analysis report for {query}.\n\nThank you for using our service!"
    message.attach(MIMEText(body, "plain"))

    # Attach file
    try:
        with open(report_file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(report_file_path)}"'
        )
        message.attach(part)
        print(message)
    except Exception as e:
        print(chalk.red(f"[ERROR] Failed to attach file: {e}"))
        return False

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(chalk.green(f"[SUCCESS] Sent email to: {recipient_email} | Query: {query}"))
        return True
    
    except Exception as e:
        print(chalk.red(f"[ERROR] Failed to send email: {e}"))
        return False
