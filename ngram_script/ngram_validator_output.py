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
SELECT *
FROM sy_testset_external3b
LIMIT %d
""" % max_records

sql2 = """
SELECT *
FROM sample3_shodan_2014_12_13
WHERE id = """

cur.execute(sql)

id_list = []

input = open("C:/analyze_log.txt", "r")
output = codecs.open("C:/analyze_log_output.txt", "w", "utf-8")

for row in cur:
    line = input.readline()
    signals = line.split()
    if signals[2] == "2:1":
        id_list.append(row[0])

for i in range(100):
    id = id_list[i]

    sql2 += str(id)
    if i != 99:
        sql2 += " or id = "
print(sql2)
exit(0)
    # cur.execute(sql2 + str(id))
    # for line in cur:
    #     ip = line[4]
    #     port = line[5]
    #     output.write("{0}\t{1}\t{2}\n".format(id, ip, port))

output.close()
