__author__ = 'sagars'

import pymysql
import time
import json
import urllib.request

# function to connect to the database. Table we are interested in is shodan.vulnerablesystems_test on 128.196.27.147

db = pymysql.connect(host="128.196.27.147", # your host, usually localhost
                         user="ShodanTeam", # your username
                         passwd="Sh0d@n7e", # your password
                         db="shodan", # name of the data base
                         charset='utf8',
                         autocommit=True)
def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

# retrieve all of the IP addresses and store in a list
cur = db.cursor()
ip_list = []

cur.execute("select distinct(ipaddr) from shodan.vulnerablesystems")
results= cur.fetchall()
iplist = [row[0] for row in results]

# URL to call out to
APIURL =  "http://ip-api.com/json/"

counter = 0
for ip in iplist:
    APICALL = APIURL + ip
    response = urllib.request.urlopen(APICALL)
    json_string = response.read().decode('utf-8')
    json_data = json.loads(json_string)
    status = (json_data['status'])

    # since JSON will always be returned, it will either have success or failure
    if status == 'success':
        as_info = (str_replace(json_data['as']))
        city = (str_replace(json_data['city']))
        country = (str_replace(json_data['country']))
        countryCode = (str_replace(json_data['countryCode']))
        isp = (str_replace(json_data['isp']))
        lat = (str_replace(json_data['lat']))
        lon = (str_replace(json_data['lon']))
        org = (str_replace(json_data['org']))
        ip_addr = (str_replace(json_data['query']))
        region = (str_replace(json_data['region']))
        regionName = (str_replace(json_data['regionName']))
        status = (str_replace(json_data['status']))
        timezone = (str_replace(json_data['timezone']))
        zip = (str_replace(json_data['zip']))

        #insert into the database
        string = """INSERT INTO vulnerablesystems_locations
                     (as_info ,city,country,countryCode,isp,lat,lon,org,ip_addr,region,regionName,status,timezone,zip)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s');""" %  \
                 (as_info ,city,country,countryCode,isp,lat,lon,org,ip_addr,region,regionName,status,timezone,zip)

        string = string.replace("'None'", "null")
        print (string)
        cur.execute(string)
        #cur.commit()
    else:
        pass
    
    #sleeps if there have been 250 records inserted
    counter += 1
    if counter == 249:
        print ("Sleeping here")
        time.sleep(60)
        counter = 0
