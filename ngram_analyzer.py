__author__ = 'Shuo Yu'

# This script analyze the device data field and tokenize it into continuous alphabets and/or numbers.
# It further analyzes the occurrences for each unigram, bigram and trigram.
# Current version deals with scada/non-scada devices, providing overall and port-specific n-grams statistic.
# Output txt file paths can be configured in scada_log and non_log.
# Results are inserted into db using insert_into_database flag.
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

insert_into_database = True
top_n = 30
port_device_threshold = 0
scada_specific_top_n = 100
log_scada = "C:/log_scada.txt"
log_non = "C:/log_non.txt"
log_compare = "C:/log_compare.txt"
record_num_scada = 100000
record_num_non = 100000

# setting skip_factor to 0 will prevent the script from skipping
# db_suffix is used to use a different db
skip_factor = 3
db_suffix = "_2_3"

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
    portnum = str(row[0])
    for ngram_port_dict in ngram_port_dicts_scada:
        ngram_port_dict[portnum] = {}
    for ngram_port_dict in ngram_port_dicts_non:
        ngram_port_dict[portnum] = {}
    port_count_non[portnum] = 0
    port_count_scada[portnum] = 0

print("len(ngram_port_dicts_scada[0]) = {0}".format(len(ngram_port_dicts_scada[0])))

sql1b = """
SELECT DISTINCT portnum
FROM shodan.nonscadashodan
LIMIT 0, 1000
"""
cur.execute(sql1b)

for row in cur:
    portnum = str(row[0])
    for ngram_port_dict in ngram_port_dicts_scada:
        ngram_port_dict[portnum] = {}
    for ngram_port_dict in ngram_port_dicts_non:
        ngram_port_dict[portnum] = {}
    port_count_non[portnum] = 0
    port_count_scada[portnum] = 0
## </port_info>


# ================ FOR SCADA DEVICES =================
# select the first record_num_scada records from scadashodan: the devicedata, port number
sql2 = """
SELECT portnum, devicedata
FROM shodan.scadashodan
LIMIT 0, %d
""" % record_num_scada
cur.execute(sql2)

counter = 0
# Tokenizing
for row in cur:
    counter += 1

    # reserve record No. skip_factor, ... , skip_factor * n for test
    if skip_factor != 0 and counter % skip_factor == 0:
        continue

    port = str(row[0])
    dict_inc(port_count_scada, port)

    data = row[1]

    lst = []
    newlst = []

    lst = sep.split(data)
    for s in lst:
        if len(s) != 0:
            newlst.append(s.lower())

    # this list contains all the grams in the data field. E.g., ["http", "1", "1"]
    lenlst = len(newlst)

    # Summarizing the occurrences for each unigram, bigram and trigram
    for i in range(lenlst):
        gram[0] = newlst[i]
        dict_inc(ngram_dicts_scada[0], gram[0])
        dict_inc(ngram_port_dicts_scada[0][port], gram[0])
        if i + 1 < lenlst:
            gram[1] = "".join((gram[0], "_", newlst[i + 1]))
            dict_inc(ngram_dicts_scada[1], gram[1])
            dict_inc(ngram_port_dicts_scada[1][port], gram[1])
        if i + 2 < lenlst:
            gram[2] = "".join((gram[1], "_", newlst[i + 2]))
            dict_inc(ngram_dicts_scada[2], gram[2])
            dict_inc(ngram_port_dicts_scada[2][port], gram[2])

log = open(log_scada, "w")

# provides overall statistics
# each element in sorted_list_scada is a list, containing tuples converted from ngram_dicts_scada, desc.
# sample of each element: [("1", 9000), ("http", 8500)]
sorted_list_scada = [None, None, None]
for i in range(3):
    sorted_list_scada[i] = sorted(ngram_dicts_scada[i].items(), key=operator.itemgetter(1))
    sorted_list_scada[i].reverse()

for i in range(3):
    sorted_dict = sorted_list_scada[i]
    log.write("======== Overall {0}-gram statistics ========\n".format(i + 1))
    for j in range(top_n if len(sorted_dict) > top_n else len(sorted_dict)):
        tup = sorted_dict[j]
        log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
    log.write("\n")
log.write("\n")

# provides port-specific statistics
sorted_port_list_scada = [None, None, None]
for i in range(3):
    sorted_port_list_scada[i] = sorted(ngram_port_dicts_scada[i].items(), key=operator.itemgetter(0))

for i in range(3):
    # sorted_port = [("21", {"ftp": 8000, "0": 7500}), ("80", {"http": 9000, "1": 8500})]
    sorted_port = sorted_port_list_scada[i]
    log.write("======== Port-specific {0}-gram statistics ========\n".format(i + 1))
    for port, item in sorted_port:
        # if the number of devices using a specific port is less than port_device_threshold, it will be ignored
        if port_count_scada[port] > port_device_threshold:
            log.write("Port {0}: {1} devices\n".format(port, port_count_scada[port]))
            sorted_item = sorted(item.items(), key=operator.itemgetter(1))
            sorted_item.reverse()
            for j in range(top_n if len(item) > top_n else len(item)):
                tup = sorted_item[j]
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

counter = 0
for row in cur:
    counter += 1
    # reserve record No. skip_factor, ... , skip_factor * n for test
    if skip_factor != 0 and counter % skip_factor == 0:
        continue

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
sorted_list_non = [None, None, None]
for i in range(3):
    sorted_list_non[i] = sorted(ngram_dicts_non[i].items(), key=operator.itemgetter(1))
    sorted_list_non[i].reverse()

for i in range(3):
    sorted_dict = sorted_list_non[i]
    log.write("======== Overall {0}-gram statistics ========\n".format(i + 1))
    for j in range(top_n if len(sorted_dict) > top_n else len(sorted_dict)):
        tup = sorted_dict[j]
        log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
    log.write("\n")
log.write("\n")

# provides port-specific statistics
sorted_port_list_non = [None, None, None]
for i in range(3):
    sorted_port_list_non[i] = sorted(ngram_port_dicts_non[i].items(), key=operator.itemgetter(0))

for i in range(3):
    # sorted_port = [("21", {"ftp": 8000, "0": 7500}), ("80", {"http": 9000, "1": 8500})]
    sorted_port = sorted_port_list_non[i]
    log.write("======== Port-specific {0}-gram statistics ========\n".format(i + 1))
    for port, item in sorted_port:
        # if the number of devices using a specific port is less than port_device_threshold, it will be ignored
        if port_count_non[port] > port_device_threshold:
            log.write("Port {0}: {1} devices\n".format(port, port_count_non[port]))
            sorted_item = sorted(item.items(), key=operator.itemgetter(1))
            sorted_item.reverse()
            for j in range(top_n if len(item) > top_n else len(item)):
                tup = sorted_item[j]
                log.write("\t{0}: {1}\n".format(tup[0], tup[1]))
log.close()


# ================ FOR COMPARISON BETWEEN SCADA AND NON-SCADA DEVICES =================

port_count_sql = """
INSERT INTO sy_device_port_count (port, scada, nonscada)
VALUES ('%s', '%s', '%s')
"""

ngrams_sql = """
INSERT INTO sy_scada_port_ngrams{0} (port, type, word, count)
VALUES ('%s', '%s', '%s', '%s')
""".format(db_suffix)

ngrams_non_sql = """
INSERT INTO sy_nonscada_port_ngrams{0} (port, type, word, count)
VALUES ('%s', '%s', '%s', '%s')
""".format(db_suffix)

log = open(log_compare, "w")

freq_scada = [None, None, None]
freq_non = [None, None, None]
freq_scada_only_dicts = [{}, {}, {}]
freq_non_only_dicts = [{}, {}, {}]

# figure out the grams used only by scada and non-scada devices
for i in range(3):
    freq_scada[i] = sorted_list_scada[i][:scada_specific_top_n]
    freq_non[i] = sorted_list_non[i][:scada_specific_top_n]
    freq_scada_only_dicts[i] = {}
    freq_non_only_dicts[i] = {}

    temp_non_list = [j[0] for j in freq_non[i]]
    temp_scada_list = [j[0] for j in freq_scada[i]]
    for gram in temp_scada_list:
        if gram not in temp_non_list:
            freq_scada_only_dicts[i][gram] = ngram_dicts_scada[i][gram]
    for gram in temp_non_list:
        if gram not in temp_scada_list:
            freq_non_only_dicts[i][gram] = ngram_dicts_non[i][gram]

sorted_freq_scada_only_list = [None, None, None]
sorted_freq_non_only_list = [None, None, None]

# output the results to txt files and db (optional)
for i in range(3):
    sorted_freq_scada_only_list[i] = sorted(freq_scada_only_dicts[i].items(), key=operator.itemgetter(1))
    sorted_freq_scada_only_list[i].reverse()
    sorted_freq_non_only_list[i] = sorted(freq_non_only_dicts[i].items(), key=operator.itemgetter(1))
    sorted_freq_non_only_list[i].reverse()

for i in range(3):
    sorted_freq_scada_only = sorted_freq_scada_only_list[i]
    log.write("======== Overall scada-only {0}-gram statistics ========\n".format(i + 1))
    for key, value in sorted_freq_scada_only:
        log.write("\t{0}: {1}\n".format(key, item))
        if insert_into_database:
            try:
                cur.execute(ngrams_sql % (-1, (i+1), key, value))
            except:
                pass
    log.write("\n")

for i in range(3):
    sorted_freq_non_only = sorted_freq_non_only_list[i]
    log.write("======== Overall nonscada-only {0}-gram statistics ========\n".format(i + 1))
    for key, value in sorted_freq_non_only:
        log.write("\t{0}: {1}\n".format(key, item))
        if insert_into_database:
            try:
                cur.execute(ngrams_non_sql % (-1, (i+1), key, value))
            except:
                pass
    log.write("\n")

# port-specific
freq_scada_port = [{}, {}, {}]
freq_non_port = [{}, {}, {}]
freq_scada_only_dicts_port = [{}, {}, {}]
freq_non_only_dicts_port = [{}, {}, {}]

# figure out port-specific grams used only by scada and non-scada devices
for i in range(3):
    # temp_dict = {"80": {"http": 8000, "1": 7500}, "21": {"ftp": 7500}}
    for port in ngram_port_dicts_scada[i].keys():
        # port_dict = {"http": 8000, "1": 7500}
        # port_dict_list = [("http", 8000), ("1", 7500)]
        temp_list = sorted(ngram_port_dicts_scada[i][port].items(), key=operator.itemgetter(1))
        temp_list.reverse()
        freq_scada_port[i][port] = temp_list[:]

for i in range(3):
    # temp_dict = {"80": {"http": 8000}, "21": {"ftp": 7500}}
    for port in ngram_port_dicts_non[i].keys():
        # port_dict_list = [("http", 8000)]
        temp_list = sorted(ngram_port_dicts_non[i][port].items(), key=operator.itemgetter(1))
        temp_list.reverse()
        freq_non_port[i][port] = temp_list[:]

for i in range(3):
    for port in freq_scada_port[i].keys():
        freq_port_scada_list = freq_scada_port[i][port][:scada_specific_top_n]
        freq_port_non_list = freq_non_port[i][port][:scada_specific_top_n]
        freq_scada_only_dicts_port[i][port] = {}
        freq_non_only_dicts_port[i][port] = {}

        temp_non_list = [j[0] for j in freq_port_non_list]
        temp_scada_list = [j[0] for j in freq_port_scada_list]
        for gram in temp_scada_list:
            if gram not in temp_non_list:
                freq_scada_only_dicts_port[i][port][gram] =\
                    ngram_port_dicts_scada[i][port][gram]
        for gram in temp_non_list:
            if gram not in temp_scada_list:
                freq_non_only_dicts_port[i][port][gram] =\
                    ngram_port_dicts_non[i][port][gram]

# output the port-specific results to txt files and db (optional)
sorted_freq_port_scada_only_list = [None, None, None]
sorted_freq_port_non_only_list = [None, None, None]

for i in range(3):
    sorted_freq_port_scada_only_list[i] = sorted(freq_scada_only_dicts_port[i].items(), key=operator.itemgetter(0))
    sorted_freq_port_non_only_list[i] = sorted(freq_non_only_dicts_port[i].items(), key=operator.itemgetter(0))

for i in range(3):
    sorted_freq_port_scada_only = sorted_freq_port_scada_only_list[i]
    log.write("======== Port-specific scada-only {0}-gram statistics ========\n".format(i + 1))
    for port, port_dict in sorted_freq_port_scada_only:
        log.write("Port {0}, with {1} scada devices and {2} non-scada devices\n".format(
            port, port_count_scada[port], port_count_non[port]
        ))
        if insert_into_database:
            try:
                cur.execute(port_count_sql % (port, port_count_scada[port], port_count_non[port]))
            except:
                pass

        sorted_port_list = sorted(port_dict.items(), key=operator.itemgetter(1))
        sorted_port_list.reverse()
        for key, value in sorted_port_list:
            log.write("\t{0}: {1}\n".format(key, value))
            if insert_into_database:
                try:
                    cur.execute(ngrams_sql % (port, (i+1), key, value))
                except:
                    pass
        log.write("\n")

    log.write("======== Port-specific nonscada-only {0}-gram statistics ========\n".format(i + 1))
    sorted_freq_port_non_only = sorted_freq_port_non_only_list[i]
    for port, port_dict in sorted_freq_port_non_only:
        log.write("Port {0}, with {1} scada devices and {2} non-scada devices\n".format(
            port, port_count_scada[port], port_count_non[port]
        ))

        sorted_port_list = sorted(port_dict.items(), key=operator.itemgetter(1))
        sorted_port_list.reverse()
        for key, value in sorted_port_list:
            log.write("\t{0}: {1}\n".format(key, value))
            if insert_into_database:
                try:
                    cur.execute(ngrams_non_sql % (port, (i+1), key, value))
                except:
                    pass
        log.write("\n")
log.close()
