from datetime import datetime, timedelta
from utils.logging_utils import setup_logger
import jinja2
import traceback
import os
import sys

logger = setup_logger()

def shift_times(date, date_offset=0):
    # """
    # Shifts the given date by a specified number of days and returns the start and end dates.

    # Parameters:
    # - date: The base date for shifting.
    # - date_offset (optional): The number of days to offset the date. Defaults to 0.

    # Returns:
    # - start_date: The start date after shifting.
    # - end_date: The end date after shifting.
    # """

    # end_date is this morning at 7am
    end_date = date.replace(hour=7, minute=0, second=0, microsecond=0)
    # adjust end_date by date_offset days
    end_date = end_date - timedelta(days=date_offset)
    # start_date is yesterday morning at 7am
    start_date = end_date - timedelta(hours=24)
    end_date = end_date - timedelta(seconds=1)
    return start_date, end_date




def get_data(start, end):
#   """
#     Retrieve data for report generation within the specified time range. This is where you would query the database for data, by replacing the dummy data with
#     an actual function to do so.
    
#     Parameters:
#     start (datetime): The start time for data retrieval.
#     end (datetime): The end time for data retrieval.
    
#      Returns:
#       - list: A list of dictionaries, each containing information about parts.
#         Each dictionary could have the following keys for example:
#         - 'part_number': The part number.
#         - 'good': The count of good parts.
#         - 'reject': A dictionary containing information about rejected parts.
#             Each key in the 'reject' dictionary corresponds to a type of rejection,
#             and its value is a dictionary containing the label and count of rejections.
#     Example:
#     [
#         {'part_number': '1234', 'good': 100, 'reject': {'spotface': {'label': 'Spot Face', 'count': 5}}},
#         {'part_number': '5678', 'good': 200, 'reject': {'media': {'label': 'Media', 'count': 3}}},
#         ...
#     ]
#     """   

    # Dummy data
    data = [
        {'part_number': '1234', 'good': 100, 'reject': {'spotface': {'label': 'Spot Face', 'count': 5}}},
        {'part_number': '5678', 'good': 200, 'reject': {'media': {'label': 'Media', 'count': 3}}},
        {'part_number': '2323', 'good': 300, 'reject': {}},
        {'part_number': '1234', 'good': 100, 'reject': {'spotface': {'label': 'Spot Face', 'count': 5}}},
        {'part_number': '5678', 'good': 200, 'reject': {'media': {'label': 'Media', 'count': 3}}},
        {'part_number': '2323', 'good': 300, 'reject': {}},
        {'part_number': '1234', 'good': 100, 'reject': {'spotface': {'label': 'Spot Face', 'count': 5}}},
        {'part_number': '5678', 'good': 200, 'reject': {}},
        {'part_number': '2323', 'good': 300, 'reject': {}},
        {'part_number': '1234', 'good': 100, 'reject': {'spotface': {'label': 'Spot Face', 'count': 5}}},
        {'part_number': '7889', 'good': 150, 'reject': {'burrs': {'label': 'Burrs', 'count': 2}}},
        {'part_number': '9988', 'good': 250, 'reject': {'warp': {'label': 'Warp', 'count': 1}}},
        {'part_number': '5467', 'good': 350, 'reject': {'crack': {'label': 'Crack', 'count': 4}}},
        {'part_number': '2143', 'good': 120, 'reject': {'spotface': {'label': 'Spot Face', 'count': 3}}},
        {'part_number': '8765', 'good': 220, 'reject': {'media': {'label': 'Media', 'count': 6}}},
        {'part_number': '3434', 'good': 330, 'reject': {'porosity': {'label': 'Porosity', 'count': 7}}},
        {'part_number': '1212', 'good': 140, 'reject': {'spotface': {'label': 'Spot Face', 'count': 8}}},
        {'part_number': '4545', 'good': 230, 'reject': {'deformation': {'label': 'Deformation', 'count': 5}}},
        {'part_number': '6767', 'good': 340, 'reject': {'paint': {'label': 'Paint Defect', 'count': 2}}},
        {'part_number': '8989', 'good': 160, 'reject': {'spotface': {'label': 'Spot Face', 'count': 1}}},
        {'part_number': '1010', 'good': 210, 'reject': {'media': {'label': 'Media', 'count': 3}}},
        {'part_number': '3232', 'good': 310, 'reject': {}},
        {'part_number': '5432', 'good': 190, 'reject': {'spotface': {'label': 'Spot Face', 'count': 6}}},
        {'part_number': '7865', 'good': 205, 'reject': {'crack': {'label': 'Crack', 'count': 2}}},
        {'part_number': '3498', 'good': 305, 'reject': {'media': {'label': 'Media', 'count': 5}}},
        {'part_number': '2124', 'good': 115, 'reject': {'spotface': {'label': 'Spot Face', 'count': 3}}},
        {'part_number': '5656', 'good': 225, 'reject': {'deformation': {'label': 'Deformation', 'count': 4}}},
        {'part_number': '7373', 'good': 335, 'reject': {'paint': {'label': 'Paint Defect', 'count': 1}}},
        {'part_number': '9191', 'good': 155, 'reject': {'spotface': {'label': 'Spot Face', 'count': 2}}},
    ]
    return data



def render_report(data, start, end):
    # """
    # Render a report HTML using Jinja2 templates based on the provided data, start time, and end time.
    # The function loads a template from the 'templates' directory, injects the data into the template,
    # and returns the rendered HTML content.
    
    # Parameters:
    # data (list of dict): The data to be included in the report, typically containing information about parts.
    # start (datetime): The start time for the report period.
    # end (datetime): The end time for the report period.
    
    # Returns:
    # str: The rendered HTML content of the report.
    
    # Raises:
    # jinja2.TemplateError: If there is an error during template rendering.
    # """
    try:
        # Get the directory path where main.py is located
        current_directory = os.path.dirname(__file__)
        
        # Construct the path to the templates directory
        template_path = os.path.join(current_directory, '..', 'templates')

        # Load the template from the templates directory
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        template = env.get_template('template.html')
        return template.render(data=data, start=start, end=end)
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        traceback.print_exc()
        raise