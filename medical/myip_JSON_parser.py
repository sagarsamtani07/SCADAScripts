__author__ = 'Hongyi'

import os
import pymysql
import json
import math


def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def db_connection():
    return pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                                user="ShodanTeam",  # your username
                                passwd="Sh0d@n7e",  # your password
                                db="shodan",
                                charset='utf8',
                                autocommit=True).cursor()  # name of the data base

cur = db_connection()

errlog = open("errlog.txt", "w")

os.chdir("myip_json/")
for root, dir, files in os.walk("."):
    for file in files:
        f = open(file, "r").read()
        js = json.loads(f)
        f = json.dumps(js)
        js = json.loads(f)

        owner = js["owners"]["owner"]

        cidrs = owner["cidr"]
        range = owner["range"]
        range_size = owner["rangeSize"]
        owner_name = str_replace(owner["ownerName"])
        country_name = str_replace(owner["countryName"])
        address = str_replace(owner["address"])
        if cidrs == "":
            cidrs = range.split(" ")[0] + "/" + str(int(32 - math.log(int(range_size), 2)))

        for cidr in cidrs.split(", "):
            sql = """
            INSERT INTO `shodan`.`ip_owner` (
            `cidr`, `range`, `rangesize`, `ownername`, `country`, `address`
            ) VALUES (
            '%s', '%s', '%s', '%s', '%s', '%s'
            )""" % (cidr, range, range_size, owner_name, country_name, address)
            print(sql)
            try:
                cur.execute(sql)
            except Exception as err:
                errlog.write(str(err) + "\t" + cidr + "\n")

cur.close()
