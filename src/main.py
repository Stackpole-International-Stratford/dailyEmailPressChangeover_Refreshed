"""
File: main.py
Description: This script processes report data for a specified time frame,
             generates a report using Jinja2 templates, and sends the report via email.
Date: Thursday May 23rd, 2024
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jinja2
from utils.email_utils import send_email, load_email_config
from utils.report_utils import shift_times, get_report_data, render_report
from utils.logging_utils import setup_logger
import traceback

# Load environment variables from a .env file located in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'example.env')
load_dotenv(dotenv_path=dotenv_path)

# Setup logger for logging information and errors
logger = setup_logger()

# Define the hour at which the shift starts
start_hour = 6

def main():
    """
    Main function to process the report and send it via email.
    """
    # Determine the offset for the report based on command-line arguments
    offset = 0 if len(sys.argv) == 1 else int(sys.argv[1])
    
    # Calculate the start and end times for the report based on the current time and offset
    start_time, end_time = shift_times(datetime.now(), offset, start_hour)
    
    # Retrieve report data for the calculated time frame
    data = get_report_data(start_time, end_time)
    
    # Render the report using Jinja2 templates
    report = render_report(data, start_time, end_time)
    
    # Load email configuration settings
    email_config = load_email_config()
    
    # Send the rendered report via email
    send_email(report, email_config)
    
    # Log a success message upon completion
    logger.info("Report processing and email sending completed successfully.")

if __name__ == '__main__':
    # Execute the main function if the script is run directly
    main()
