from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import ssl, mimetypes, traceback, os, io
from sys import argv; import json, random, mysql.connector
from networkx import is_connected
from sqlvalidator.sql_validator import parse as SQLParse
# from adduser import addUser
import socket
from urllib.parse import unquote
import re; from datetime import datetime; from time import time
WEB_ROOT = '../website'

class ticketType(Enum):
	NewUser = "newUser"
	NewTicket = "newTicket"

def logger(Data, title=None):
	if not title:
		title = "Activity Log"
	try:
		if isinstance(Data, dict):
			data = Data.copy()
		else:
			data = getattr(Data, '__dict__', Data)
			data = data.copy() if isinstance(data, (dict, list)) else data
		cleaned_data = {}
		if isinstance(data, dict):
			for key, value in data.items():
				if isinstance(value, (io.BufferedReader, socket.socket)):
					cleaned_data[key] = str(value)
				elif callable(value):
					cleaned_data[key] = str(value)
				elif isinstance(value, bytes):
					cleaned_data[key] = value.decode('utf-8', errors='ignore')
				elif isinstance(value, str):
					try: value = json.loads(value)
					except json.JSONDecodeError:
						pass
					cleaned_data[key] = value
				else: cleaned_data[key] = str(value)
		else: cleaned_data = data
		with open('./log', 'a') as log:
			current_time = datetime.now().strftime("%d %B %Y, %I:%M%p")
			log_entry = f"{current_time}\n{title}:\n{json.dumps(cleaned_data, indent=4, default=lambda o: str(o))}\n{'-' * 50}\n"
			log.write(log_entry)
	except Exception as e:
		print(f"Error logging user activity: {str(e)}")
		raise
	finally:
		log.close()

class SQLConnector():
	DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'','database':'ticketdb'}
	EMAIL_REGEX = r'^(?!\.)[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$'
	SQL_RESTRICTED = {
		'chars': [';', '\\', '*', '`', '$', '#', '!', '{', '}', '(', ')', ' ', '"', "'", '-', '/'],
		'keywords': ['EXEC', 'SELECT', 'WHERE', 'LIKE', 'HAVING', 'OFFSET', 'INSERT', 'DELETE', 'CREATE', 'DROP', 'GRANT', 'REVOKE', 'UNION']
	}

	@staticmethod
	def SQLINJECTIONCHECK(string: str):
		has_restricted = SQLConnector.HasSQLChars(string)
		is_valid_sql = SQLParse(string).is_valid()
		if is_valid_sql or has_restricted:
			return [False, 403]
		else:
			return [True, 202]

	@staticmethod
	def EmailIsValid(email: str) -> bool:
		if not re.match(SQLConnector.EMAIL_REGEX, email):
			return False
		return not SQLConnector.HasSQLChars(email)
		# return True

	@staticmethod
	def HasSQLChars(string: str) -> bool:
		string_lower_clean = string.lower().replace('\t', '').replace('\n', '')
		for char in SQLConnector.SQL_RESTRICTED['chars']:
			if char in string:
				return True
		for kw in SQLConnector.SQL_RESTRICTED['keywords']:
			if kw.lower() in string_lower_clean.split():
				return True
		return False

	@staticmethod
	def validateLogin(email: str, password_hash: str):
		try:
			testP = SQLConnector.SQLINJECTIONCHECK(password_hash)
			if not testP[0]:
				return [False, 403, "Forbidden: SQL Injection detected"]
			testE = SQLConnector.EmailIsValid(email)
			if not testE:
				return [False, 403, "Forbidden: Invalid email format"]
			if not testP[0]:
				return testP
			if not testE:
				return [False, 403, "Invalid email format"]
			connection = mysql.connector.connect(**SQLConnector.DB_CONFIG)
			cursor = connection.cursor()
			with open('../backend/userfetch.sql') as script:
				base_sql = script.read().strip()
			filtered_sql = f"{base_sql} WHERE email = '{email}'"
			cursor.execute(filtered_sql)
			data = cursor.fetchall()
			row = data[0] if data else None
			cursor.close()
			connection.close()
			script.close()
			login_attempt = {
				'email': email,
				'timestamp': datetime.now().strftime("%d %B %Y, %I:%M%p")
			}
			if row:
				user_id, username, user_email, db_pw_hash = row
				if db_pw_hash == password_hash:
					login_attempt.update({
						'status': 'success',
						'userid': user_id,
						'username': username
					})
					logger(login_attempt, "Active Login Attempt")
					return [True, 200, user_id]
			login_attempt['status'] = 'failed'
			logger(login_attempt, "Active Login Attempt")
			return [False, 400, "Login failed"]
		except ConnectionError as e:
			print(str(e))
			return [False, 500, "Connection error"]
		except mysql.connector.Error as e:
			error_msg = str(e).lower()
			if "syntax" in error_msg or "sql" in error_msg:
				return [False, 403, "Forbidden: SQL error detected"]
			return [False, 500, "Database error"]
		except IndexError or TypeError or ValueError as e:
			print(str(e))
			return [False, 400, "Value error"]
		except Exception as e:
			print(str(e))
			return [False, 404, "General error"]



	@staticmethod
	def getTickets():
		try:
			connection = mysql.connector.connect(**SQLConnector.DB_CONFIG)
			cursor = connection.cursor()
			with open('../backend/ticketfetch.sql') as script:
				sql = script.read()
				cursor.execute(str(sql))
				data = cursor.fetchall()
				cursor.close(); connection.close(); script.close()
			tickets = []
			for row in data:
				# print(f"temp: {temp}")
				ticket = {
					'ticketID': int(row[0]),
					'userID': int(row[1]),
					'title': row[2],
					'description': row[3]
				}
				logger(ticket, "Ticket GET data")
				tickets.append(ticket)
			return [True, 200, tickets]
		except ConnectionError as e: logger(e, "DB failure"); return [False, 500]
		except mysql.connector.Error as e: logger(e, "DB failure"); return [False, 500]
		except IndexError or TypeError or ValueError: return [False, 400]
		except Exception: return [False, 404]

	@staticmethod
	def addTicket(type = ticketType.NewTicket, ticketData = []):
		try:
			if type == ticketType.NewUser:
				script = """INSERT INTO tickets (title, description) VALUES (%s, %s)"""
				values = ('Add new User', ticketData)
			else:
				user_id = ticketData[2]
				script = """INSERT INTO tickets (users_userID, title, description) VALUES (%s, %s, %s)"""
				values = (user_id, ticketData[0], ticketData[1])

			connection = mysql.connector.connect(**SQLConnector.DB_CONFIG)
			if connection.is_connected():
				cursor = connection.cursor()
				cursor.execute(script, values)
				connection.commit()
				cursor.close()
				connection.close()
			return [True, 201]
		except ConnectionError as e: 
			logger(e, "DB failure")
			return [False, 500]
		except mysql.connector.Error as e: 
			logger(e, "DB failure")
			return [False, 500]
		except IndexError or TypeError or ValueError: 
			return [False, 400]
		except Exception as e:
			logger(e, "Unexpected failure")
			return [False, 500]

class VerificationTracker:
	length = 20; number = 0; kmax = 2
	keyArray = [{'key': "",'initialTime': 0, 'uid':0} for _ in range(kmax)]
	choices = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','&','@','=','>','<','^']
	timeout = 60*5 # 5 min in seconds

	@staticmethod
	def newKey(userid: int):
		current_time = int(time())
		for i in range(VerificationTracker.kmax):
			entry = VerificationTracker.keyArray[i]
			if entry['key'] and (current_time - entry['initialTime']) >= VerificationTracker.timeout:
				VerificationTracker.keyArray[i] = {'key': "", 'initialTime': 0, 'uid': 0}
				if VerificationTracker.number > 0:
					VerificationTracker.number -= 1
		if VerificationTracker.number >= VerificationTracker.kmax:
			return None
		start = ''.join(random.choice(VerificationTracker.choices) for _ in range(VerificationTracker.length))
		for i in range(VerificationTracker.kmax):
			if VerificationTracker.keyArray[i]['key'] == "":
				VerificationTracker.keyArray[i] = {
					'key': start,
					'initialTime': current_time,
					'uid': userid
				}
				VerificationTracker.number += 1
				logger(VerificationTracker.keyArray[i], f"Key registration for user {userid}, keyarray index {i}")
				logger(VerificationTracker.keyArray, "Key array state")
				return i
		return None  # Should rarely occur

	@staticmethod
	def checkKeyValidity(key: str):
		for x in range(len(VerificationTracker.keyArray)):
			if key == VerificationTracker.keyArray[x]['key']:
				if abs(int(time()) - VerificationTracker.keyArray[x]['initialTime']) < VerificationTracker.timeout:
					return [True, 202, {'userid_hash':VerificationTracker.keyArray[x]['uid']}]
				else:
					VerificationTracker.keyArray[x] = {'key': "", 'initialTime': 0, 'uid': 0}
					VerificationTracker.number -= 1
		return [False, 401]

class apiHandler(str):
	@staticmethod
	def postRequestHandler(endpoint: str, data: bytes):
		target = endpoint.removeprefix('/api/0/POST/')
		postd = json.loads(data.decode('utf-8'))
		
		logger({"Raw JSON parsed": postd}, title="Parsed POST")
		logger({"Data": data.decode("utf-8")}, title="POST request data")

		if target == 'login':
			try:
				email = postd.get('email')
				pw_hash = postd.get('password_hash')
				if not email or not pw_hash:
					return [False, 400]
			except Exception as e:
				return [False, 400, str(e)]

			# Validate inputs
			email_valid = SQLConnector.EmailIsValid(email)
			sql_check = SQLConnector.SQLINJECTIONCHECK(pw_hash)

			if not email_valid:
				return [False, 403, "Invalid email format"]
			if not sql_check[0]:
				return sql_check + ["SQL injection detected"]

			# Validate login
			user = SQLConnector.validateLogin(email, pw_hash)
			if not user[0]:
				return [False, user[1], "Login failed"]

			# Generate new key
			key_index = VerificationTracker.newKey(user[2])
			if key_index is None:
				return [False, 507, "Unable to create new key"]

			return [
				True,
				200,
				{
					'userid': user[2],
					'auth_key': VerificationTracker.keyArray[key_index]['key'],
					'expires_in': VerificationTracker.timeout
				}
			]

		elif target == 'data':
			try:
				key = postd.get('key')
				title = postd.get('title')
				description = postd.get('description')
				if not all([key, title, description]):
					return [False, 400, "Missing required fields"]
			except Exception as e:
				return [False, 400, str(e)]

			# Validate key
			key_valid = VerificationTracker.checkKeyValidity(key)
			if not key_valid[0]:
				return [False, 401, "Invalid or expired key"]

			user_id = key_valid[2]['userid_hash']

			# Validate inputs
			sql_title = SQLConnector.SQLINJECTIONCHECK(title)
			sql_description = SQLConnector.SQLINJECTIONCHECK(description)

			if not sql_title[0] or not sql_description[0]:
				return [False, 403, "SQL injection detected"]

			# Add ticket, now with user_id
			ticket_added = SQLConnector.addTicket(ticketData=[title, description, user_id])
			if not ticket_added[0]:
				return [False, ticket_added[1], "Ticket creation failed"]

			return [True, 201, {"message": "Ticket created successfully"}]

		elif target == 'newuser':
			try:
				email = postd.get('email')
				pw_hash = postd.get('pw_hash')
				commonName = postd.get('commonName', '')
				if not email or not pw_hash:
					return [False, 400, "Missing required fields"]
			except Exception as e:
				return [False, 400, str(e)]

			# Validate inputs
			email_valid = SQLConnector.EmailIsValid(email)
			sql_email = SQLConnector.SQLINJECTIONCHECK(email)
			sql_pw = SQLConnector.SQLINJECTIONCHECK(pw_hash)

			if not email_valid:
				return [False, 403, "Invalid email format"]
			if not sql_email[0] or not sql_pw[0]:
				return [False, 403, "SQL injection detected"]

			# Add new user ticket
			user_ticket = SQLConnector.addTicket(type=ticketType.NewUser,
												ticketData=[email, pw_hash, commonName])
			if not user_ticket[0]:
				return [False, user_ticket[1], "User creation failed"]

			return [True, 201, {"message": "New user ticket created successfully"}]

		else:
			return [False, 418, "Invalid endpoint"]

	@staticmethod
	def getRequestHandler(endpoint: str):
		target = endpoint.removeprefix('/api/0/GET/')

		logger(target, "GET ticket request URI")

		if target.startswith('data'):
			try:
				key = target.removeprefix('data?key=')
				if not key:
					return [False, 400, "Missing auth key"]
			except Exception as e:
				return [False, 400, str(e)]

			# Validate key
			key_valid = VerificationTracker.checkKeyValidity(key)
			if not key_valid[0]:
				return [False, 401, "Invalid or expired key"]

			# Get tickets
			ticket_data = SQLConnector.getTickets()
			if not ticket_data[0]:
				return [False, ticket_data[1], "Failed to retrieve tickets"]

			return [True, 200, ticket_data[2]]

		else:
			return [False, 418, "Invalid endpoint"]

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self): # API Endpoints
		logger(self)
		if self.path.startswith('/api/0/GET/'):
			response = apiHandler.getRequestHandler(endpoint = unquote(self.path))
			self.send_response(response[1])
			logger(response, "GET response")
			self.send_header('Content-Type', 'application/json')
			response_size = len(str(response[2])) if len(response) >= 3 else 0
			self.send_header('Content-length', str(response_size))
			self.end_headers();
			if len(response) >=3: self.wfile.write(str(response[2]).encode('utf-8'))
			return
		elif self.path.startswith('/api'):
			self.send_response(418)
			self.send_header('Content-length', '0')
			self.end_headers()
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee")
			logger([418, self.wfile], "POST response")

		else:
			# Serve index.html for root
			if self.path == ('/' or ''):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				with open(WEB_ROOT+'/dashboard.html', 'rb') as file:
					html_content = file.read()
				file_size = len(html_content)
				self.send_header('Content-length', str(file_size))
				self.end_headers()
				self.wfile.write(html_content)
				logger(200, "GET response")
			elif self.path == '/favicon.png':
				# favicon handler
				self.send_response(200)
				self.send_header('Content-Type', 'image/x-icon')
				file_size = os.path.getsize(WEB_ROOT+'/assets/graphics/favicon.png')
				self.send_header('Content-length', str(file_size))
				self.end_headers()
				with open(WEB_ROOT+'/assets/graphics/favicon.png', 'rb') as favicon_file:
					favicon_data = favicon_file.read()
					self.wfile.write(favicon_data)
					logger(200, "GET response")
			elif '.' not in self.path:
				# Serve static html files
				requested_path = f"{self.path.lstrip('/')}.html"
				file_path = os.path.join(WEB_ROOT, requested_path)

				if os.path.isfile(file_path):
					self.send_response(200)
					mime_type, _ = mimetypes.guess_type(file_path)
					self.send_header('Content-type', mime_type or 'application/octet-stream')
					file_size = os.path.getsize(file_path)
					self.send_header('Content-length', str(file_size))
					self.end_headers()
					with open(file_path, 'rb') as f:
						self.wfile.write(f.read())
					logger(200, "GET response")
				else:
					self.send_response(404)
					self.send_header('Content-type', 'text/plain')
					self.send_header('Content-length', '0')
					self.end_headers()
					self.wfile.write(b"404 Not Found")
					logger([404, self.wfile], "GET response")
			else:
				# Serve static files from /css, /js, etc.
				requested_path = self.path.lstrip('/')
				file_path = os.path.join(WEB_ROOT, requested_path)

				if os.path.isfile(file_path):
					self.send_response(200)
					mime_type, _ = mimetypes.guess_type(file_path)
					self.send_header('Content-type', mime_type or 'application/octet-stream')
					file_size = os.path.getsize(file_path)
					self.send_header('Content-length', str(file_size))
					self.end_headers()
					with open(file_path, 'rb') as f:
						self.wfile.write(f.read())
					logger(200, "GET response")
				else:
					self.send_response(404)
					self.send_header('Content-type', 'text/plain')
					self.send_header('Content-length', '0')
					self.end_headers()
					self.wfile.write(b"404 Not Found")
					logger([404, self.wfile], "GET response")

	def do_POST(self):
		logger(self)
		if self.path.startswith('/api/0/POST/'):
			try:
				content_length = int(self.headers['Content-Length'])
			except Exception:
				self.send_response(411)
				self.end_headers()
				return
			post_data = self.rfile.read(content_length)
			response = apiHandler.postRequestHandler(endpoint=self.path, data=post_data)
			self.send_response(response[1])
			self.send_header('Content-Type', 'application/json')
			if len(response) >= 3:
				body = json.dumps(response[2]).encode('utf-8')
				self.send_header('Content-Length', str(len(body)))
			else:
				body = b''
				self.send_header('Content-Length', '0')
			self.end_headers()
			if body:
				self.wfile.write(body)
			logger(response, "POST response")
		else:
			self.send_response(418)
			self.end_headers()
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee")
			logger([418, self.wfile], "POST response")

	def do_HEAD(self): # Last required method
		logger(self, "Raw request data - HEAD")
		if '.' not in self.path:
			# Static html files
			requested_path = f'{self.path.lstrip('/')}.html'
			file_path = os.path.join(WEB_ROOT, requested_path)

			if os.path.isfile(file_path):
				self.send_response(200)
				mime_type, _ = mimetypes.guess_type(file_path)
				self.send_header('Content-type', mime_type or 'application/octet-stream')
				file_size = os.path.getsize(file_path)
				self.send_header('Content-length', str(file_size))
				self.end_headers()
			else:
				self.send_response(404)
				self.send_header('Content-type', 'text/plain')
				self.send_header('Content-length', '0')
				self.end_headers()
		else:
			# Static files from /css, /js, etc.
			requested_path = self.path.lstrip('/')
			file_path = os.path.join(WEB_ROOT, requested_path)

			if os.path.isfile(file_path):
				self.send_response(200)
				mime_type, _ = mimetypes.guess_type(file_path)
				self.send_header('Content-type', mime_type or 'application/octet-stream')
				file_size = os.path.getsize(file_path)
				self.send_header('Content-length', str(file_size))
				self.end_headers()
			else:
				self.send_response(404)
				self.send_header('Content-type', 'text/plain')
				self.send_header('Content-length', '0')
				self.end_headers()

def run():
	try:
		# subprocess.run('start "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Wampserver64\Wampserver64.lnk"')

		SSLOn = True if (argv[1].lower() if len(argv) > 1 else input("Use TLS? (y/n) > ").strip().lower()) in ("y", "yes", "tls") else False
		portq = 4443 if SSLOn else 8008
		if (SSLOn):
			handler = RequestHandler
			server = HTTPServer(('', portq), handler)

			certchain = '../certs/server_chain.pem'
			keyfile = '../certs/serverkey.pem'

			context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			context.load_cert_chain(certfile = certchain, keyfile = keyfile)

			server.socket = context.wrap_socket(server.socket, server_side=True)
			print(f"Server running with SSL/TLS")
			print(f'Local: 127.0.0.1:{portq}')
			server.serve_forever()

		else:
			handler = RequestHandler
			server = HTTPServer(('', portq), handler)

			print("Server running")
			print(f'Local: 127.0.0.1:{portq}')
			server.serve_forever()

	except ssl.SSLError as e:
		print(f"SSL Error: {e}")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	# # Create a self-signed certificate if you don't have one (for testing only) // only gonna work with openssl and even then prob only linux
	# if not path.exists('server.pem'):
	# 	print("Generating self-signed certificate...")
	# 	subprocess.run("openssl req -x509 -newkey rsa:4096 -keyout server.pem -out server.pem -nodes -days 365", shell=True)

	run()
