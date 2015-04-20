__author__ = 'Hongyi'

import xml.etree.ElementTree as eTree
import pymysql


def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

db = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="shodan",
                     charset='utf8',
                     autocommit=True)  # name of the data base

cur = db.cursor()

ns = {'scap-core': "http://scap.nist.gov/schema/scap-core/0.1",
      'xsi': "http://www.w3.org/2001/XMLSchema-instance",
      'patch': "http://scap.nist.gov/schema/patch/0.1",
      'vuln': "http://scap.nist.gov/schema/vulnerability/0.4",
      'cvss': "http://scap.nist.gov/schema/cvss-v2/0.2",
      'cpe-lang': "http://cpe.mitre.org/language/2.0",
      'ns': "http://scap.nist.gov/schema/feed/vulnerability/2.0"}

tree = eTree.parse("nvdcve-2.0-2013.xml")
log = open("xml.log", "w")

root = tree.getroot()
entries = tree.findall('ns:entry', ns)

for entry in entries:
    # get cve_id
    cve_id = entry.findall('vuln:cve-id', ns)[0].text

    # get cvss_score
    try:
        cvss = entry.findall('vuln:cvss', ns)[0]
    except IndexError:
        log.write(cve_id + "\tNo Score\n")
        continue
    base_metrics = cvss.findall('cvss:base_metrics', ns)[0]
    cvss_score = base_metrics.findall('cvss:score', ns)[0].text

    # get product
    product_list = []
    try:
        products = entry.findall('vuln:vulnerable-software-list', ns)[0]
    except IndexError:
        log.write(cve_id + "\tNo Product\n")
        continue

    for product in products:
        string_split = product.text.split(":")
        try:
            vendor = str_replace(string_split[2]) if not (string_split[2] == "") else None
        except IndexError:
            vendor = None

        try:
            product_name = str_replace(string_split[3]) if not (string_split[3] == "") else None
        except IndexError:
            product_name = None

        try:
            version = str_replace(string_split[4]) if not (string_split[4] == "") else None
        except IndexError:
            version = None

        try:
            patch = str_replace(string_split[5]) if not (string_split[5] == "") else None
        except IndexError:
            patch = None

        try:
            platform = str_replace(string_split[6]) if not (string_split[6] == "") else None
        except IndexError:
            platform = None

        product_list.append([vendor, product_name, version, patch, platform])

    for item in product_list:
        sql = """
        INSERT INTO `shodan`.`nvdcve` (
        `cvd_id`, `vendor`, `product`, `version`, `patch`, `platform`, `score`
        ) VALUES (
        '%s', '%s', '%s', '%s', '%s', '%s', '%s'
        );""" % (cve_id, item[0], item[1], item[2], item[3], item[4], cvss_score)

        sql = sql.replace("'None'", "null")

        cur.execute(sql)
