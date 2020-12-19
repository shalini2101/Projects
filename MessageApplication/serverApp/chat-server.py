import socket
import select  
import sys  
import _thread
import pickle
import utility
from utility import *


#table Schema
TABLE_DISCRIPTON = (
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

TABLE_NAME = 'subscribers'
DB_NAME = 'serverDB'

user_conn={}

def server_start(ip,port):
    print("Server Starting....")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

    server.bind((ip, port)) 
    return server

def userConnHandler(conn,addr,mydb,cursor):
    'Handle User connection for each user'
    print("User Thread started ")
    while True:
        data = conn.recv(2048) #Waiting for message from client
        msg = pickle.loads(data)

        #Now take the message to the operation level
        if msg.get('type') == 'Online':
            print('User {} is online now'.format(msg.get('user')))

            user = str(msg.get('user'))
            query = ("SELECT * FROM subscribers "
                "WHERE user_id={} ".format(user))
            
            result = query_table(mydb,cursor,query,user)
            
            if len(result) == 0:
                print("This is first time for user {}".format(user))
                user_status = ("INSERT INTO subscribers "
                    "(user_id, ip, port, status, time, message) "
                    "VALUES (%(user_id)s, %(ip)s, %(port)s, %(status)s, %(time)s, %(message)s)")

                user_v = {
                    'user_id':user,
                    'ip':addr[0],
                    'port':addr[1],
                    'status':'Online',
                    'time':str(msg.get('time')),
                    'message':None
                }

                insert_data(mydb,cursor,user_status, user_v)
            else:
                user_status = "UPDATE subscribers SET status = {} WHERE  user_id={}".format(1,user)
                update_data(mydb,cursor,user_status)
            user_conn[user]=conn


            print(user_conn)

        if msg.get('type') == 'Delete':
            print("User {} wants to delete this account".format(msg.get('user')))

        if msg.get('type') == 'MessageSend':
            sender = str(msg.get('sender'))
            receiver = str(msg.get('receiver'))
            query1 = ("SELECT * FROM subscribers "
                "WHERE user_id={} ".format(sender))
            result = query_table(mydb,cursor,query1,sender)
            #if caller status is found in server
            if len(result) is not 0:
                #Lets check status of calle 
                query2 = ("SELECT * FROM subscribers "
                    "WHERE user_id={} ".format(receiver))
                res = query_table(mydb,cursor,query2,receiver)
                if len(res) == 0:
                    print("Fatel : User not found")
                    pass
                else:
                    try:
                        connection = user_conn[receiver]
                    except:
                        print("Key Error")
                        connection = user_conn[sender]
                        nACK = {
                            'type':'404',
                            'message':'User Not Available'
                        }
                        payLoad=pickle.dumps(nACK)
                        connection.send(payLoad)
                        continue
                    msg['type'] = 'MessagRecv'
                    print(msg)
                    payLoad = pickle.dumps(msg)
                    connection.send(payLoad)

        if msg.get('type') == 'Offline':
            user_status = "UPDATE subscribers SET status = {} WHERE  user_id={}".format(2,msg.get('sender'))
            update_data(mydb,cursor,user_status)
 
        if msg.get('type') == 'Status':   #Now Server will tell you who is online in your contacts  
            #print('Update {} About its all Buddies who is online'.format(msg.get('user')))
            contacts = msg.get('contacts')
            for cont,status in contacts.items():
                query = "SELECT status from {} where user_id={}".format(TABLE_NAME,cont)
                result = query_table(mydb,cursor,query,cont)
                if len(result) != 0:
                    contacts[cont]=result[0][0]
            online_check={'type':'Status'}
            online_check['contacts'] = contacts
            data = pickle.dumps(online_check)
            connection = user_conn[msg.get('sender')]
            connection.send(data)



def client_handler(server,mydb,cursor):
    print("Waiting for clients...")
    server.listen(5)  #Queuing up the client request 
    while True:  
        conn, addr = server.accept() #This will accept the client request <---- CLient1, client2
        try:
            _thread.start_new_thread( userConnHandler, (conn, addr,mydb,cursor) )
        except:
            print ("Error: unable to start thread")

       # print("Conn {} addr {}".format(conn,addr))


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 1234
    try:
        mydb = mysql.connector.connect(host='127.0.0.1',user='root',database='serverDB')
    except mysql.connector.Error as err:
        mydb = mysql.connector.connect(host='127.0.0.1',user='root')
        cursor = mydb.cursor()
        create_database(cursor,DB_NAME)
    cursor = mydb.cursor()
    db_init(mydb,cursor,TABLE_DISCRIPTON,TABLE_NAME,DB_NAME)
    s_id = server_start(ip,port)
    client_handler(s_id,mydb,cursor)
