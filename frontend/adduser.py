# i=__import__;n=input;a=i('sys').argv;e,c,p=(a[1:4]+[""]*3)[:3];e=e or n('Email:');c=c or n('Name:');p=p or n('Pass:');w=i('hashlib').sha256(p.encode()).hexdigest();d={'host':'localhost','user':'root','database':'ticketdb'};c=i('mysql.connector').connect(**d);r=c.cursor();r.execute(f"INSERT INTO users(commonName,email,passwordHash)VALUES('{c}','{e}','{w}')");c.commit();r.close();c.close()

import mysql.connector; import hashlib; from sys import argv 

STANDARD_USERS=[['ADMIN01', 'admin01@helpdesk.sys', '35eb4a21e044648712b51f8224d77f194aa7d73c84baa5678686a3b2a0abfe0c'],
				['ADMIN02', 'admin02@helpdesk.sys', '8d7388e77acb50a36ecd18611b300a5376108486e22b5851aafbe20fc01580f9'],
				['ADMIN03', 'admin03@helpdesk.sys', '8586db554709d8ee78aa13675e011caeff12203f240935328c63d02332b22006']]
# These hashes are all X.2's OG pw seeded with num - gen with pw_gen.py 

def addUser(email='', commonName='', password=''): 
	dbConf = {'host':'localhost','user':'root','password':'','database':'ticketdb'} 

	hashobj = hashlib.sha256() 
	
	if not email: email = input('Email Address: ') 
	if not commonName: commonName = input('Name: ') 
	if not password: password = input('Password: ') 
	
	# Modified section for standard users
	if email.startswith("@STANDARD"):
		if input("Register standard users? > ").lower() == 'y':
			# Query the database to find the current maximum id
			try:
				conn = mysql.connector.connect(**dbConf)
				if conn.is_connected():
					print("Connected to MySQL")
					cur = conn.cursor()
					cur.execute("SELECT MAX(id) FROM users;")
					max_id = cur.fetchone()[0] or 0  # Get maximum id or 0 if no records
					cur.close()
					conn.close()
			except mysql.connector.Error as e:
				print(f"Error connecting to MySQL: {e}")
				max_id = 0  # Default to 0 if query fails

			# Assign new ids starting from max_id + 1
			for i in range(len(STANDARD_USERS)-1):
				user_id = max_id + i
				script = f"""
				INSERT INTO users (userID, commonName, email, passwordHash) 
				VALUES ({user_id}, '{STANDARD_USERS[i][0]}', '{STANDARD_USERS[i][1]}', '{STANDARD_USERS[i][2]}');
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

	else:
		# Query the database for the maximum existing id
		try:
			conn_query = mysql.connector.connect(**dbConf)
			if conn_query.is_connected():
				cur_query = conn_query.cursor()
				cur_query.execute("SELECT MAX(id) FROM users;")
				max_id = cur_query.fetchone()[0] or 0
				cur_query.close()
				conn_query.close()
		except:
			max_id = 0

		user_id = max_id + 1

		hashobj = hashlib.sha256()
		hashobj.update(password.encode('utf-8'))
		pw_hash = hashobj.hexdigest()

		script = f"""
		INSERT INTO users (userID, commonName, email, passwordHash)
		VALUES ({user_id}, '{commonName}', '{email}', '{pw_hash}');
		"""

		try:
			conn_insert = mysql.connector.connect(**dbConf)
			if conn_insert.is_connected():
				print("Connected to MySQL")
				cur_insert = conn_insert.cursor()
				cur_insert.execute(script)
				conn_insert.commit()
				print("Data added successfully")
			cur_insert.close()
			conn_insert.close()
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
