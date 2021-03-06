from fuzzywuzzy import fuzz
import pymysql
import time

db_10 = pymysql.connect(host="10.128.50.165",  # your host, usually localhost
                        port=8080,
                        user="shodan",  # your username
                        passwd="Sh0d@n7e",  # your password
                        db="test",
                        charset='utf8',
                        autocommit=True)  # name of the data base

db_128 = pymysql.connect(host="128.196.27.147",  # your host, usually localhost
                        port=3306,
                        user="ShodanTeam",  # your username
                        passwd="Sh0d@n7e",  # your password
                        db="shodan",
                        charset='utf8',
                        autocommit=True)  # name of the data base

def str_replace(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

cursor_128 = db_128.cursor()
cursor_10_write = db_10.cursor()

# sql_count = "select count(*) from test.shodan_classified_scada where conf > 0.995"
# cursor_10.execute(sql_count)
# total_records = cursor_10.fetchone()[0]

sql = "select searchID, ip, portnum, timestamp, devicedata from shodan.scadashodan"
cursor_128.execute(sql)
print("Query Succeeded")
total_records = cursor_128.rowcount
print("Will parse " + str(total_records) + " records")

threshold = 50
cluster_list = []
sql_log = open("sql_insert2.log", "w")
cluster_log = open("cluster2.log", "w")


def insert_record(rec, clindex):
    """
    Insert the record into the database
    :param rec: Device record
    :param clindex: Cluster number
    :return: None
    """
    id = rec[0]
    ip_str = rec[1]
    port = rec[2]
    timestamp = rec[3]
    data = rec[4]

    cluster_log.write(str(id) + "\t=>\t" + str(clindex) + "\n")
    cluster_log.flush()

    sql = "INSERT INTO test.clustered_scadashodan (id, ip_str, port, timestamp, data, conf, cluster)" \
          "VALUES ('%s', '%s','%s','%s','%s','%s','%s')" % \
          (id, ip_str, port, timestamp, str_replace(data), 0, clindex)
    try:
        cursor_10_write.execute(sql)
    except Exception as e:
        sql_log.write("Error: " + str(e) + " " + sql + "\n")
        sql_log.flush()


def get_score(s, t):
    """
    Function to return similarity scores between two Strings
    The method will use lower() to deal with case
    :param s: String 1
    :param t: String 2
    :return: Similarity score
    """
    return fuzz.ratio(s.lower(), t.lower())

count = 0

for record in cursor_128:
    count += 1
    if count % int(total_records/100) == 0:
        print("Progress: " + str(count) + "/" + str(total_records) + " " + time.strftime("%m/%d %H:%M:%S", time.localtime()))

    data = record[4]
    if len(cluster_list) == 0:
        cluster_list.append(data)
        insert_record(record, len(cluster_list))
    else:
        score = [get_score(data, x) for x in cluster_list]
        m_score = max(score)
        if m_score >= threshold:
            index = score.index(m_score)
            insert_record(record, index + 1)
        else:
            cluster_list.append(data)
            insert_record(record, len(cluster_list))

cluster_log.close()
sql_log.close()


