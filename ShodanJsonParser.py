import json
import pymysql

def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

db = pymysql.connect(host="128.196.27.147", # your host, usually localhost
                     user="ShodanTeam", # your username
                    passwd="Sh0d@n7e", # your password
                     db="shodan",
                     charset='utf8',
                      autocommit=True)# name of the data base

cur = db.cursor()

sql = ""
counter = 0

log = open("C:/Users/ejgross/Desktop/log.txt", "w+")

with open("C:/Users/ejgross/Desktop/ShodanRepo/2014-12-23.json", "rb") as s:

    for line in s:
        for s in s:

            sql = ""
            counter += 1

            # used to skip the front "counter" records
            if counter < 1024345:
                print ("Record {0} skipped".format(counter))
                continue

            try:
                #d = ijson.parse(open(txt, encoding="utf-8"))
                d = json.loads(str(s, 'utf-8'))
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

                string = """INSERT INTO `shodan`.`shodan_2014_12_13`
                 (`asn` ,`data`,`ip`,`ip_str`,`port`,`timestamp`,`hostnames`,`domains`,`area_code`,`city`,`country_code`,
                `country_code3`,`country_name`,`dma_code`,`latitude`,`longitude`,`postal_code`,`region_code`,`opts`,
                `org`,`isp`,`os`,`uptime`,`link`,`product`,`version`,`devicetype`,`info`,
                `cpe`, `html`)
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" %(asn,
                data, ip, ip_str, port, timestamp, hostnames, domains, area_code, city, country_code, country_code3, country_name, dma_code, latitude, longitude, postal_code, region_code, opts, org, isp, os, uptime, link, product, version, devicetype, info, cpe, html)

                string = string.replace("'None'", "null")

                sql += string

                print(counter)
                # if counter % 2 == 0:
                    # print(sql)

                cur.execute(sql)
            except pymysql.err.IntegrityError as err:
                log.write("IntegrityError: {0}, at counter {1}, ip {2}\n".format(err, counter, ip))
                log.flush()
            except Exception as err:
                log.write("Unsolved exception: {0}, at counter {1}, ip {2}, json object {3}\n".format(err, counter, ip, d))
                log.flush()
