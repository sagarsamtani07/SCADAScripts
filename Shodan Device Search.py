__author__ = 'sagars'
import shodan
import pymysql


def db_connect():
    return pymysql.connect(host="128.196.27.147",
                           user="ShodanTeam",
                           passwd="Sh0d@n7e",
                           db="shodan",
                           charset='utf8',
                           autocommit=True).cursor()

cur = db_connect()

def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

api_key = 'taRFETcxyjbQQEAUmyJ1WAyzwhALCq3a'
api = shodan.Shodan(api_key)

counter = 0
device_list = ['apache']
log = open('C:\\Users\\sagars\\Desktop\\deviceerrors.txt', 'w')

for device in device_list:
    try:
        # Search Shodan
        results = api.search(device)

        print'Results found: %s' % results['total']
        for d in results['matches']:
                counter += 1
                asn = str_replace(d["asn"]) if "asn" in d else None
                dataa = str_replace(d["data"]) if "data" in d else None
                ip = str_replace(d["ip"]) if "ip" in d else None
                ip_str = str_replace(d["ip_str"]) if "ip_str" in d else None
                port = str_replace(d["port"]) if "port" in d else None
                timestampp = str_replace(d["timestamp"]) if "timestamp" in d else None
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

                string = """INSERT INTO new_scada_shodan
                 (asn ,dataa,ip,ip_str,port,timestampp,hostnames,domains,
                 area_code,city,country_code,country_code3,country_name,dma_code,latitude,longitude,
                 postal_code,region_code,opts,org,isp,os,uptime,link,
                 product,version,devicetype,info,cpe, html)
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                '%s', '%s', '%s', '%s', '%s', '%s');""" % \
                         (asn, dataa, ip, ip_str, port, timestampp, hostnames, domains,
                         area_code, city, country_code, country_code3, country_name, dma_code, latitude, longitude,
                         postal_code, region_code, opts, org, isp, os, uptime, link,
                         product, version, devicetype, info, cpe, html)

                string = string.replace("'None'", "null")
                print string
                cur.execute(string)

        print ''
    except shodan.APIError, e:
        print 'Error: %s' %e
