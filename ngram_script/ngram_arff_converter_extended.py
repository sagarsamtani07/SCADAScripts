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
FROM sy_filtered_trainset_1k_2_3
LIMIT %d
""" % max_records

cur.execute(sql)

arff = open("C:/trainset_extended_filtered_1k_2_3.arff", "w")
port_list_1 = [21, 23, 25, 80, 81, 102, 137, 161, 443, 445, 502, 1434, 5000, 8080, 44818, 47808]
port_list_2 = [21, 23, 25, 80, 81, 82, 83, 84, 110, 137, 143, 161, 443, 445, 993, 1234, 1900, 5000, 5060, 7777, 8080,
               8081, 8090, 8181, 8443, 10000]

port_list = port_list_1[:]
for item in port_list_2:
    if item not in port_list:
        port_list.append(item)

print(port_list)

header = """@RELATION scadashodan

@ATTRIBUTE port {21, 23, 25, 80, 81, 102, 137, 161, 443, 445, 502, 1434, 5000, 8080, 44818, 47808, 82, 83, 84, 110, 143, 993, 1234, 1900, 5060, 7777, 8081, 8090, 8181, 8443, 10000}
@ATTRIBUTE length INTEGER
@ATTRIBUTE num_grams INTEGER
@ATTRIBUTE num_gen_uni_top100 INTEGER
@ATTRIBUTE num_gen_bi_top100 INTEGER
@ATTRIBUTE num_gen_tri_top100 INTEGER
@ATTRIBUTE num_port_uni_top100 INTEGER
@ATTRIBUTE num_port_bi_top100 INTEGER
@ATTRIBUTE num_port_tri_top100 INTEGER
@ATTRIBUTE num_non_gen_uni_top100 INTEGER
@ATTRIBUTE num_non_gen_bi_top100 INTEGER
@ATTRIBUTE num_non_gen_tri_top100 INTEGER
@ATTRIBUTE num_non_port_uni_top100 INTEGER
@ATTRIBUTE num_non_port_bi_top100 INTEGER
@ATTRIBUTE num_non_port_tri_top100 INTEGER
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
    n5 = row[9] if row[9] != -1 else "?"
    n6 = row[10] if row[10] != -1 else "?"
    n7 = row[11]
    n8 = row[12]
    n9 = row[13]
    n10 = row[14] if row[14] != -1 else "?"
    n11 = row[15] if row[15] != -1 else "?"
    n12 = row[16] if row[16] != -1 else "?"
    is_scada = row[1]

    arff.write("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}\n".format(
        port, length, num_grams, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, is_scada))
