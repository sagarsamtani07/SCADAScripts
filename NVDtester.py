# __author__ = 'Eric Gross'
# code to test Shodan entries against NVD database entries 

import pymysql


def str_replace(s):
    return str(s).replace("_", "_").replace("-","").replace("None","")

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


with open("C:/Users/Gross/Desktop/NVDtesterLogs/log.txt", "w+") as log:

    try:  
            
        with nvddb.cursor() as cursornv:
            # Read all records from NVD DB
            sql = "SELECT `cvd_id`,`vendor`, `product`, `version`, `Score` FROM `nvdvuln` where `cvd_id` like '%2015%' or `cvd_id` like '%2014%' or `cvd_id` like '%2013%' and CHAR_LENGTH(product) > 4"# or `cvd_id` like '%2012%' and CHAR_LENGTH(product) > 4"
            cursornv.execute(sql)
            result = cursornv.fetchall()
            
            for r in result:
                cvid = r["cvd_id"]
                vendor = r["vendor"]
                product = r["product"]
                version = str_replace(r["version"])
                score = r["Score"]
                
                datatest = "%" + product + "%" + version + "%"
                
                print(datatest)
                
                with shodandb.cursor() as cursorsdb:
                    # Read all records from SFS SCADA db
                    sql = "SELECT `ID`,`ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
                    cursorsdb.execute(sql, (datatest,))
                    result2 = cursorsdb.fetchall()

                    for r in result2:
                        ShodanID = r["ID"]
                        ip_str = r["ip_str"]
                        data = r["data"]
                        print("executed Shodan cursor")  

                        print(cvid + "on" + ip_str)

                        try:
                            with vulnerablesystems.cursor() as cursorvs:
                                # Create a new record in Vulnerable systems
                                sql = "INSERT INTO `nvdvuln` (`ShodanID`, `ipaddr`, `CVE-ID`, `vendor`,`product`,`version`, `score`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                cursorvs.execute(sql, (ShodanID, ip_str, cvid, vendor, product, version, score))
                            print("Vulnerable system found!")
                        except Exception as err:
                                log.write("Unsolved exception: {0}, at CVID {1}, ip {2}\n".format(err, cvid, ip_str))
                                log.flush()

    finally:
        nvddb.close()
        shodandb.close()
        vulnerablesystems.close()