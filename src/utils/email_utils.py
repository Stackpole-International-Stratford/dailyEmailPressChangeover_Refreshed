# src/utils/email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logging_utils import setup_logger
import os

logger = setup_logger()

def get_email_list():
    # Fetch the email list from the environment variable, split by comma
    email_list = os.getenv('EMAIL_LIST', '').split(',')
    return email_list

def send_email(report, email_config):
    # """
    # Send an email with a report as HTML content using SMTP configuration provided.
    
    # Parameters:
    # report (str): The HTML content of the report to be sent.
    # email_config (dict): A dictionary containing SMTP configuration including server, sender, recipient(s), and subject.
    
    # Returns:
    # None
    
    # Raises:
    # Exception: If there's an issue with SMTP or an unexpected error occurs during email sending.
    # """
    message = MIMEMultipart("alternative")
    message["Subject"] = email_config['subject']
    message["From"] = email_config['from']
    message["To"] = ", ".join(get_email_list())  # Use the dynamic list
    msg_body = MIMEText(report, "html")
    message.attach(msg_body)
    
    # Try to connect to the SMTP server and send the email.
    try:
        server = smtplib.SMTP(email_config['server'])
        server.sendmail(email_config['from'], email_config['to'], message.as_string())
        server.quit()  # Ensure the connection is closed after sending the email.
        logger.info("Email sent successfully to {}".format(email_config['to']))
    except smtplib.SMTPException as e:
        # Log SMTP specific exceptions, e.g., authentication issues, connection refused.
        logger.error(f"Failed to send email: {e}")
        raise Exception("Failed to send email due to SMTP issue.") from e
    except Exception as e:
        # Log any other unexpected exceptions that may occur.
        logger.error(f"An unexpected error occurred: {e}")
        raise Exception("An unexpected error occurred when sending an email.") from e
    finally:
        # Ensure the server connection is closed even if an exception occurs.
        server.quit()

