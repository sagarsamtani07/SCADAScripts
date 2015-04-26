# __author__ = 'Eric Gross'
# code to test Shodan entries against NVD database entries 

import pymysql


def str_replace(s):
    return str(s).replace("_", " ")

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
        sql = "SELECT `cvd_id`,`vendor`, `product`, `version`, `Score` FROM `nvdvuln`"
        cursornv.execute(sql)
        result = cursornv.fetchall()
        for r in result:
            cvid = r["cvd_id"]
            vendor = str_replace(r["vendor"])
            product = str_replace(r["product"])
            version = r["version"]
            score = r["Score"]
            
            with shodandb.cursor() as cursorsdb:
                # Read all records from SFS SCADA db
                sql = "SELECT `ID`,`ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
                cursorsdb.execute(sql, ('%scada%',))
                result2 = cursorsdb.fetchall()
                for r in result2:
                    ShodanID = r["ID"]
                    ip_str = r["ip_str"]
                    data = r["data"]
                    print("executed Shodan cursor")  
            
                    print(product)
                    print(data)
                    print(version)
                    
                    if(product in data) and (version in data): #or (product in data) and (version in data)): 
                        try:
                            with vulnerablesystems.cursor() as cursorvs:
                                # Create a new record in Vulnerable systems
                                sql = "INSERT INTO `nvdvuln` (`ShodanID`, `ipaddr`, `CVE-ID`, `Score`) VALUES (%s, %s, %s, %s)"
                                cursorvs.execute(sql, (ShodanID, ip_str, cvid, score))
                            print("Vulnerable system found!")
                        except: 
                            print('duplicate entry: rollback')

finally:
    nvddb.close()
    shodandb.close()
    vulnerablesystems.close()