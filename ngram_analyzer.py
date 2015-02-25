__author__ = 'Shuo Yu'

# This script analyze the device data field and tokenize it into continuous alphabets and/or numbers.
# It further analyzes the occurrences for each unigram, bigram and trigram.
# Current alphanumeric characters include ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789. Other characters are discarded.
# Stopwords are not used in this version.
# Sample

import json
import re


def dict_inc(d, item):
    if item not in d:
        d[item] = 1
    else:
        d[item] += 1

# define seperators
sep = re.compile(r"\W")

lst = []
newlst = []

uni_dict = {}
bi_dict = {}
tri_dict = {}

# this script is currently dealing with raw json files; could be modified to access to the db
with open("C:/latest10.txt", "r") as src:
    for line in src:
        print(line)
        json_obj = json.loads(line)
        data = json_obj["data"]
        lst = sep.split(data)
        print(lst)
        for s in lst:
            if len(s) != 0:
                newlst.append(s.lower())
        print(newlst)
    lenlst = len(newlst)

    for i in range(lenlst):
        uni = newlst[i]
        if i + 1 < lenlst:
            bi = "".join((uni, "_", newlst[i + 1]))
        if i + 2 < lenlst:
            tri = "".join((bi, "_", newlst[i + 2]))
        dict_inc(uni_dict, uni)
        dict_inc(bi_dict, bi)
        dict_inc(tri_dict, tri)

    for key, item in uni_dict.items():
        print("{0}: {1}".format(key, item))
    for key, item in bi_dict.items():
        print("{0}: {1}".format(key, item))
    for key, item in tri_dict.items():
        print("{0}: {1}".format(key, item))

