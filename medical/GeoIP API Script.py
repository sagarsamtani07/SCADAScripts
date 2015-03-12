from urllib.request import urlopen
import json
import pymysql

def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

geoIPURL = 'http://api.db-ip.com/addrinfo?addr='
# geoIPKey = '&api_key=792d6e9afd59125f05fd07ea9af324bf45d32d0c'  # Free Key
geoIPKey = '&api_key=9b6edc5aa3336fc97a8e918957123c3426ddc66b'  # Lite Key

db = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="shodan",
                     charset='utf8',
                     autocommit=True)  # name of the data base
cur = db.cursor()

sqlCommand = """
    SELECT DISTINCT hospitalip
    FROM hospital_data
    WHERE hospitalip != "Not available"
    AND hospitalip NOT IN (
        SELECT DISTINCT ip
        FROM geo_ip_api
    )
    LIMIT 3000
    """
cur.execute(sqlCommand)
results = cur.fetchall()

for row in results:
    apicall = geoIPURL + row[0] + geoIPKey
    htmlfile = urlopen(apicall)
    line = htmlfile.read()
    print("JSON of {0} Fetched".format(row[0]))

    d = json.loads(str(line, 'utf-8'))
    ip_address = str_replace(d["address"]) if "address" in d else None
    country = str_replace(d["country"]) if "country" in d else None
    stateprov = str_replace(d["stateprov"]) if "stateprov" in d else None
    city = str_replace(d["city"]) if "city" in d else None
    latitude = str_replace(d['latitude']) if "latitude" in d else None
    longitude = str_replace(d['longitude']) if "longitude" in d else None
    tz_offset = str_replace(d['tz_offset']) if "tz_offset" in d else None
    tz_name = str_replace(d['tz_name']) if "tz_name" in d else None

    string = """
        INSERT INTO `shodan`.`geo_ip_api`
            (`ip`, `country`, `state`, `city`, `latitude`, `longitude`, `tz_offset`, `tz_name`)
        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" \
             % (ip_address, country, stateprov, city, latitude, longitude, tz_offset, tz_name)
    cur.execute(string)

    print("IP: {0} Inserted Successfully".format(ip_address))

