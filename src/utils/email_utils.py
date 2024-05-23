import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logging_utils import setup_logger
import os

logger = setup_logger()

def load_email_config():
    email_config = {
        'server': os.getenv('EMAIL_SERVER'),
        'from': os.getenv('EMAIL_FROM'),
        'to': os.getenv('EMAIL_LIST').split(','),  # Split list if multiple recipients
        'subject': os.getenv('EMAIL_SUBJECT')
    }
    return email_config

def get_email_list():
    email_list = os.getenv('EMAIL_LIST', '').split(',')
    return email_list

def send_email(report, email_config):
    message = MIMEMultipart("alternative")
    message["Subject"] = email_config['subject']
    message["From"] = email_config['from']
    message["To"] = ", ".join(get_email_list())  # Use the dynamic list
    msg_body = MIMEText(report, "html")
    message.attach(msg_body)
    
    server = None
    try:
        server = smtplib.SMTP(email_config['server'])
        server.sendmail(email_config['from'], email_config['to'], message.as_string())
        logger.info("Email sent successfully to {}".format(email_config['to']))
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")
        raise Exception("Failed to send email due to SMTP issue.") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exception("An unexpected error occurred when sending an email.") from e
    finally:
        if server:
            try:
                server.quit()
            except smtplib.SMTPServerDisconnected:
                pass  # Connection was already closed

