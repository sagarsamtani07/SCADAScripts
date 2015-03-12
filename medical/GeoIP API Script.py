from urllib.request import urlopen
import json
import pymysql

db = pymysql.connect(host="128.196.27.147", # your host, usually localhost
                     user="ShodanTeam", # your username
                    passwd="Sh0d@n7e", # your password
                     db="shodan",
                     charset='utf8',
                     autocommit=True) # name of the data base
cur = db.cursor()

ips = []
jsonResponses = []
sqlCommand = "select hospitalip from hospital_data limit 1800"
cur.execute(sqlCommand)
results= cur.fetchall()
for row in results:
    ips.append(row[0])


geoIPURL = 'http://api.db-ip.com/addrinfo?addr='
geoIPKey = '&api_key=792d6e9afd59125f05fd07ea9af324bf45d32d0c'

i = 0

jsonnn = []
while i<len(ips):
    print (ips[i])
    apicall = geoIPURL + ips[i] + geoIPKey
    htmlfile = urlopen(apicall)
    html = htmlfile.read()
    jsonResponses.append(html)
    i += 1



for line in jsonResponses:
    d = json.loads(str(line, 'utf-8'))
    address = d["address"] if "address" in d else None
    country = d["country"] if "country" in d else None
    stateprov = d["stateprov"] if "stateprov" in d else None
    city = d["city"] if "city" in d else None

    print (address, country, stateprov, city)

    string = """INSERT INTO shodan.geo_ip_api (hospitalip, hospitalcountry, hospitalstate, hospitalcity)
                        VALUES ('%s', '%s', '%s', '%s')""" %(address, country, stateprov, city)
    cur.execute(string)

