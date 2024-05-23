"""
File: report_utils.py
Description: This module provides utility functions for processing changeover reports,
             including fetching data from a MySQL database and rendering reports using Jinja2 templates.
Date: Thursday May 23rd, 2024
"""

from datetime import datetime, timedelta
from utils.logging_utils import setup_logger
import mysql.connector
import jinja2
import traceback
import os

# Initialize the logger for this module
logger = setup_logger()

# Define the hour at which the shift starts
start_hour = 6

def shift_times(date, date_offset=0, start_hour=6):
    """
    Calculate the start and end times for a reporting period based on the given date and offset.

    Args:
        date (datetime): The reference date.
        date_offset (int): Number of days to offset from the reference date.
        start_hour (int): The hour at which the shift starts.

    Returns:
        tuple: Start and end times for the reporting period.
    """
    # end_date is today at {start_hour}
    end_date = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    # adjust end_date by date_offset days
    end_date = end_date - timedelta(days=date_offset)
    # start_date is the day before at {start_hour}
    start_date = end_date - timedelta(hours=24)
    end_date = end_date - timedelta(seconds=1)
    return start_date, end_date

def completed_changeovers(start, end):
    """
    Fetch completed changeovers from the database within the specified time frame.

    Args:
        start (datetime): Start time of the reporting period.
        end (datetime): End time of the reporting period.

    Returns:
        list: List of dictionaries containing completed changeover records.
    """
    results = []
    db_config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': 'prodrptdb',
        # 'raise_on_warnings': True
    }
    with mysql.connector.connect(**db_config) as cnx:
        cursor = cnx.cursor()

        query = ("SELECT * FROM pr_downtime1 "
                 "WHERE priority = -2 "
                 "AND (completedtime BETWEEN %s AND %s)")

        cursor.execute(query, (start, end))

        for row in cursor:
            record = {
                'machine': row[0],
                'problem': row[1],
                'comments': row[8],
                'updatedtime': row[10],
                'completedtime': row[7],
                'changeovertime': row[15],
                'setupdelta': row[15] - row[10],
                'dialindelta': row[7] - row[15],
            }
            results.append(record)
    return results

def pending_changeovers(start, end):
    """
    Fetch pending changeovers from the database within the specified time frame.

    Args:
        start (datetime): Start time of the reporting period.
        end (datetime): End time of the reporting period.

    Returns:
        list: List of dictionaries containing pending changeover records.
    """
    results = []
    db_config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': 'prodrptdb',
        # 'raise_on_warnings': True
    }
    with mysql.connector.connect(**db_config) as cnx:
        cursor = cnx.cursor()

        query = "SELECT * FROM pr_downtime1 WHERE priority = -1;"

        cursor.execute(query)

        for row in cursor:
            record = {
                'machine': row[0],
                'problem': row[1],
                'called4helptime': row[2],
            }
            results.append(record)
    return results

def get_report_data(start, end):
    """
    Aggregate completed and pending changeover data for the report.

    Args:
        start (datetime): Start time of the reporting period.
        end (datetime): End time of the reporting period.

    Returns:
        dict: Dictionary containing the start and end times, completed changeover list, and pending changeover list.
    """
    pending_list = pending_changeovers(start, end)
    completed_list = completed_changeovers(start, end)
    data = {
        'start': start,
        'end': end,
        'completed_list': completed_list,
        'pending_list': pending_list,
    }
    return data

def render_report(data, start, end):
    """
    Render the report using Jinja2 templates.

    Args:
        data (dict): Dictionary containing the report data.
        start (datetime): Start time of the reporting period.
        end (datetime): End time of the reporting period.

    Returns:
        str: Rendered report as an HTML string.
    """
    try:
        # Get the directory path where this script is located
        current_directory = os.path.dirname(__file__)
        
        # Construct the path to the templates directory
        template_path = os.path.join(current_directory, '..', 'templates')

        # Load the template from the templates directory
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            extensions=["jinja2_humanize_extension.HumanizeExtension"]
        )
        template = env.get_template('template.html')
        return template.render(data=data, start=start, end=end)
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        traceback.print_exc()
        raise
