import logging
import random
from datetime import datetime

import pymongo

import sqlalchemy as db
import pandas as pd
# create logger with 'spam_application'
from pymongo import MongoClient

from models import scheduler_video, joining_group, connection, via_share

logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
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

client = MongoClient("mongodb://minh:ThinhMinh1234@45.77.38.64:27017/?authSource=minh")
mongo_client = client['minh']
videos_table = mongo_client['videos']
scheduler_table = mongo_client['scheduler_table']


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
    # # 'id', 'password', '2fa', "email", "email password", "proxy", "status"
    return [
        item.get('fb_id', ''),
        item.get('password', ''),
        item.get('mfa', ''),
        item.get('email', ''),
        item.get('email_password', ''),
        item.get('proxy', ''),
        item.get('status', ''),
    ]


def get_scheduler_data():
    table_default = scheduler_table.find(
        {
            "shared": False
        },
        {
            "video_id": 1,
            "groups_shared": 1,
            "shared": 1,
            "go_enable": 1,
            "co_khi_enable": 1,
            "xay_dung_enable": 1,
            "options_enable": 1,
        }
    ).sort("create_date", pymongo.ASCENDING)
    table_default = list(map(mapping_table, list(table_default)))
    return table_default


def get_group_joining_data(group_type):
    results = connection.execute(
        db.select([joining_group]).where(joining_group.columns.group_type == group_type)).fetchall()
    groups = [result.name for result in results if result.name.strip() != '']
    data_group_join = "\n".join(groups)
    return data_group_join


def get_via_data():
    results = connection.execute(db.select([via_share])).fetchall()
    if len(results) == 0:
        return []
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    table_default = list(map(mapping_via_table, df.to_dict(orient='records')))
    return table_default
