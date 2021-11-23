import re
import sys
from datetime import datetime, timedelta
import mysql.connector
import jinja2

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.debug("Running")

email_config = {
    'server': 'mesg06.stackpole.ca',
    'from': 'cstrutton@stackpole.com',
    'to': [
        'dbrenneman@stackpole.com',
        'rzylstra@stackpole.com',
        'dmilne@stackpole.com',
        'lbaker@stackpole.com',
        'jmcmaster@stackpole.com',
        'roberto.jimenez@vantage-corp.com',
        'cstrutton@stackpole.com',
    ],
    'subject': 'AB1V Autogauge scrap report'
}

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': 'prod_mon',
    'raise_on_warnings': True
}


def get_part_list(range_start, range_end=None):
    if not range_end:
        range_end = range_start + timedelta(hours=24)
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    query = ("SELECT DISTINCT part_number FROM 1730_Vantage "
             "WHERE created_at BETWEEN %s AND %s")

    cursor.execute(query, (range_start, range_end))
    parts = []
    for row in cursor:
        # print(row[0])
        parts.append(row[0])

    cursor.close()
    cnx.close()
    return parts


def good_part_count(part_number, start_date, end_date):
    if not end_date:
        end_date = start_date + timedelta(hours=24)
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    query = ("SELECT COUNT(*) FROM 1730_Vantage "
             "WHERE part_number = %s "
             "AND part_fail = 1 "
             "AND (created_at BETWEEN %s AND %s)")

    cursor.execute(query, (part_number, start_date, end_date))
    res = cursor.fetchone()

    cursor.close()
    cnx.close()

    return res[0]


def shift_times(date, date_offset=0):
    # end_date is this morning at 7am
    end_date = date.replace(hour=7, minute=0, second=0, microsecond=0)
    # adjust end_date by date_offset days
    end_date = end_date - timedelta(days=date_offset)
    # start_date is yesterday morning at 7am
    start_date = end_date - timedelta(hours=24)
    end_date = end_date - timedelta(seconds=1)
    return start_date, end_date


def reject_part_count(part_number, start_date, end_date):
    # initialize empty results object
    results = {
        'spotface': {'label': 'Spot Face', 'count': 0},
        'media': {'label': 'Media', 'count': 0},
        'oilholes': {'label': 'Oil Holes', 'count': 0},
        'induction': {'label': 'Induction', 'count': 0},
        'balpos': {'label': 'Balance Pos', 'count': 0},
        'balwitness': {'label': 'Bal Witness Mark', 'count': 0},
        'winheight': {'label': 'Window Height', 'count': 0},
        'staking': {'label': 'Staking Pocket', 'count': 0},
        'pocketholes': {'label': 'Mach Pocket Holes', 'count': 0},
        'eddy': {'label': 'Eddy Current', 'count': 0},
        'res': {'label': 'Resonance', 'count': 0},
        'plateph': {'label': 'Plate PH', 'count': 0},
        'pedph': {'label': 'Ped PH', 'count': 0},
        'bushid': {'label': 'Bush ID', 'count': 0},
        'upid': {'label': 'Upper ID', 'count': 0},
        'lowerid': {'label': 'Lower ID', 'count': 0},
        'other': {'label': 'Other', 'count': 0}
    }

    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    query = ("SELECT inspection_data FROM 1730_Vantage "
             "WHERE part_number = %s "
             "AND part_fail = 2 "
             "AND (created_at BETWEEN %s AND %s)")

    cursor.execute(query, (part_number, start_date, end_date))

    for row in cursor:
        features = re.split(r'\t+', row[0])
        try:
            failure = features.index("FAIL")
        except ValueError:
            failure = -1

        if failure == 8:
            results['spotface']['count'] += 1

        elif failure == 5:
            results['media']['count'] += 1
        elif failure == 8:
            results['media']['count'] += 1
        elif failure == 12:
            results['media']['count'] += 1
        elif failure == 14:
            results['media']['count'] += 1
        elif 17 <= failure <= 21:
            results['media']['count'] += 1
        elif failure == 35:
            results['media']['count'] += 1

        elif failure == 6:
            results['oilholes']['count'] += 1
        elif failure == 9:
            results['oilholes']['count'] += 1

        elif failure == 10:
            results['induction']['count'] += 1

        elif failure == 11:
            results['balpos']['count'] += 1

        elif failure == 13:
            results['balwitness']['count'] += 1

        elif 21 <= failure <= 32:
            results['winheight']['count'] += 1

        elif failure == 34:
            results['staking']['count'] += 1

        elif failure == 36:
            results['pocketholes']['count'] += 1

        elif failure == 37:
            results['eddy']['count'] += 1

        elif failure == 38:
            results['res']['count'] += 1

        elif 39 <= failure <= 48:
            results['plateph']['count'] += 1

        elif 49 <= failure <= 58:
            results['pedph']['count'] += 1

        elif failure == 60:
            results['bushid']['count'] += 1

        elif failure == 62:
            results['upid']['count'] += 1

        elif failure == 64:
            results['lowerid']['count'] += 1

        else:
            results['other']['count'] += 1

    cursor.close()
    cnx.close()

    return results


def report_html(start, end):
    data = []
    part_list = get_part_list(start, end)
    for part in part_list:
        data.append({
            'part_number': part,
            'good': good_part_count(part, start, end),
            'reject': reject_part_count(part, start, end)
        })
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=''))
    template = env.get_template('template.html')
    return template.render(data=data, start=start, end=end)


@logger.catch
def main():
    offset = 0 if len(sys.argv) == 1 else int(sys.argv[1])
    start_time, end_time = shift_times(datetime.now(), offset)
    report = report_html(start_time, end_time)
    message = MIMEMultipart("alternative")
    message["Subject"] = email_config['subject']
    message["From"] = email_config['from']
    message["To"] = ", ".join(email_config['to'])
    msg_body = MIMEText(report, "html")
    message.attach(msg_body)
    server = smtplib.SMTP(email_config['server'])
    server.sendmail(email_config['from'], email_config['to'], message.as_string())
    server.quit()


if __name__ == '__main__':
    main()
