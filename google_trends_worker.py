# coding: utf-8
import os
import sys
import datetime
import json

from celery import Celery
from pymongo import MongoClient
import pymongo
import requests

mongo_host = os.getenv('MONGO_HOST') or 'localhost'
rabbitmq_host = os.getenv('RABBITMQ_HOST') or 'localhost'
rabbitmq_username = os.getenv('RABBITMQ_USERNAME') or 'test'
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD') or 'test'

app = Celery('tasks', broker='pyamqp://%s:%s@%s//'%(rabbitmq_username,
                                                    rabbitmq_password,
                                                    rabbitmq_host))

@app.task
def get_google_trends(start_date, days):
    for day in range(1,days + 1):
        dump_json.delay(start_date, day)

@app.task
def dump_json(start_date, day):
    conn = MongoClient(host=mongo_host)

    dstr = (datetime.datetime.strptime(start_date,'%Y%m%d') - datetime.timedelta(days=day)).strftime("%Y%m%d")

    print("[DEBUG] Requesting %s"%dstr)
    url = "https://trends.google.com/trends/hottrends/hotItems"
    data = {
        "ajax": "1",
        "pn": "p12",
        "htd": dstr,
        "htv": "l"
    }

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "content-length": "32",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "origin": "https://trends.google.com",
        "pragma": "no-cache",
        "referer": "https://trends.google.com/trends/hottrends",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }

    resp = requests.post(url, data=data, headers=headers)
    data = resp.json()
    print("[INFO] %s"%data.get('oldestVisibleDate'))

    # conn.<db_name>.<table_name>.<operation>
    for row in data.get('trendsByDateList'):
        row['_id'] = row.get('date')
        try:
            res = conn.crawler.google_trends.insert(row)
            print("[INFO] Inserted id %s"%res)
        except pymongo.errors.DuplicateKeyError as e:
            print(e)
            res = conn.crawler.google_trends.update({'_id': row['_id']}, row)
            print("[INFO] %s exists, updating"%res)
