import pickle
import json
import pandas as pd

FILE_NAME ="subscriber_mob_directory.txt"

def menu():
    print('+----------------+')
    print("1. Add User")
    print("2. Find User")
    print("3. Delete User")
    print("4. Display All User")
    op = int(input("Choose Option or '0' :"))
    return op

def add_user():
    name = input('Enter Name :')
    Mob = input("Enter Mobile :")
    Add = input("Address :")
    
    cust_id = 100000
    with open(FILE_NAME) as ctx:
        line = ctx.readline()
        
        while line:
            data = eval(line)
            cust_id = data['custid']
            line = ctx.readline()
    
    cust_id += 1
    context = {
        'custid':cust_id,
        'name':name,
        'mob':Mob,
        'add':Add
    }
  
    fo = open(FILE_NAME,'a+')
    fo.write(str(context)+'\n')
    fo.close() 

def find_user():
    find_name = input("Enter Name to search :")
    with open(FILE_NAME) as ctx:
        line = ctx.readline()
        
        while line:
            data = eval(line)
            if data['name'] == find_name:
                df = pd.DataFrame(data,index=[0])
                print(df)

            line = ctx.readline()
        
def display_all():
    print('+----------- All Users ------------+')
    print('{:<15} {:<20} {:<11} {:<15}'.format('Customer ID','Name','Mobile','Address'))
    with open(FILE_NAME) as ctx:
        line = ctx.readline()
        while line:
            data = eval(line)
            print('{:<15} {:<20} {:<11} {:<15}'.format(data['custid'],data['name'],data['mob'],data['add']))
            line = ctx.readline()
    print('+---------------------------------+')
    
def del_user():
    objDel = input('Enter Name/Mob :')

    with open(FILE_NAME,'r+') as fd:
        lines = fd.readlines()
        fd.seek(0)
        fd.truncate()
        print(lines)
        for line in lines:
            ln = line.strip("\n")
            data = eval(ln)
            print(data)
            if data['name'] == objDel or data['mob'] == objDel:
                line = fd.readline()
                continue
            fd.write(line)
            line = fd.readline()
        
     
if __name__ == '__main__' :
    
    while True:
        op = menu()

        if op == 1:
            add_user()
        elif op == 2:
            find_user()
        elif op == 3:
            del_user()
        elif op == 4:
            display_all()
        else:
            print("Wrong Choice")
