# __author__ = 'Eric Gross'
# code to test Shodan entries against NVD database entries 

import pymysql
import re


def str_replace(s):
    return str(s).replace("-", "").replace("None", "").replace(".", "\.")


def str_replaceteststr(d):
    return str(d).replace(".", "\\.")


def str_replaceprod(p):
    return str(p).replace("_", ".").replace("/", ".").replace("\\", ".").replace("-", ".").replace(" ", ".")

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


with open("E:/EricGross-PC/Users/Eric/Desktop/log.txt", "w+") as log:

    try:  
            
        with nvddb.cursor() as cursornv:
            # Read all records from NVD DB
            # sql = "SELECT `cvd_id`,`vendor`, `product`, `version`, `Score`
            # FROM `nvdvuln` where `product` = 'windows_xp'"
            sql = """SELECT distinct `product`, `version` FROM `nvdvuln`
                     WHERE `cvd_id` LIKE '%2015%' OR `cvd_id` LIKE '%2014%'
                     OR `cvd_id` LIKE '%2013%' OR `cvd_id` LIKE '%2012%'
                     AND `CHAR_LENGTH`(`product`)>'4';"""
            cursornv.execute(sql)
            result = cursornv.fetchall()
            
            for r in result:
                product = r["product"]
                versorig = r["version"]
                version = str_replace(versorig)
                
                datatest = "%" + product + "%" + version + "%"
                
                print(datatest)
                
                with shodandb.cursor() as cursorsdb:
                    # Read all records from SFS SCADA db
                    sql = "SELECT `ID`,`ip_str`, `data` FROM `sy_sfs_scadashodan` WHERE `data` like %s"
                    cursorsdb.execute(sql, (datatest,))
                    result2 = cursorsdb.fetchall()

                    for r2 in result2:
                        ShodanID = r2["ID"]
                        ip_str = r2["ip_str"]
                        data = r2["data"]
                        print("executed Shodan cursor on " + ip_str)
                        
                        print(version)
                        m = re.search("[^0-9][^.](%s)[^0-9]" % version, data)

                        newprod = str_replaceprod(product)
                        print(newprod)
                                                              
                        l = re.search("(%s)" % newprod, data)
                        
                        if version == "":
                            try:
                                with vulnerablesystems.cursor() as cursorvs:
                                    # Create a new record in Vulnerable systems
                                    sql = """INSERT INTO `nvdvuln` (
                                             `ShodanID`, `ipaddr`, `product`,`version`
                                             ) VALUES (
                                             %s, %s, %s, %s
                                             );"""
                                    cursorvs.execute(sql, (ShodanID, ip_str, product, versorig))
                                print("Vulnerable system found!")
                                print("on " + ip_str)
                            except Exception as err:
                                    log.write("Unsolved exception: {0}, ip {1}\n".format(err, ip_str))
                                    log.flush()

                        if m and l:
                            try:
                                with vulnerablesystems.cursor() as cursorvs:
                                    # Create a new record in Vulnerable systems
                                    sql = """INSERT INTO `nvdvuln` (
                                             `ShodanID`, `ipaddr`, `product`,`version`
                                             ) VALUES (
                                             %s, %s, %s, %s
                                             );"""
                                    cursorvs.execute(sql, (ShodanID, ip_str, product, versorig))
                                print("Vulnerable system found!")
                                print("on " + ip_str)
                            except Exception as err:
                                    log.write("Unsolved exception: {0}, ip {1}\n".format(err, ip_str))
                                    log.flush()
                        else:
                            print("incorrect MySQL version match")

    finally:
        nvddb.close()
        shodandb.close()
        vulnerablesystems.close()
