# main script

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jinja2
from utils.email_utils import send_email, load_email_config
from utils.report_utils import shift_times, get_data, render_report
from utils.logging_utils import setup_logger
import traceback
import _mysql_connector

# relative path to the .env file from the current script location
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'example.env')
load_dotenv(dotenv_path=dotenv_path)
logger = setup_logger()







def main():
    #   """
    # Main function for orchestrating the generation of a report, rendering it as HTML, and sending it via email.
    # The function retrieves data within a specified time range, renders a report using the retrieved data,
    # and sends the report as an email using SMTP configuration. Any errors that occur during the process are logged.

    # Load email configuraiton from email_utils module
    email_config = load_email_config()

    # Extract the shift_times offset from command line arguments if provided, if there's no command line args then default to 0
    offset = 0 if len(sys.argv) == 1 else int(sys.argv[1])

    # Calculating start and end times based on current time and offset
    start_time, end_time = shift_times(datetime.now(), offset)

    # Format start and end times for display in email
    formatted_start_time = start_time.strftime("%Y-%m-%d %I:%M %p")
    formatted_end_time = end_time.strftime("%Y-%m-%d %I:%M %p")

    try:
        # Retrieving data based on formatted start and end times
        data = get_data(formatted_start_time, formatted_end_time)
        
        # Rendering report HTML using retrieved data and formatted times
        report_html = render_report(data, formatted_start_time, formatted_end_time)
        
        # Sending email with the generated report HTML and email configuration
        send_email(report_html, email_config)
        
        # Logging successful completion of report processing and email sending
        logger.info("Report processing and email sending completed successfully.")
        
    except Exception as e:
        # Handling any exceptions that occur during the main process and logging them
        logger.error(f"An error occurred in the main process: {e}")


if __name__ == '__main__':
    main()
