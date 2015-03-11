__author__ = 'Shuo Yu'

import pymysql
import codecs

def db_connect():
    return pymysql.connect(host="128.196.27.147",
                           user="ShodanTeam",
                           passwd="Sh0d@n7e",
                           db="shodan",
                           charset='utf8',
                           autocommit=True).cursor()

max_records = 1000000

cur = db_connect()

sql = """
SELECT searchid
FROM sy_filtered_testset_external4_1k_2_3
LIMIT %d
""" % max_records

cur.execute(sql)

sql2 = """
SELECT id, port
FROM sample4_shodan_2014_12_13
WHERE id = {0}"""

id_list = []

input = open("C:/analyze_log.txt", "r")
output = codecs.open("C:/analyze_log_output.txt", "w", "utf-8")

for row in cur:
    line = input.readline()
    signals = line.split()
    if signals[2] == "2:1":
        id_list.append(row[0])  # the id in db

for i in range(len(id_list)):
    id = id_list[i]
    if i % 10000 == 0:
        print(i)
#     sql2 += str(id)
#     if i != 99:
#         sql2 += " or id = "
# print(sql2)
# exit(0)
    cur.execute(sql2.format(id))
    for line in cur:
        port = line[1]
        output.write("{0}\t{1}\n".format(id, port))

output.close()
