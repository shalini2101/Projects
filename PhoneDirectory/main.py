import sys
import pandas as pd
from colorama import Fore, Back, Style 

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
    userFlag = False
    with open(FILE_NAME) as ctx:
        line = ctx.readline()
        while line:
            data = eval(line)
            if data['name'] == find_name:
                df = pd.DataFrame(data,index=[0])
                print(df)
                userFlag = True

            line = ctx.readline()
    if userFlag == False:
        print(Fore.RED+Style.BRIGHT+"User You are Looking for is not present in current Directory")
        print(Style.RESET_ALL)

        
        
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
        userFlag = False
        for line in lines:
            ln = line.strip("\n")
            data = eval(ln)
            if data['name'] == objDel or data['mob'] == objDel:
                line = fd.readline()
                print(Fore.GREEN +"User {} Deleted Successfully".format(data['name']))
                print(Style.RESET_ALL)
                userFlag = True
                continue
            fd.write(line)
            line = fd.readline()
    if userFlag == False:
        print(Fore.RED+Style.BRIGHT+"User You are Looking for is not present in current Directory")

        print(Style.RESET_ALL)
        return
        
    display_all()
        
     
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
        elif op == 0:
            print("See You Again...")
            sys.exit(0)
        else:
            print(Fore.RED +Style.BRIGHT+"Wrong Choice")
            print(Style.RESET_ALL)
