__author__ = 'Shuo Yu'

import pymysql

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
FROM sy_trainset_1k_2_3
LIMIT %d
""" % max_records

cur.execute(sql)

arff = open("C:/trainset_1k_2_3.arff", "w")
port_list = [21, 23, 25, 80, 81, 82, 102, 110, 137, 143, 161, 443, 445, 465, 502, 631, 993, 995, 1023, 1434, 1471, 1604, 1723, 1900, 2067, 2121, 2323, 3128, 4022, 5000, 5060, 5560, 5632, 5900, 5984, 5985, 7071, 7777, 8080, 8089, 8098, 8129, 8443, 9000, 9151, 9200, 9944, 9981, 9999, 10000, 16010, 17988, 27017, 28017, 44818, 47808, 49152, 50100]

header = """@RELATION scadashodan

@ATTRIBUTE port {21, 23, 25, 80, 81, 82, 102, 110, 137, 143, 161, 443, 445, 465, 502, 631, 993, 995, 1023, 1434, 1471, 1604, 1723, 1900, 2067, 2121, 2323, 3128, 4022, 5000, 5060, 5560, 5632, 5900, 5984, 5985, 7071, 7777, 8080, 8089, 8098, 8129, 8443, 9000, 9151, 9200, 9944, 9981, 9999, 10000, 16010, 17988, 27017, 28017, 44818, 47808, 49152, 50100}
@ATTRIBUTE length INTEGER
@ATTRIBUTE num_grams INTEGER
@ATTRIBUTE num_gen_uni_top100 INTEGER
@ATTRIBUTE num_gen_bi_top100 INTEGER
@ATTRIBUTE num_gen_tri_top100 INTEGER
@ATTRIBUTE num_port_uni_top100 INTEGER
@ATTRIBUTE num_port_bi_top100 INTEGER
@ATTRIBUTE num_port_tri_top100 INTEGER
@ATTRIBUTE is_scada {0, 1}

@DATA
"""

arff.write(header)

for row in cur:
    port = row[2] if int(row[2]) in port_list else "?"
    length = row[3]
    num_grams = row[4]
    n1 = row[5]
    n2 = row[6]
    n3 = row[7]
    n4 = row[8] if row[8] != -1 else "?"
    n5 = row[9] if row[8] != -1 else "?"
    n6 = row[10] if row[8] != -1 else "?"
    is_scada = row[1]

    arff.write("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}\n".format(
        port, length, num_grams, n1, n2, n3, n4, n5, n6, is_scada))
