__author__ = 'Shuo Yu'

# This script analyze the device data field and tokenize it into continuous alphabets and/or numbers.
# It further analyzes the occurrences for each unigram, bigram and trigram.
# Current version deals with scada/non-scada devices, providing overall and port-specific n-grams statistic.
# Output txt file paths can be configured in scada_log and non_log.
# Current alphanumeric characters include ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789. Other characters are discarded.
# Stopwords are not used in this version.

import re
import pymysql
import operator


def dict_inc(_dict, _item):
    if _item not in _dict:
        _dict[_item] = 1
    else:
        _dict[_item] += 1


def db_connect():
    return pymysql.connect(host="128.196.27.147",
                           user="ShodanTeam",
                           passwd="Sh0d@n7e",
                           db="shodan",
                           charset='utf8',
                           autocommit=True).cursor()


# define seperators
sep = re.compile(r"\W")

## <init> initialize some variables
lst = []
newlst = []
gram = ["", "", ""]

# Config:
# scada_log, non_log: Output txt file paths
# top_n: The number of top-n grams that will be listed
# port_device_threshold: The threshold for the minimum number of devices for a particular port
# record_num_scada, record_num_non: The number of records that will be read from the db

top_n = 30
port_device_threshold = 10
log_scada = "C:/log_scada.txt"
log_non = "C:/log_non.txt"
log_compare = "C:/log_compare.txt"
record_num_scada = 10000
record_num_non = 10000

# this list contains 3 empty dicts for overall n-gram stats: [0]: gram[0] (aka uni), [1]: gram[1], [2]: gram[2]
# each dict contains a set of {word: count} pairs
ngram_dicts_scada = [{}, {}, {}]
ngram_dicts_non = [{}, {}, {}]

# this list contains 3 empty dicts for port-specific n-gram stats: [0]: gram[0], [1]: gram[1], [2]: gram[2]
# each dict contains a set of {port: word_dict} pairs, and each word_dict contains a set of {word: count} pairs
ngram_port_dicts_scada = [{}, {}, {}]
ngram_port_dicts_non = [{}, {}, {}]

# this dict counts the number of devices for each port
port_count_scada = {}
port_count_non = {}

# connect to the db, using config in db_connect() and get a cursor
cur = db_connect()

## </init>

## <port_info>
# select all the port numbers from the database
sql1 = """
SELECT DISTINCT portnum
FROM shodan.scadashodan
LIMIT 0, 1000
"""
cur.execute(sql1)

for row in cur:
    for ngram_port_dict in ngram_port_dicts_scada:
        ngram_port_dict[str(row[0])] = {}
    port_count_scada[str(row[0])] = 0

print("len(ngram_port_dicts_scada[0]) = {0}".format(len(ngram_port_dicts_scada[0])))

sql1b = """
SELECT DISTINCT portnum
FROM shodan.nonscadashodan
LIMIT 0, 1000
"""
cur.execute(sql1b)

for row in cur:
    for ngram_port_dict in ngram_port_dicts_non:
        ngram_port_dict[str(row[0])] = {}
    port_count_non[str(row[0])] = 0

## </port_info>


# ================ FOR SCADA DEVICES =================
# select the first record_num_scada records from scadashodan: the devicedata, port number
sql2 = """
SELECT portnum, devicedata
FROM shodan.scadashodan
LIMIT 0, %d
""" % record_num_scada
cur.execute(sql2)

for row in cur:
    port = str(row[0])
    dict_inc(port_count_scada, port)

    data = row[1]

    lst = []
    newlst = []

    lst = sep.split(data)
    for s in lst:
        if len(s) != 0:
            newlst.append(s.lower())

    lenlst = len(newlst)

    for i in range(lenlst):
        gram[0] = newlst[i]
        if i + 1 < lenlst:
            gram[1] = "".join((gram[0], "_", newlst[i + 1]))
        if i + 2 < lenlst:
            gram[2] = "".join((gram[1], "_", newlst[i + 2]))
        dict_inc(ngram_dicts_scada[0], gram[0])
        dict_inc(ngram_dicts_scada[1], gram[1])
        dict_inc(ngram_dicts_scada[2], gram[2])
        dict_inc(ngram_port_dicts_scada[0][port], gram[0])
        dict_inc(ngram_port_dicts_scada[1][port], gram[1])
        dict_inc(ngram_port_dicts_scada[2][port], gram[2])

log = open(log_scada, "w")

# provides overall statistics
sorted_list = [None, None, None]
for i in range(3):
    sorted_list[i] = sorted(ngram_dicts_scada[i].items(), key=operator.itemgetter(1))

for i in range(3):
    sorted_dict = sorted_list[i]
    log.write("======== Overall {0}-gram statistics ========\n".format(i + 1))
    for j in range(top_n if len(sorted_dict) > top_n else len(sorted_dict)):
        tup = sorted_dict[-(j + 1)]
        log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
    log.write("\n")
log.write("\n")

# provides port-specific statistics
sorted_port_list = [None, None, None]
for i in range(3):
    sorted_port_list[i] = sorted(ngram_port_dicts_scada[i].items(), key=operator.itemgetter(0))

for i in range(3):
    sorted_port = sorted_port_list[i]
    log.write("======== Port-specific {0}-gram statistics ========\n".format(i + 1))
    for key, item in sorted_port:
        # if the number of devices using a specific port is less than port_device_threshold, it will be ignored
        if port_count_scada[key] > port_device_threshold:
            log.write("Port {0}: {1} devices\n".format(key, port_count_scada[key]))
            sorted_item = sorted(item.items(), key=operator.itemgetter(1))
            for j in range(top_n if len(item) > top_n else len(item)):
                tup = sorted_item[-(j + 1)]
                log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
log.close()


# ================ FOR NON-SCADA DEVICES =================
# select the first record_num_non records from nonscadashodan: the devicedata, port number
sql2b = """
SELECT portnum, devicedata
FROM shodan.nonscadashodan
LIMIT 0, %d
""" % record_num_non
cur.execute(sql2b)

for row in cur:
    port = str(row[0])
    dict_inc(port_count_non, port)

    data = row[1]

    lst = []
    newlst = []

    lst = sep.split(data)
    for s in lst:
        if len(s) != 0:
            newlst.append(s.lower())

    lenlst = len(newlst)

    for i in range(lenlst):
        gram[0] = newlst[i]
        if i + 1 < lenlst:
            gram[1] = "".join((gram[0], "_", newlst[i + 1]))
        if i + 2 < lenlst:
            gram[2] = "".join((gram[1], "_", newlst[i + 2]))
        dict_inc(ngram_dicts_non[0], gram[0])
        dict_inc(ngram_dicts_non[1], gram[1])
        dict_inc(ngram_dicts_non[2], gram[2])
        dict_inc(ngram_port_dicts_non[0][port], gram[0])
        dict_inc(ngram_port_dicts_non[1][port], gram[1])
        dict_inc(ngram_port_dicts_non[2][port], gram[2])

log = open(log_non, "w")

# provides overall statistics
sorted_list = [None, None, None]
for i in range(3):
    sorted_list[i] = sorted(ngram_dicts_non[i].items(), key=operator.itemgetter(1))

for i in range(3):
    sorted_dict = sorted_list[i]
    log.write("======== Overall {0}-gram statistics ========\n".format(i + 1))
    for j in range(top_n if len(sorted_dict) > top_n else len(sorted_dict)):
        tup = sorted_dict[-(j + 1)]
        log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
    log.write("\n")
log.write("\n")

# provides port-specific statistics
sorted_port_list = [None, None, None]
for i in range(3):
    sorted_port_list[i] = sorted(ngram_port_dicts_non[i].items(), key=operator.itemgetter(0))

for i in range(3):
    sorted_port = sorted_port_list[i]
    log.write("======== Port-specific {0}-gram statistics ========\n".format(i + 1))
    for key, item in sorted_port:
        # if the number of devices using a specific port is less than port_device_threshold, it will be ignored
        if port_count_non[key] > port_device_threshold:
            log.write("Port {0}: {1} devices\n".format(key, port_count_non[key]))
            sorted_item = sorted(item.items(), key=operator.itemgetter(1))
            for j in range(top_n if len(item) > top_n else len(item)):
                tup = sorted_item[-(j + 1)]
                log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
log.close()


