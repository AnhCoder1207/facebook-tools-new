import logging
import random
import time
from datetime import datetime

import pymongo

import sqlalchemy as db
import pandas as pd
# create logger with 'spam_application'
from pymongo import MongoClient

# from models import scheduler_video, joining_group, connection, via_share

logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log', encoding="UTF-8")
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

client = MongoClient("mongodb://localhost:27017")
mongo_client = client['minh']
videos_table = mongo_client['videos']
scheduler_table = mongo_client['scheduler_table']
via_share = mongo_client['via_share']
joining_group = mongo_client['joining_group']
group_auto_approved = mongo_client['group_auto_approved']


def mapping_table(item):
    return [
        item.get('video_id', ''),
        item.get('share_number', 0),
        item.get('shared', False),
        item.get('go_enable', False),
        item.get('co_khi_enable', False),
        item.get('xay_dung_enable', False),
        item.get('options_enable', False),
    ]


def mapping_via_table(item):
    current_date = str(datetime.date(datetime.now()))
    if item.get('date', '') == current_date:
        share_number = item.get('share_number', '')
    else:
        share_number = 0
    # # 'id', 'password', '2fa', "email", "email password", "proxy", "status"
    return [
        item.get('fb_id', ''),
        item.get('password', ''),
        item.get('mfa', ''),
        item.get('email', ''),
        item.get('email_password', ''),
        item.get('proxy', ''),
        item.get('status', ''),
        share_number,
    ]


def get_scheduler_data():
    table_default = scheduler_table.find().sort("create_date", pymongo.ASCENDING)
    table_default = list(map(mapping_table, list(table_default)))
    return table_default


def get_group_joining_data(group_type):
    # results = connection.execute(
    #     db.select([joining_group]).where(joining_group.columns.group_type == group_type)).fetchall()
    # groups = [result.name for result in results if result.name.strip() != '']
    # data_group_join = "\n".join(groups)
    results = joining_group.find({"group_type": group_type})
    groups = [result.get("name") for result in results if result.get("name").strip() != '']
    data_group_join = "\n".join(groups)
    return data_group_join


def get_via_data():
    # results = connection.execute(db.select([via_share])).fetchall()
    # if len(results) == 0:
    #     return []
    # df = pd.DataFrame(results)
    # df.columns = results[0].keys()
    results = via_share.find().sort([("status", pymongo.DESCENDING), ("create_date", pymongo.DESCENDING)])
    table_default = list(map(mapping_via_table, list(results)))
    return table_default


def random_sleep(first_time=1, last_time=5):
    time.sleep(random.randint(first_time, last_time))


def validate_string(input_txt):
    if type(input_txt) is str:
        return ''.join(e for e in input_txt if (e.isalnum() or e == " " or e == '.'))
    return input_txt