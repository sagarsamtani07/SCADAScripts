__author__ = 'edwardsj'

from subprocess import PIPE
import subprocess
import time
import pymysql

log = open("zmaplog.txt", "a")
db = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                     user="ShodanTeam",  # your username
                     passwd="Sh0d@n7e",  # your password
                     db="shodan",
                     charset='utf8',
                     autocommit=True)  # name of the data base

cur_ip = db.cursor()
cur_port = db.cursor()
cur_ou = db.cursor()
ip_list = []
port_list = []

try:
    cur_ip.execute("""
                SELECT `ip`, `searchid`
                FROM `shodan`.`scadashodan`
                WHERE `portnum` = 80
                LIMIT 0, 10;
                """)
except pymysql.err.IntegrityError as err:
    log.write("SQL ERROR: {0}\n".format(err))
    log.flush()
    exit(0)

try:
    cur_port.execute("""
                SELECT `port`
                FROM `shodan`.`sy_scada_port_list`
                ORDER BY port;
                """)
except pymysql.err.IntegrityError as err:
    log.write("SQL ERROR: {0}\n".format(err))
    log.flush()
    exit(0)

ip_result = cur_ip.fetchall()
#ip_result = [("128.196.27.147",1), ("128.196.27.170",2),("10.128.50.165",3), ("74.125.224.81",4)]
port_result = cur_port.fetchall()
#port_result = [(80,),(3306,),(102,)]
for (result) in port_result:
    port_list.append(result[0])

for (result) in ip_result:
    ip = result[0]
    id = result[1]

    proc_list = []
    
    # intitalize two lists
    port_check_list = [1 for i in range(len(port_list))]
    proc_list = [None for i in range(len(port_list))]
    port_string_list = []

    print("Scan IP: " + ip)
    for i in range(len(port_check_list)):
        proc_list[i] = subprocess.Popen(["zmap", "-p", str(port_list[i]), "{0} -o -".format(ip)],
                                        stdout=PIPE,
                                        stderr=PIPE)  # create a scanning thread for the port 

    # waiting for the scan
    while True:
        bigflag = True
        for i in range(len(port_list)):
            if port_check_list[i] == 1: # check this port
                proc = proc_list[i]                    
                flag = proc.poll()
                if flag is None:
                    bigflag = False
                else:
                    stdou, stderr = proc.communicate()
                    if stderr.decode("utf8").strip().find("hits: 100.00%") != -1:
                        port_string_list.append(str(port_list[i]))
                        port_check_list[i] = 0
                    elif stderr.decode("utf8").strip().find("0.00%") == -1:
                        proc_list[i] = subprocess.Popen(["zmap", "-p", str(port_list[i]), "{0} -o -".format(ip)],
                                                        stdout=PIPE,
                                                        stderr=PIPE)
                    else:
                        port_check_list[i] = 0
        if bigflag:
            break

    port_string = ";".join(port_string_list)
    port_string = port_string.strip()
    print("Open Ports: " + port_string)    

    try:
        sql = """
              INSERT INTO `shodan`.`zmap_verified_devices` (
              `ip`, `timestamp`, `portlist`, `id`
              ) VALUES (
              '%s', '%s', '%s', '%s'
              );
              """ % (ip, time.time(), port_string, id)
        # print(sql)
        sql = sql.replace("''", "null")
        cur_ou.execute(sql)
    except pymysql.err.IntegrityError as err:
        log.write("IntegrityError for {0}: {1}\n".format(ip, err))
        log.flush()
