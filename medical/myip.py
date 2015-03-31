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

cur = db_connection()

# Hongyi's API: Used up
# api_id = "id17657"
# api_key = "753573301-739817362-1975251929"

# Sagar's API: Used up
# api_id = "id17704"
# api_key = "1810016131-841994778-423714404"

# Shuo's API: Used up
# api_id = "id17706"
# api_key = "1610597678-1954412878-1994905298"

# Sagar's API 2: Used up
# api_id = "id17873"
# api_key = "1884986588-1043917337-218347093"

# Shuo's API 2: Used up
# api_id = "id17874"
# api_key = "1930053096-59693597-80284299"

# Hongyi's API 2: Used up
# api_id = "id17875"
# api_key = "1554773148-1266496742-2034997215"

# Samantha's API: Unfortunately Wasted :(
# api_id = "id17877"
# api_key = "915862348-165079643-957050812"

# Hongyi's API3: Used up
api_id = "id17895"
api_key = "1060943727-1394130379-1020573296"

api_url = "http://api.myip.ms"

query = """
    SELECT DISTINCT hospitalip
    FROM hospital_data
    LIMIT 900, 150;
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

    str = urlopen(url).read().decode('utf-8')
    jsonstr = json.loads(str)

    json_file = open("myip_json/" + ip + ".json", "w")
    json_file.write(json.dumps(jsonstr, indent=4, sort_keys=True))
    json_file.close()

    time.sleep(2)

#
# file = raw_json.readline()
# jsonstr = json.loads(file)
# print(json.dumps(jsonstr))