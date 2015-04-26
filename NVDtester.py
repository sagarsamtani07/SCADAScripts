# code to test Shodan entries against NVD database entries 

import pymysql


db = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="shodan",
                     charset='utf8',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)  # name of the data base

cur = db.cursor()

try:

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
        cursor.execute(sql, ('%powerlog%',))
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()