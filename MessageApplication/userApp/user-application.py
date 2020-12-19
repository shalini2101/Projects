import socket
import _thread
import time
import pickle
import utility
import sys
from utility import *

activeChat=False
activeChatThread=False

DB_NAME=getClientDB()

#table Schema
MAIN_TABLE_DISCRIPTON = (
    "CREATE TABLE `{}` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `time` varchar(128) ,"
    "  `contacts` varchar(16) NOT NULL,"
    "  `status` enum('Online','Offline') NOT NULL,"
    "  `reply_status` enum('no','yes') NOT NULL,"
    "  `message` varchar(2048) ,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

CONTACT_TABLE_DISCRIPTON = (
    "CREATE TABLE `{}` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `contacts` varchar(16) NOT NULL,"
    "  `name` varchar(20) ,"
    "  `status` enum('Offline','Online') NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 


def menu():
    print("+--------------------+")
    print("1. Add Buddies ")
    print("2. Delete Buddy")
    print("3. Show New Messages")
    print("4. Show Online Buddies ")
    print("5. Go Offline")
    op = input("Option :")
    if op == '':
        return 0
    return int(op)

def msg_sender(mydb,cursor,userInfo,receiverID):
    global activeChat
    while activeChat == True:
        reply=input("{} Type :".format(userInfo['Mobile']))
        lTime = time.asctime()
        data = {
            'type':'MessageSend',
            'time':lTime,
            'sender':userInfo['Mobile'],
            'receiver':receiverID,
            'message':reply
        }
        payLoad = pickle.dumps(data)
        client.send(payLoad)
        print("{}[{}]:{}".format(userInfo['Mobile'],lTime,reply))
        if reply.capitalize() == "Bye":
            activeChat = False
            
def add_buddies(mydb,cursor,userInfo):
    'Adding the buddies based on their mobile number'
    global activeChat
    while True:
        number=input("Enter Mobile Number:")
        name=input("Name:")
        
        insert_contact = ("INSERT INTO {} (contacts, name) VALUES (%(contacts)s, %(name)s)".format(userInfo['contactsTable']))
        print(insert_contact)
        contact_params={
            'contacts':number,
            'name':name
        }
        insert_data(mydb,cursor,insert_contact, contact_params)
        op = input("Wish to add more y/n:")
        if op == 'y':
            continue
        else:
            activeChat=False
            break

def delete_buddies(userInfo):
    'deleting buddies from the contact list'



def newMessages(mydb,cursor,userInfo):
    'Show New Messages'
    global activeChat, activeChatThread
    query = ("SELECT contacts,count(reply_status) FROM {} WHERE reply_status=1 group by contacts".format(userInfo['mainTable']))

    result = query_table(mydb,cursor,query,userInfo['mainTable'])
    if len(result) is not 0:
        # Print the names of the columns. 
        print ("{:<3} {:<15} {:<11}".format('Id','Contacts', 'New Message')) 
  
        # print each data item. 
        id = 1
        for i in result:  
            print ("{:<3} {:<15} {:<11}".format(id,i[0],i[1])) 
            id += 1
        select = int(input("Select Id to See the message:"))
        count = 1
        receiver=''
        for i in result:
            if count == select:
                receiver=i[0]
                query = ("SELECT contacts,time,message FROM {} WHERE contacts={} ".format(userInfo['mainTable'],i[0]))
                result = query_table(mydb,cursor,query,i[0])
                for idx in result:
                    print("{:<8}[{}]:{}".format(idx[0],idx[1],idx[2]))
                break

            count += 1
        if count == select:
            activeChat = activeChatThread = True
            _thread.start_new_thread( msg_sender, (mydb,cursor,userInfo, receiver ) )


def onlineBuddies(mydb,cursor,userInfo):
    'Check who is online'
    global activeChat, activeChatThread
    query="select * from {} where status=2".format(userInfo['contactsTable'])
    result = query_table(mydb,cursor,query,userInfo['contactsTable'])
    if len(result) is not 0:
        print("{:<3} {:<15} {:<15} {:<11}".format('Id','Contacts','Name', 'Status'))

        id = 1
        for i in result:
            print ("{:<3} {:<15} {:<15} {:<11}".format(id,i[1],i[2],i[3]))
            id += 1
        select = int(input("Select Id to Chat with..:"))
        count = 1
        receiver=''
        for i in result:
            if count == select:
                receiver=i[1]
                query = ("SELECT contacts,time,message FROM {} WHERE contacts={} ".format(userInfo['mainTable'],i[1]))
                result = query_table(mydb,cursor,query,i[1])
                print(len(result))
                for idx in result:
                    msg="{:<8}[{}]:{}".format(i[2],idx[1],idx[2])
                    print(msg)
                break

            count += 1
        if count == select:
            activeChat = activeChatThread = True
            _thread.start_new_thread( msg_sender, (mydb,cursor,userInfo, receiver ) )

def goOffline(userInfo):
    'Adio Amigos'
    global activeChat
    offline_msg={
        'type':'Offline',
        'sender':userInfo['Mobile']
    }
    data = pickle.dumps(offline_msg)
    client.send(data)
    activeChat = False

def msg_receiver(mydb,cursor,userInfo,clientObj):
    'This thread will keep receiving message from server'
    global activeChat, activeChatThread
    while True:
        data = clientObj.recv(2048)
        msg = pickle.loads(data)
        activeChat = True
        if msg.get('type') == 'Status':
            contacts = msg.get('contacts')
            for cont,status in contacts.items():
                if status == 'Offline':
                    user_status = "UPDATE {} SET status = {} WHERE  contacts={}".format(userInfo['contactsTable'],1,cont)
                else:
                    user_status = "UPDATE {} SET status = {} WHERE  contacts={}".format(userInfo['contactsTable'],2,cont)
                update_data(mydb,cursor,user_status)
        if msg.get('type') == '404':
            print('<<< {} >>>'.format(msg['message']))
            activeChat = False
        if msg.get('type') == 'MessagRecv':
            sender = str(msg.get('sender'))
            #print("Message Received from <{}>".format(user))

            sender_info = ("INSERT INTO {} (time,contacts, status, reply_status, message) VALUES (%(time)s, %(contacts)s, %(status)s,%(reply_status)s, %(message)s)".format(userInfo['mainTable']))
            print(sender_info)
            sender_params = {
                'time':str(msg.get('time')),
                'contacts':sender,
                'status':'Online',
                'reply_status':'no',
                'message':msg.get('message')
            }
            insert_data(mydb,cursor,sender_info, sender_params)
            print("{}[{}]:{}".format(msg['sender'],msg['time'],msg['message']))
            if activeChatThread == False:
                msg_sender(mydb,cursor,userInfo, sender)
        

def contacts_status(mydb,cursor,userInfo,client):
   # print('Keep running and checking about all contacts Online Status')
    while True:
        query="select contacts,status from {}".format(userInfo['contactsTable'])
        result = query_table(mydb,cursor,query,userInfo['contactsTable'])
        online_check={
            'type':'Status',
            'sender':userInfo['Mobile']
            }
        contacts={}
        if len(result) != 0:
            for i in result:
                contacts[i[0]] = i[1]
            online_check['contacts'] = contacts
            data=pickle.dumps(online_check)
            client.send(data)

        time.sleep(3)

def connectServer(mydb,cursor,userInfo):
    try:
        client.connect(('127.0.0.1', 1234)) 
    except:
        print("Server connection is not established")
        return
    
    #Notify to server you are online now :)
    lTime = time.asctime()
    helloMsg = {'type':'Online','user':userInfo['Mobile'], 'time':lTime}
    data = pickle.dumps(helloMsg)
    client.send(data)
    # Create two threads as follows
    # 1. To Listen all incoming message
    # 2. Periodically check with server for its Contacts Online Status
    try:
        _thread.start_new_thread( msg_receiver, (mydb,cursor,userInfo, client) )
        _thread.start_new_thread( contacts_status, (mydb,cursor,userInfo, client ) )
    except:
        print ("Error: unable to start thread")

def client_start(mydb,cursor,userInfo):
    global activeChat
    connectServer(mydb,cursor,userInfo)
    while True:
        if activeChat == False:
            op = menu()
            if op == 1:
                add_buddies(mydb,cursor,userInfo)
            elif op == 2:
                delete_buddies(userInfo)
            elif op == 3:
                newMessages(mydb,cursor,userInfo)
            elif op == 4:
                onlineBuddies(mydb,cursor,userInfo)
            elif op == 5:
                goOffline(userInfo)
            
        time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) != 2: #check for Command Line Arguments 
        print("Pass any of client Name as an Argument")
        print(return_client_list())
        sys.exit(1)
    
    userInfo=getAllClientDetails(sys.argv[1])
    print(userInfo)
    try:
        mydb = mysql.connector.connect(host=userInfo['IP'],user='root',database=DB_NAME)
        cursor = mydb.cursor()
    except mysql.connector.Error as err:
        mydb = mysql.connector.connect(host=userInfo['IP'],user='root')
        cursor = mydb.cursor()
        create_database(cursor,DB_NAME)
    
    db_init(mydb,cursor,MAIN_TABLE_DISCRIPTON.format(userInfo['mainTable']),userInfo['mainTable'],DB_NAME)
    #Create Contact Table where all contacts entries are made
    createTable(cursor,CONTACT_TABLE_DISCRIPTON.format(userInfo['contactsTable']),userInfo['contactsTable'])
    #Start The Client main Operation
    client_start(mydb,cursor,userInfo)

    while True:
        time.sleep(10000)
        pass