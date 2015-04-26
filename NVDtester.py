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
        # Read a single record
        sql = "SELECT `vendor`, `product`, `version` FROM `nvdvuln` WHERE `vendor` like %s or `product` like %s"
        cursornv.execute(sql, ('%power%','%power%',))
        result = cursornv.fetchall()
        for r in result:
            print(r)
        #print(result)
        
    with shodandb.cursor() as cursorsdb:
        # Read a single record
        sql = "SELECT `ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
        cursorsdb.execute(sql, ('%scada%',))
#        for r in shodandb.fetchall():
#            print(r)
        result = cursorsdb.fetchone()
        print(result)

    try:
        with vulnerablesystems.cursor() as cursorvs:
            # Create a new record
            sql = "INSERT INTO `nvdvuln` (`ShodanID`, `ipaddr`, `CVE-ID`, `Score`) VALUES (%s, %s, %s, %s)"
            cursorvs.execute(sql, ('webmaster@python.org', 'very-secret', 'very-secret', 'very-secret'))
    except: 
        print('duplicate entry: rollback')

finally:
    nvddb.close()
    shodandb.close()
    vulnerablesystems.close()