# code to test Shodan entries against NVD database entries 

import pymysql


shodandb = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="shodan",
                     charset='utf8',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)  # name of the data base

nvddb = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="nvddb",
                     charset='utf8',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)  # name of the data base

vulnerablesystems = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="vulnerablesystems",
                     charset='utf8',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)  # name of the data base

try:

    with shodandb.cursor() as cursor:
        # Read a single record
        sql = "SELECT `ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
        cursor.execute(sql, ('%scada%',))
        result = cursor.fetchone()
        print(result)
finally:
    shodandb.close()
    
try:

    with nvddb.cursor() as cursor:
        # Read a single record
        sql = "SELECT `vendor`, `product`, `version` FROM `nvdvuln` WHERE `vendor` like %s or `product` like %s"
        cursor.execute(sql, ('%power%','%power%',))
        result = cursor.fetchone()
        print(result)
finally:
    nvddb.close()