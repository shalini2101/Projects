import socket
import _thread
import time
import json
import pickle
import utility
import tkinter

from utility import *

userID = '9884465584'
userName = 'John'



MAIN_TABLE_NAME = 'usr_'+userID
DB_NAME = 'clientDB'
CONTACT_TABLE_NAME='contacts'
#table Schema
MAIN_TABLE_DISCRIPTON = (
    "CREATE TABLE `"+MAIN_TABLE_NAME+"` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `time` varchar(128) ,"
    "  `contacts` varchar(16) NOT NULL,"
    "  `status` enum('Online','Offline') NOT NULL,"
    "  `reply_status` enum('no','yes') NOT NULL,"
    "  `message` varchar(2048) ,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

CONTACT_TABLE_DISCRIPTON = (
    "CREATE TABLE `"+CONTACT_TABLE_NAME+"` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `contacts` varchar(16) NOT NULL,"
    "  `name` varchar(20) ,"
    "  `status` enum('Offline','Online') NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

#serverDB = 'serverDB'
ip = '127.0.0.1'
port = 2223
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#client.bind((ip,port))
chat_box={}














def msg_receiver(mydb,cursor,userID,clientObj):
    'This thread will keep receiving message from server'
    while True:
        data = clientObj.recv(2048)
        #print("Message Received..")
        msg = pickle.loads(data)
        if msg.get('type') == 'Status':
            contacts = msg.get('contacts')
            for cont,status in contacts.items():
                if status == 'Offline':
                    user_status = "UPDATE {} SET status = {} WHERE  contacts={}".format(CONTACT_TABLE_NAME,1,cont)
                else:
                    user_status = "UPDATE {} SET status = {} WHERE  contacts={}".format(CONTACT_TABLE_NAME,2,cont)
                update_data(mydb,cursor,user_status)
        if msg.get('type') == 'MessagRecv':
            user = str(msg.get('sender'))
            print("Message Received from <{}>".format(user))
         
            sender_info = ("INSERT INTO usr_7091728998 (time,contacts, status, reply_status, message) VALUES (%(time)s, %(contacts)s, %(status)s,%(reply_status)s, %(message)s)")

            sender_params = {
                'time':str(msg.get('time')),
                'contacts':user,
                'status':'Online',
                'reply_status':'no',
                'message':msg.get('message')
            }
            insert_data(mydb,cursor,sender_info, sender_params)


            print("{}[{}]:{}".format(msg['sender'],msg['time'],msg['message']))
            msg=input("John :")
            lTime = time.asctime()
            data = {
                'type':'MessageSend',
                'sender':userID,
                'receiver':user,
                'time':lTime,
                'message':msg
            }
            payLoad = pickle.dumps(data)
            clientObj.send(payLoad)
            #print("{}[{}]:{}".format(msg['sender'],msg['time'],msg['message']))





def connectServer(mydb,cursor,userID):
    serverIP = '127.0.0.1'
    serverPort = 1234
    try:
        client.connect((serverIP, serverPort)) 
    except:
        print("Server connection is not established")
        return
    
    #Notify to server you are online now :)
    lTime = time.asctime()
    helloMsg = {'type':'Online','user':userID, 'time':lTime}
    data = pickle.dumps(helloMsg)
    client.send(data)
    # Create two threads as follows
    try:
        _thread.start_new_thread( msg_receiver, (mydb,cursor,userID, client) )
     #   _thread.start_new_thread( contacts_status, (mydb,cursor,userID, client ) )
    except:
        print ("Error: unable to start thread")
    

def client_start(mydb,cursor,userID):
    connectServer(mydb,cursor,userID)




if __name__ == '__main__':
    try:
        mydb = mysql.connector.connect(host='127.0.0.1',user='root',database=DB_NAME)
        cursor = mydb.cursor()
    except mysql.connector.Error as err:
        mydb = mysql.connector.connect(host='127.0.0.1',user='root')
        cursor = mydb.cursor()
        create_database(cursor,DB_NAME)
    
    db_init(mydb,cursor,MAIN_TABLE_DISCRIPTON,MAIN_TABLE_NAME,DB_NAME)
    #Create Contact Table where all contacts entries are made
    createTable(cursor,CONTACT_TABLE_DISCRIPTON,CONTACT_TABLE_NAME)
    client_start(mydb,cursor,userID)

    while True:
        time.sleep(10000)
        pass