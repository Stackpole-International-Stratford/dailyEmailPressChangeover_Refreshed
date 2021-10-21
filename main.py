import re
from datetime import datetime, timedelta
import mysql.connector
import jinja2

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email_config = {
    'server': 'mesg06.stackpole.ca',
    'from': 'cstrutton@stackpole.com',
    'to': [
        'cstrutton@stackpole.com',
        'dbrenneman@stackpole.com',
        'rzylstra@stackpole.com',
        'dmilne@stackpole.com',
        'lbaker@stackpole.com',
        'roberto.jimenez@vantage-corp.com'],
    'subject': 'AB1V Autogauge scrap report'
}

db_config = {
    'user': 'prodmon',
    'password': 'pm258',
    'host': '10.4.1.245',
    'port': 6601,
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


def shift_times(date):
    # end_date is this morning at 7am
    end_date = date.replace(hour=7, minute=0, second=0, microsecond=0)
    # start_date is yesterday morning at 7am
    start_date = end_date - timedelta(hours=24)
    end_date = end_date - timedelta(seconds=1)
    return start_date, end_date


def reject_part_count(part_number, start_date, end_date):
    # initialize empty results object
    results = {
        'balance hole': 0,
        'eddy': 0,
        'resonance': 0,
        'plate ph': 0,
        'ped ph': 0,
        'laser grade': 0,
        'bushing id': 0,
        'window height': 0,
        'lube holes': 0,
        'staking pocket': 0,
        'pinion cross hole': 0,
        'spot face': 0,
        'stuck media': 0,
        'upper lower id': 0,
        'pre existing barcode': 0,
        'other': 0
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

        if 11 <= failure <= 13:
            results['balance hole'] += 1

        elif failure == 37:
            results['eddy'] += 1

        elif failure == 38:
            results['resonance'] += 1

        elif 39 <= failure <= 48:
            results['Plate PH'] += 1

        elif 49 <= failure <= 58:
            results['Ped PH'] += 1

        elif 65 <= failure <= 68:
            results['laser grade'] += 1

        elif 59 <= failure <= 60:
            results['busing id'] += 1

        elif 21 <= failure <= 32:
            results['window height'] += 1

        elif failure == 34:
            results['staking pocket'] += 1

        elif failure == 9:
            results['pinion cross hole'] += 1

        elif failure == 8:
            results['spot face'] += 1

        elif 61 <= failure <= 64:
            results['upper lower id'] += 1

        elif 14 <= failure <= 20:
            results['stuck media'] += 1
        elif failure == 5:
            results['stuck media'] += 1
        elif failure == 7:
            results['stuck media'] += 1
        elif failure == 12:
            results['stuck media'] += 1

        else:
            results['other'] += 1

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


if __name__ == '__main__':

    start_time, end_time = shift_times(datetime.now())
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
