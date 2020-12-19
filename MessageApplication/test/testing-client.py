import socket
import _thread
import time
import json
import pickle

import tkinter

if __name__ == '__main__':
    
    ip = '127.0.0.1'
    port = 2221
    
    
    while True:
        port = int(input('Enter Port:'))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.bind((ip,port))
        sender = input("Sender Id:")
        try:
            client.connect(('127.0.0.1', 1234))
        except:
            print("Already Connected")
            pass
        lTime = time.asctime()
        helloMsg = {'type':'Online','user':sender, 'time':lTime}
        data = pickle.dumps(helloMsg)
        client.send(data)
        msg = input("Enter Text :")

        lTime = time.asctime()
        message = {
            'type':'MessageSend',
            'sender':sender,
            'time':str(lTime),
            'receiver':'7091728998',
            'message':msg

        }
        payLoad = pickle.dumps(message)
        client.send(payLoad)
