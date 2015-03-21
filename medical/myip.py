__author__ = 'Hongyi'

import json
import pymysql
import hashlib
import time
from urllib.request import urlopen


def db_connection():
    return pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                                user="ShodanTeam",  # your username
                                passwd="Sh0d@n7e",  # your password
                                db="shodan",
                                charset='utf8',
                                autocommit=True).cursor()  # name of the data base

f = open("sample.json")
cur = db_connection()

api_url = "http://api.myip.ms"
api_id = "id17657"
api_key = "753573301-739817362-1975251929"

query = """
    SELECT DISTINCT hospitalip
    FROM hospital_data
    LIMIT 0, 150;
    """
cur.execute(query)
rs = cur.fetchall()

for record in rs:
    ip = record[0]
    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
    tempurl = "{0}/{1}/api_id/{2}/api_key/{3}/timestamp/{4}".format(api_url, ip, api_id, api_key, timestamp)
    signature = hashlib.md5(tempurl.encode('utf-8')).hexdigest()
    url = "{0}/{1}/api_id/{2}/api_key/{3}/signature/{4}/timestamp/{5}"\
        .format(api_url, ip, api_id, api_key, signature, timestamp)
    print(url)

for line in f.readlines():
    jstr = json.loads(line)
    print(json.dumps(jstr, indent=4, sort_keys=True))