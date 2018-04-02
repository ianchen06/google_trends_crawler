#!coding: utf-8
from pymongo import MongoClient

c = MongoClient(host='192.168.33.10')

dict_list = []
for doc in c.crawler.google_trends.find({}):
    print("[DEBUG] Processing %s"%doc.get('_id'))
    words = [word_dict['title'] for word_dict in doc.get('trendsList')]
    dict_list.extend(words)

with open('/tmp/custom_dict.txt', 'w') as f:
    for word in set(dict_list):
        f.write("%s 1 n\n"%word)

