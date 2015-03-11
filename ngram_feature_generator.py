__author__ = 'Shuo Yu'

# This script fetches top-n grams from db and analyzes the occurrence of each gram for records to be tested.
# Port -1 indicates general top-n grams.

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

record_num_scada = 100000
maxnum = 100000
num_gen_gram = 1000
num_port_gram = 100
skip_factor = 3

cur = db_connect()
cur_write = db_connect()

sep = re.compile(r"\W")
scada_count = {}
nonscada_count = {}
ngram_dict = {}
ngram_non_dict = {}

sql = """
SELECT port, scada, nonscada
FROM shodan.sy_device_port_count
LIMIT 0, %d
""" % maxnum
cur.execute(sql)

for row in cur:
    scada_count[row[0]] = row[1]
    nonscada_count[row[0]] = row[2]

# Using sy_scada_port_grams_2_3, not the entire one

sql = """
SELECT port, type, word, count
FROM shodan.sy_scada_port_ngrams_extended_filtered_1k_2_3
ORDER BY count DESC
LIMIT 0, %d
""" % maxnum
cur.execute(sql)

# {80: [{"http": 9000, "80": 8500}, {}, {}]}

for row in cur:
    port = row[0]
    type = row[1]
    word = row[2]
    count = row[3]
    if port not in ngram_dict:
        ngram_dict[port] = [[], [], []]
    if int(port) == -1: # general grams, not port-specific
        if (len(ngram_dict[port][type - 1]) < num_gen_gram):
            ngram_dict[port][type - 1].append(word)
    else:
        if (len(ngram_dict[port][type - 1]) < num_port_gram):
            ngram_dict[port][type - 1].append(word)

sql = """
SELECT port, type, word, count
FROM shodan.sy_nonscada_port_ngrams_extended_filtered_1k_2_3
ORDER BY count DESC
LIMIT 0, %d
""" % maxnum
cur.execute(sql)

# {80: [{"http": 9000, "80": 8500}, {}, {}]}

for row in cur:
    port = row[0]
    type = row[1]
    word = row[2]
    count = row[3]
    if port not in ngram_non_dict:
        ngram_non_dict[port] = [[], [], []]
    if int(port) == -1: # general grams, not port-specific
        if (len(ngram_non_dict[port][type - 1]) < num_gen_gram):
            ngram_non_dict[port][type - 1].append(word)
    else:
        if (len(ngram_non_dict[port][type - 1]) < num_port_gram):
            ngram_non_dict[port][type - 1].append(word)


sql3 = """
INSERT INTO sy_filtered_trainset_1k_2_3 (searchID, is_scada, port, length, num_grams,
                         num_gen_uni_top100, num_gen_bi_top100, num_gen_tri_top100,
                         num_port_uni_top100, num_port_bi_top100, num_port_tri_top100,
                         num_non_gen_uni_top100, num_non_gen_bi_top100, num_non_gen_tri_top100,
                         num_non_port_uni_top100, num_non_port_bi_top100, num_non_port_tri_top100)
VALUES
                        ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                         '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
"""

# choose the records in scadashodan, extract features and insert into sy_testset
sql = """
SELECT searchID, portnum, devicedata
FROM shodan.scadashodan
LIMIT 0, %d
""" % record_num_scada
cur.execute(sql)

counter = 0
print("Begin scadashodan")
for row in cur:
    counter += 1

    # use record No. skip_factor, ... , skip_factor * n for test
    if skip_factor != 0 and counter % skip_factor == 0:
        continue

    id = row[0]
    port = int(row[1])
    data = row[2]

    lst = []
    newlst = []

    lst = sep.split(data)
    for s in lst:
        if len(s) != 0:
            newlst.append(s.lower())

    lenstr = len(data)
    lenlst = len(newlst)

    gram = [None, None, None]
    gen_gram_count = [0, 0, 0]
    port_gram_count = [0, 0, 0]

    non_gen_gram_count = [0, 0, 0]
    non_port_gram_count = [0, 0, 0]
    # summarize occurrence for each gram in the top-n lists
    # summarize occurrence for each gram in the top-n lists
    # if one port does not exist in our list, denote it as "-1".
    # "-1" should be handled and converted into "?" in the arff file.
    if int(port) in ngram_dict.keys():
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_dict[-1][0]:
                gen_gram_count[0] += 1
            if gram[0] in ngram_dict[port][0]:
                port_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_dict[-1][1]:
                    gen_gram_count[1] += 1
                if gram[1] in ngram_dict[port][1]:
                    port_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_dict[-1][2]:
                    gen_gram_count[2] += 1
                if gram[2] in ngram_dict[port][2]:
                    port_gram_count[2] += 1
    else: # the port does not exist in the list, set port_gram_count to -1
        for i in range(3):
            port_gram_count[i] = -1
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_dict[-1][0]:
                gen_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_dict[-1][1]:
                    gen_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_dict[-1][2]:
                    gen_gram_count[2] += 1
    if int(port) in ngram_non_dict.keys():
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_non_dict[-1][0]:
                non_gen_gram_count[0] += 1
            if gram[0] in ngram_non_dict[port][0]:
                non_port_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_non_dict[-1][1]:
                    non_gen_gram_count[1] += 1
                if gram[1] in ngram_non_dict[port][1]:
                    non_port_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_non_dict[-1][2]:
                    non_gen_gram_count[2] += 1
                if gram[2] in ngram_non_dict[port][2]:
                    non_port_gram_count[2] += 1
    else: # the port does not exist in the list, set non_port_gram_count to -1
        for i in range(3):
            non_port_gram_count[i] = -1
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_non_dict[-1][0]:
                non_gen_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_non_dict[-1][1]:
                    non_gen_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_non_dict[-1][2]:
                    non_gen_gram_count[2] += 1
    # write n-gram features for each record to db
    try:
        cur_write.execute(sql3 % (id, 1, port, lenstr, lenlst,
                          gen_gram_count[0], gen_gram_count[1], gen_gram_count[2],
                          port_gram_count[0], port_gram_count[1], port_gram_count[2],
                          non_gen_gram_count[0], non_gen_gram_count[1], non_gen_gram_count[2],
                          non_port_gram_count[0], non_port_gram_count[1], non_port_gram_count[2]
        ))
    except Exception as err:
        print("{0}: {1}".format(err, id))



# choose the records in nonscadashodan, extract features and insert into sy_testset
sql = """
SELECT searchID, portnum, devicedata
FROM shodan.nonscadashodan
LIMIT 0, %d
UNION
SELECT searchID, portnum, devicedata
FROM shodan.nonscadashodanmore
LIMIT 0, %d
""" % (record_num_scada, record_num_scada)
cur.execute(sql)

print("Begin nonscadashodan")
counter = 0
for row in cur:
    counter += 1

    # use record No. skip_factor, ... , skip_factor * n for test
    if skip_factor != 0 and counter % skip_factor == 0:
        continue

    id = row[0]
    port = int(row[1])
    data = row[2]

    lst = []
    newlst = []

    lst = sep.split(data)
    for s in lst:
        if len(s) != 0:
            newlst.append(s.lower())

    lenstr = len(data)
    lenlst = len(newlst)

    gram = [None, None, None]
    gen_gram_count = [0, 0, 0]
    port_gram_count = [0, 0, 0]
    non_gen_gram_count = [0, 0, 0]
    non_port_gram_count = [0, 0, 0]

    # summarize occurrence for each gram in the top-n lists
    # summarize occurrence for each gram in the top-n lists
    # if one port does not exist in our list, denote it as "-1".
    # "-1" should be handled and converted into "?" in the arff file.
    if int(port) in ngram_dict.keys():
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_dict[-1][0]:
                gen_gram_count[0] += 1
            if gram[0] in ngram_dict[port][0]:
                port_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_dict[-1][1]:
                    gen_gram_count[1] += 1
                if gram[1] in ngram_dict[port][1]:
                    port_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_dict[-1][2]:
                    gen_gram_count[2] += 1
                if gram[2] in ngram_dict[port][2]:
                    port_gram_count[2] += 1
    else: # the port does not exist in the list, set port_gram_count to -1
        for i in range(3):
            port_gram_count[i] = -1
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_dict[-1][0]:
                gen_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_dict[-1][1]:
                    gen_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_dict[-1][2]:
                    gen_gram_count[2] += 1
    if int(port) in ngram_non_dict.keys():
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_non_dict[-1][0]:
                non_gen_gram_count[0] += 1
            if gram[0] in ngram_non_dict[port][0]:
                non_port_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_non_dict[-1][1]:
                    non_gen_gram_count[1] += 1
                if gram[1] in ngram_non_dict[port][1]:
                    non_port_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_non_dict[-1][2]:
                    non_gen_gram_count[2] += 1
                if gram[2] in ngram_non_dict[port][2]:
                    non_port_gram_count[2] += 1
    else: # the port does not exist in the list, set non_port_gram_count to -1
        for i in range(3):
            non_port_gram_count[i] = -1
        for i in range(lenlst):
            gram[0] = newlst[i]
            if gram[0] in ngram_non_dict[-1][0]:
                non_gen_gram_count[0] += 1

            if i + 1 < lenlst:
                gram[1] = "".join((gram[0], "_", newlst[i + 1]))
                if gram[1] in ngram_non_dict[-1][1]:
                    non_gen_gram_count[1] += 1

            if i + 2 < lenlst:
                gram[2] = "".join((gram[1], "_", newlst[i + 2]))
                if gram[2] in ngram_non_dict[-1][2]:
                    non_gen_gram_count[2] += 1
    # write n-gram features for each record to db
    try:
        cur_write.execute(sql3 % (id, 0, port, lenstr, lenlst,
                          gen_gram_count[0], gen_gram_count[1], gen_gram_count[2],
                          port_gram_count[0], port_gram_count[1], port_gram_count[2],
                          non_gen_gram_count[0], non_gen_gram_count[1], non_gen_gram_count[2],
                          non_port_gram_count[0], non_port_gram_count[1], non_port_gram_count[2]
        ))
    except Exception as err:
        print("At counter {0}, id {1}, err: {2}".format(counter, id, err))
