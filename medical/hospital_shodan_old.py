__author__ = 'Shuo Yu'

import shodan
import json
import time
import pymysql

def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def db_connect():
    return pymysql.connect(host="128.196.27.147",
                           user="ShodanTeam",
                           passwd="Sh0d@n7e",
                           db="shodan",
                           charset='utf8',
                           autocommit=True).cursor()


def ip_range_generator(cidr):
    ip, power = cidr.split("/")
    ip1, ip2, ip3, ip4 = ip.split(".")
    ip_int = int(ip4) + int(ip3) * 256 + int(ip2) * 65536 + int(ip1) * 2 ** 24
    ip_int = ip_int // (2 ** (32 - int(power))) * (2 ** (32 - int(power)))
    def reconstruct_ip(ip_int):
        ip_addr = []
        for i in range(4):
            ip_addr.append(str(ip_int % 256))
            ip_int //= 256
        return ".".join(ip_addr[::-1])

    output_list = []
    for i in range(2 ** (32 - int(power))):
        output_list.append(reconstruct_ip(ip_int))
        ip_int += 1
    return output_list


api_key_shuo = 'taRFETcxyjbQQEAUmyJ1WAyzwhALCq3a'
api_key_eric = 'qlNmFUhpentjJ2DdRaK8XlAavpf4Kvkq'

api_key = api_key_shuo

api = shodan.Shodan(api_key)
cidr_list = ['66.162.22.128/25', '162.129.0.0/16', '129.176.0.0/16', '143.111.0.0/16']

cur = db_connect()
counter = 0

log = open('c:/log_hospital.txt', 'w')

for cidr in cidr_list:
    # result_list = api.search('net:' + cidr)
    # total = result_list['total']
    # for i in range(total / 100 + 1):
    #     result_list = api.search('net:' + cidr, page=i+1)
    #     for item in result_list['matches']:
    for ip in ip_range_generator(cidr):
        try:
            # Lookup the host
            host = api.host(ip)

            # Print general info
            for d in host['data']:
                try:
                    counter += 1
                    asn = str_replace(d["asn"]) if "asn" in d else None
                    data = str_replace(d["data"]) if "data" in d else None
                    ip = str_replace(d["ip"]) if "ip" in d else None
                    ip_str = str_replace(d["ip_str"]) if "ip_str" in d else None
                    port = str_replace(d["port"]) if "port" in d else None
                    timestamp = str_replace(d["timestamp"]) if "timestamp" in d else None
                    hostnames = str_replace(d["hostnames"]) if "hostnames" in d else None
                    domains = str_replace(d["domains"]) if "domains" in d else None

                    loc = d["location"] if "location" in d else None

                    area_code = str_replace(loc["area_code"]) if "area_code" in loc else None
                    city = str_replace(loc["city"]) if "city" in loc else None
                    country_code = str_replace(loc["country_code"]) if "country_code" in loc else None
                    country_code3 = str_replace(loc["country_code3"]) if "country_code3" in loc else None
                    country_name = str_replace(loc["country_name"]) if "country_name" in loc else None
                    dma_code = str_replace(loc["dma_code"]) if "dma_code" in loc else None
                    latitude = str_replace(loc["latitude"]) if "latitude" in loc else None
                    longitude = str_replace(loc["longitude"]) if "longitude" in loc else None
                    postal_code = str_replace(loc["postal_code"]) if "postal_code" in loc else None
                    region_code = str_replace(loc["region_code"]) if "region_code" in loc else None

                    opts = str_replace(d["opts"]) if "opts" in d else None
                    org = str_replace(d["org"]) if "org" in d else None
                    isp = str_replace(d["isp"]) if "isp" in d else None
                    os = str_replace(d["os"]) if "os" in d else None
                    uptime = str_replace(d["uptime"]) if "uptime" in d else None
                    link = str_replace(d["link"]) if "link" in d else None
                    product = str_replace(d["product"]) if "product" in d else None
                    version = str_replace(d["version"]) if "version" in d else None
                    devicetype = str_replace(d["devicetype"]) if "devicetype" in d else None
                    info = str_replace(d["info"]) if "info" in d else None
                    cpe = str_replace(d["cpe"]) if "cpe" in d else None
                    html = str_replace(d["html"]) if "html" in d else None

                    string = """INSERT INTO `shodan`.`hospital_shodan`
                     (`asn` ,`data`,`ip`,`ip_str`,`port`,`timestamp`,`hostnames`,`domains`,
                     `area_code`,`city`,`country_code`,`country_code3`,`country_name`,`dma_code`,`latitude`,`longitude`,
                     `postal_code`,`region_code`,`opts`,`org`,`isp`,`os`,`uptime`,`link`,
                     `product`,`version`,`devicetype`,`info`,`cpe`, `html`, `cidr`)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                    '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                    '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                    '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % \
                             (asn, data, ip, ip_str, port, timestamp, hostnames, domains,
                             area_code, city, country_code, country_code3, country_name, dma_code, latitude, longitude,
                             postal_code, region_code, opts, org, isp, os, uptime, link,
                             product, version, devicetype, info, cpe, html, cidr)

                    string = string.replace("'None'", "null")

                    cur.execute(string)
                except pymysql.err.IntegrityError as err:
                    log.write("IntegrityError: {0}, at counter {1}, ip {2}\n".format(err, counter, ip))
                    log.flush()
                except Exception as err:
                    log.write("Unsolved exception: {0}, at counter {1}, ip {2}, json object {3}\n".format(err, counter, ip, d))
                    log.flush()
        except Exception as err:
            print("IP {0}: {1}".format(ip, err))
