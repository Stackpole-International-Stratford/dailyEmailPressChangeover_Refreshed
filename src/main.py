import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jinja2
from utils.email_utils import send_email, load_email_config
from utils.report_utils import shift_times, get_report_data, render_report
from utils.logging_utils import setup_logger
import traceback

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'example.env')
load_dotenv(dotenv_path=dotenv_path)
logger = setup_logger()

start_hour = 6

def main():
    offset = 0 if len(sys.argv) == 1 else int(sys.argv[1])
    start_time, end_time = shift_times(datetime.now(), offset, start_hour)
    data = get_report_data(start_time, end_time)
    report = render_report(data, start_time, end_time)
    
    email_config = load_email_config()
    send_email(report, email_config)
    
    logger.info("Report processing and email sending completed successfully.")

if __name__ == '__main__':
    main()
