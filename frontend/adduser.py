# i=__import__;n=input;a=i('sys').argv;e,c,p=(a[1:4]+[""]*3)[:3];e=e or n('Email:');c=c or n('Name:');p=p or n('Pass:');w=i('hashlib').sha256(p.encode()).hexdigest();d={'host':'localhost','user':'root','database':'ticketdb'};c=i('mysql.connector').connect(**d);r=c.cursor();r.execute(f"INSERT INTO users(commonName,email,passwordHash)VALUES('{c}','{e}','{w}')");c.commit();r.close();c.close()

import mysql.connector; import hashlib; from sys import argv 

def addUser(email='', commonName='', password=''): 
    if not email: email = input('Email Address: ') 
    if not commonName: commonName = input('Name: ') 
    if not password: password = input('Password: ') 

    hashobj = hashlib.sha256() 
    hashobj.update(password.encode('utf-8')) 
    pw_hash = hashobj.hexdigest() 

    dbConf = {'host':'localhost','user':'root','password':'','database':'ticketdb'} 
    script = f"""
INSERT INTO users (commonName, email, passwordHash) 
VALUES ('{commonName}', '{email}', '{pw_hash}');
""" 
    try: 
        conn = mysql.connector.connect(**dbConf) 
        if conn.is_connected(): 
            print("Connected to MySQL") 
            cur = conn.cursor() 
            cur.execute(script) 
            conn.commit() 
            print("Data added successfully") 
        cur.close() 
        conn.close() 
    except mysql.connector.Error as e: 
        print(f"Error connecting to MySQL: {e}") 
    except Exception as e: 
        print(f"An error occurred: {e}") 

if __name__ == "__main__": 
    if (len(argv) <= 3 and len(argv) > 1) or len(argv) > 4: 
        print('Usage:\temail\tcommonName\tpassword') 
    else: 
        if len(argv) ==4: 
            addUser(argv[1], argv[2], argv[3]) 
        else: addUser() 
