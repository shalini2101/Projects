import json
import mysql
import mysql.connector
from mysql.connector import errorcode

SUBSCRIBER_TABLE = (
    "CREATE TABLE `subscribers` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `date` date ,"
    "  `user_id` varchar(16) NOT NULL,"
    "  `ip` varchar(20) NOT NULL,"
    "  `port` int(11) NOT NULL,"
    "  `status` enum('Online','Offline') NOT NULL,"
    "  `time` varchar(128) ,"
    "  `message` varchar(2048) ,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")




def user_connect_sql(uname, passwd, host):
    mydb = mysql.connector.connect(host=host,user=uname)
    print(mydb)
    return mydb

def create_data_base(my_db,name):
    mycursor = my_db.cursor()
    try:
        mycursor.execute("CREATE DATABASE "+name)
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))


def create_database(cursor,dbName):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dbName))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

def connectDataBase(mydb,cursor,dbName):
    
    try:
        cursor.execute("USE {}".format(dbName))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(dbName))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor,dbName)
            print("Database {} created successfully.".format(dbName))
            mydb.database = dbName
        else:
            print(err)
    
    return cursor

def createTable(cursor,table_discription,table_name):
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_discription)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

    
def insert_data(mydb,cursor,col,val):
    cursor.execute(col, val)
    emp_no = cursor.lastrowid
    print(emp_no)
    mydb.commit()
    

def query_table(mydb,cursor,query,data):
    cursor.execute(query,data)
    return cursor.fetchall()

def update_data(mydb,cursor,query):
    cursor.execute(query)
    mydb.commit()

def db_init(mydb,cursor,table_disc,table_name,dbName):

    print("Initializing the DB...")
    connectDataBase(mydb,cursor,dbName)
    createTable(cursor,table_disc,table_name)

    
    
def test_insert():
    mydb = mysql.connector.connect(host='127.0.0.1',user='root',database='serverDB')
    cursor = mydb.cursor()
    user_status = ("INSERT INTO subscribers "
        "(user_id, ip, port, status, time, message) "
        "VALUES (%(user_id)s, %(ip)s, %(port)s, %(status)s, %(time)s, %(message)s)")
    user_value = {}
    user_value['user_id']='123456'
    user_value['ip']='127.0.0.1'
    user_value['port'] = 2222
    user_value['status'] = 'Online'
    user_value['time'] = 'Mon Jul 2020'
    user_value['message'] = None

    insert_data(mydb,cursor,user_status,user_value)
    
    

#db_init(SUBSCRIBER_TABLE,'subscribers','serverDB')
#test_insert()
#user_id=('7091728998')
#query = ("SELECT * FROM subscribers "
#    "WHERE user_id={}".format(user))

#result=query_table(query,user_id)
#print(result)

def getClientDB():
    with open('client_config.json') as f:
        data=json.load(f)
        return data['ClientDB']

def return_client_list():
    with open('client_config.json') as f:
        clientList=json.load(f)
        return clientList['ClientList']

def getAllClientDetails(clientName):
    with open('client_config.json') as f:
        clientParam=json.load(f)
        clientInfo = clientParam[clientName]
        return (clientInfo)
