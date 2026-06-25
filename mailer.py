import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP Configurations from environment variables with safe fallbacks
SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'no-reply@leaveportal.com')
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sent_emails.log')

def send_email(to_email, subject, html_content):
    """
    Send an email notification. 
    If SMTP server configuration is missing or connection fails, 
    fall back to logging the email to a local file for local testing and debugging.
    """
    email_sent = False
    error_msg = ""

    # Attempt SMTP if server is configured
    if SMTP_SERVER and SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            email_sent = True
            print(f"[MAILER] Email successfully sent to {to_email}: {subject}")
        except Exception as e:
            error_msg = str(e)
            print(f"[MAILER ERROR] SMTP failed, logging instead. Details: {e}")

    # Fallback to local logging (dev mode)
    if not email_sent:
        try:
            log_entry = (
                f"\n========================================================================\n"
                f"TIMESTAMP:   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"TO:          {to_email}\n"
                f"SUBJECT:     {subject}\n"
                f"SMTP STATUS: FAILED/NOT CONFIG (Fallback Logging Active) {f'[{error_msg}]' if error_msg else ''}\n"
                f"------------------------------------------------------------------------\n"
                f"{html_content}\n"
                f"========================================================================\n"
            )
            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(f"[MAILER DEV] Email logged locally to sent_emails.log for {to_email}: {subject}")
        except Exception as file_err:
            print(f"[MAILER CRITICAL] Failed to write to mail log file: {file_err}")

    return email_sent
