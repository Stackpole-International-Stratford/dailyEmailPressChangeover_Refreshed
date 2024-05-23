"""
File: email_utils.py
Description: This module provides utility functions for sending emails and loading email configuration settings.
Date: Thursday May 23rd, 2024
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logging_utils import setup_logger
import os

# Initialize the logger for this module
logger = setup_logger()

def load_email_config():
    """
    Load email configuration settings from environment variables.

    Returns:
        dict: Dictionary containing email configuration settings.
    """
    email_config = {
        'server': os.getenv('EMAIL_SERVER'),
        'from': os.getenv('EMAIL_FROM'),
        'to': os.getenv('EMAIL_LIST').split(','),  # Split list if multiple recipients
        'cc': os.getenv('EMAIL_CC_LIST').split(','),  # Split list if multiple CC recipients
        'subject': os.getenv('EMAIL_SUBJECT')
    }
    return email_config


def get_email_list():
    """
    Retrieve the list of email recipients from the environment variables.

    Returns:
        list: List of email addresses.
    """
    email_list = os.getenv('EMAIL_LIST', '').split(',')
    return email_list

def send_email(report, email_config):
    """
    Send an email with the provided report using the specified email configuration.

    Args:
        report (str): The report content to be sent in the email.
        email_config (dict): Dictionary containing email configuration settings.
    """
    # Create a MIME message object
    message = MIMEMultipart("alternative")
    message["Subject"] = email_config['subject']
    message["From"] = email_config['from']
    message["To"] = ", ".join(email_config['to'])  # Use the dynamic list
    message["Cc"] = ", ".join(email_config['cc'])  # Add CC recipients

    # Combine TO and CC recipients
    recipients = email_config['to'] + email_config['cc']

    # Attach the report as the email body
    msg_body = MIMEText(report, "html")
    message.attach(msg_body)
    
    server = None
    try:
        # Connect to the email server and send the email
        server = smtplib.SMTP(email_config['server'])
        server.sendmail(email_config['from'], recipients, message.as_string())
        logger.info("Email sent successfully to {}".format(recipients))
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")
        raise Exception("Failed to send email due to SMTP issue.") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exception("An unexpected error occurred when sending an email.") from e
    finally:
        # Ensure the server connection is properly closed
        if server:
            try:
                server.quit()
            except smtplib.SMTPServerDisconnected:
                pass  # Connection was already closed

