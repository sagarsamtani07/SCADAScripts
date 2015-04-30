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
                LIMIT 0, 3;
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
port_result = cur_port.fetchall()
for (result) in port_result:
    port_list.append(result[0])

for (result) in ip_result:
    ip = result[0]
    id = result[1]

    proc_list = []

    # creating threads to scan all the ports of one ip
    for port in port_list:
        proc_list.append(subprocess.Popen(["zmap", "-p", str(port), "{0} -o -".format(ip)],
                                          stdout=PIPE,
                                          stderr=PIPE))
    print("thread created for ip: {0}".format(ip))

    # waiting for the scan
    while True:
        bigflag = True
        for proc in proc_list:
            flag = proc.poll()
            if flag is None:
                bigflag = False
                time.sleep(1)
                break
        if bigflag:
            break

    port_string_list = []

    # read scaning results
    for i in range(len(proc_list)):
        proc = proc_list[i]
        stdou, stderr = proc.communicate()
        if stderr.decode("utf8").strip().find("hits: 100.00%") != -1:
            port_string_list.append(str(port_list[i]))
        else:
            pass
    port_string = ";".join(port_string_list)

    if port_string != "":
        print(port_string)
        try:
            sql = """
                  INSERT INTO `shodan`.`zmap_verified_devices` (
                  `ip`, `timestamp`, `portlist`, `id`
                  ) VALUES (
                  '%s', '%s', '%s', '%s'
                  );
                  """ % (ip, time.time(), port_string, id)
            print(sql)
            cur_ou.execute(sql)
        except pymysql.err.IntegrityError as err:
            log.write("IntegrityError for {0}: {1}\n".format(ip, err))
            log.flush()
