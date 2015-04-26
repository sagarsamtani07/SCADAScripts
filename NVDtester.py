# __author__ = 'Eric Gross'
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

    with nvddb.cursor() as cursornv:
        # Read all records from NVD DB
        sql = "SELECT `cvd_id`,`vendor`, `product`, `version` FROM `nvdvuln`"
        cursornv.execute(sql)
        result = cursornv.fetchall()
        for r in result:
            cvid = r["cvd_id"]
            vendor = r["cvd_id"]
            product = r["cvd_id"]
            version = r["cvd_id"]
        print("executed nvd cursor")

    with shodandb.cursor() as cursorsdb:
        # Read all records from SFS SCADA db
        sql = "SELECT `ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
        cursorsdb.execute(sql, ('%scada%',))
        result = cursorsdb.fetchall()
        for r in result:
            ip_str = r["ip_str"]
            data = r["data"]
        print("executed Shodan cursor")
    if((vendor in data) or (product in data) and (version in data)): 
        try:
            with vulnerablesystems.cursor() as cursorvs:
                # Create a new record in Vulnerable systems
                sql = "INSERT INTO `nvdvuln` (`ShodanID`, `ipaddr`, `CVE-ID`, `Score`) VALUES (%s, %s, %s, %s)"
                cursorvs.execute(sql, ('webmaster@python.org', 'very-secret', 'very-secret', 'very-secret'))
            print("Vulnerable system found!")
        except: 
            print('duplicate entry: rollback')

finally:
    nvddb.close()
    shodandb.close()
    vulnerablesystems.close()