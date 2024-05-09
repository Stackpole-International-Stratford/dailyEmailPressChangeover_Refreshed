# src/data/db.py

from datetime import timedelta
import os


db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': 'prod_mon',
    'raise_on_warnings': True
}