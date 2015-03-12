__author__ = 'Hongyi'

import pymysql

db = pymysql.connect(host="128.196.27.147", # your host, usually localhost
                     user="ShodanTeam", # your username
                     passwd="Sh0d@n7e", # your password
                     db="shodan",
                     charset='utf8',
                     autocommit=True)# name of the data base

cur = db.cursor()

f = open(r"D:/hospital.txt", "r")

for line in f.readlines():
    name = line.split("\t")[0].replace("'", "\\'")
    url = line.split("\t")[1]
    ip = line.split("\t")[2].replace("\n", "")
    sql = """INSERT INTO `shodan`.`hospital_data` (`hospitalname`, `hospitalurl`, `hospitalip`) VALUES ('%s', '%s', '%s');""" % (name, url, ip)
    cur.execute(sql)
    print(sql)

f.close()
cur.close()
db.close()