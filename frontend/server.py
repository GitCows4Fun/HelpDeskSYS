from http.server import BaseHTTPRequestHandler, HTTPServer; from math import trunc
import ssl, mimetypes, traceback, os, io 
from sys import argv; import json, random, mysql.connector 
from sqlvalidator.sql_validator import parse as SQLParse 
# from adduser import addUser 
from socketserver import _SocketWriter as socketwrite
import re; from datetime import datetime; from time import time 
WEB_ROOT = '../website' 

def logger(Data, title = None): 
	if not title: title = "Activity Log" 
	try: 
		if isinstance(Data, dict): 
			data = Data.copy() 
		else: 
			data = getattr(Data, '__dict__', Data) 
			data = data.copy() if isinstance(data, (dict, list)) else data 
		cleaned_data = {} 
		if isinstance(data, dict): 
			for key, value in data.items(): 
				if not isinstance(value, (io.BufferedReader, socketwrite)): 
					if callable(value): 
						cleaned_data[key] = str(value) 
					else: 
						cleaned_data[key] = value 
		else: 
			cleaned_data = data 
		with open('./userauth.log', 'a') as log: 
			current_time = datetime.now().strftime("%d %B %Y, %I:%M%p") 
			log_entry = f"{current_time}\n{title}:\n{json.dumps(cleaned_data, indent=4, default=lambda o: str(o))}\n{'-' * 50}\n" 
			log.write(log_entry) 
	except Exception as e: 
		print(f"Error logging user activity: {str(e)}") 
		raise 
	finally: log.close() 

class SQLConnector(): 
	DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'','database':'ticketdb'} 
	EMAIL_REGEX = r'^(?!\.)[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$' 
	SQL_RESTRICTED = { 
		'chars': [';', '\\', '*', '`', '$', '#', '!', '{', '}', '(', ')'], 
		'keywords': ['EXEC', 'SELECT', 'WHERE', 'LIKE', 'HAVING', 'OFFSET', 'INSERT', 'DELETE', 'CREATE', 'DROP', 'GRANT', 'REVOKE'] 
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
		string_lower = string.lower()
		for char in SQLConnector.SQL_RESTRICTED['chars']: 
			if char in string: 
				return True 
		for kw in SQLConnector.SQL_RESTRICTED['keywords']: 
			if kw.lower() in string_lower.split():
				return True 
		return False 

	@staticmethod 
	def validateLogin(email: str, password_hash: str): 
		try: 
			testP = SQLConnector.SQLINJECTIONCHECK(password_hash) 
			testE = SQLConnector.EmailIsValid(email) 
			if not testP[0]: 
				return testP 
			if not testE: 
				return [False, 403] 
			connection = mysql.connector.connect(**SQLConnector.DB_CONFIG) 
			cursor = connection.cursor() 
			with open('../backend/userfetch.sql') as script:
				sql = script.read() 
				cursor.execute(sql) 
				data = cursor.fetchall() 
				cursor.close(); connection.close(); script.close() 
			users = [] 
			for row in data:
				temp = ''.join(''.join(str(row).strip().removeprefix('(').removesuffix(')').split(' ')).split("'")).split(',') 
				print(f"temp: {temp}"); logger(temp, "Login data") 
				users.append({'userid':temp[0],'commonName':temp[1],'email':temp[2],'pw_hash':temp[3]}) 
			for i in range(len(users)): 
				if email == users[i]['email'] and password_hash == users[i]['pw_hash']: 
					return [True, 200, users[i]['userid']] 
			return [False, 400] 
		except ConnectionError as e: print(str(e)); return [False, 500] 
		except mysql.connector.Error as e: print(str(e)); return [False, 500] 
		except IndexError or TypeError or ValueError as e: print(str(e)); return [False, 400] 
		except Exception as e: print(str(e)); return [False, 404] 

	@staticmethod 
	def getTickets(): 
		try:
			connection = mysql.connector.connect(**SQLConnector.DB_CONFIG) 
			cursor = connection.cursor() 
			with open('../backend/ticketfetch.sql') as script: 
				sql = script.read() 
				cursor.execute(str(sql)) 
				data = cursor.fetchall() 
				cursor.close; connection.close(); script.close() 
			tickets = [] 
			for row in data: 
				temp = ''.join(str(row).strip().removeprefix('(').removesuffix(')').split(' ')).split(',') 
				print(f"temp: {temp}") 
				tickets.append({'ticketID':int(temp[0]), 'userID':int(temp[1]), 'title':temp[2], 'description':temp[3]}) 
			return [True, 200, tickets] 
		except ConnectionError: return [False, 500] 
		except mysql.connector.Error: return [False, 500] 
		except IndexError or TypeError or ValueError: return [False, 400] 
		except Exception: return [False, 404] 

class VerificationTracker: 
	length = 20; number = 0; kmax = 2 
	keyArray = [{'key':"",'initialTime': 0, 'uid':0} for _ in range(kmax)] 
	choices = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','!','#','%','&','@','$','=','>','<','^','*'] 
	timeout = 60*5 # 5 min in seconds 

	@staticmethod 
	def newKey(userid: int):
		if VerificationTracker.number >= VerificationTracker.kmax: return False 
		start = ''.join(random.choice(VerificationTracker.choices) for _ in range(VerificationTracker.length)) 
		VerificationTracker.keyArray[VerificationTracker.number] = { 
			'key': start, 
			'initialTime': int(time()), 
			'uid': userid 
		} 
		logger(VerificationTracker.keyArray[VerificationTracker.number], "Key registration") 
		VerificationTracker.number += 1 
		return True 

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
		if target == 'login': 
			try: 
				email = postd.get('email') 
				pw_hash = postd.get('password_hash') 
			except Exception: return [False, 400] 
			teste = SQLConnector.EmailIsValid(email) 
			testph = SQLConnector.SQLINJECTIONCHECK(pw_hash) 
			if not teste: print('E: '+email);print(teste); return teste 
			elif not testph[0]: print('P: '+pw_hash);print(testph); return testph 
			user = SQLConnector.validateLogin(email, pw_hash) 
			if not user[0]: return user 
			return [user[0], user[1], [{'key':VerificationTracker.keyArray[VerificationTracker.newKey(user[2])]['key'],'userid':user[2]}]] if user[0] else [user[0], user[1]] 
		else: 
			postd = json.loads(data.decode('utf-8')) 
			testd = SQLConnector.SQLINJECTIONCHECK(postd.get('key')) 
			if not testd[0]: return testd 
			if VerificationTracker.checkKeyValidity(postd.get('key'))[0]: 
				match target:
					case 'ticket': '' 

	@staticmethod 
	def getRequestHandler(endpoint: str, data: bytes): 
		target = endpoint.removeprefix('/api/0/GET/') 
		getd = json.loads(data.decode('utf-8')) 
		if VerificationTracker.checkKeyValidity(getd.get('key')): 
			testD = SQLConnector.SQLINJECTIONCHECK(getd.get('key')) 
			if not testD[0]: return testD 
			match target: 
				case 'data': #! Interface with sql db based on bytes(data) 
					ticketdata = SQLConnector.getTickets() # dict 
					if not ticketdata[0]:
						return 
					return [True, 200, ticketdata[2]] 

class RequestHandler(BaseHTTPRequestHandler): 
	def do_GET(self): # API Endpoints 
		logger(self, "Raw request data") 
		if self.path.startswith('/api/0/GET/'): 
			try: content_length = int(self.headers['Content-Length']) 
			except Exception: self.send_response(411); self.end_headers(); return 
			get_data = self.rfile.read(content_length) 
			response = apiHandler.getRequestHandler(endpoint = self.path, data = get_data) 
			self.send_response(response[1]) 
			self.send_header('Content-Type', 'application/json') 
			response_size = len((response[2]).encode('utf-8')) if len(response) >= 3 else 0 
			self.send_header('Content-length', str(response_size)) 
			self.end_headers(); 
			if len(response) >=3: self.wfile.write((response[2]).encode('utf-8')) 
			return 
		elif self.path.startswith('/api'): 
			self.send_response(418) 
			self.send_header('Content-length', '0') 
			self.end_headers() 
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee") 

		else: 
			# Serve index.html for root 
			if self.path == ('/' or ''): 
				self.send_response(200) 
				self.send_header('Content-type', 'text/html') 
				file_size = os.path.getsize(WEB_ROOT+'/index.html') 
				self.send_header('Content-length', str(file_size)) 
				self.end_headers() 
				with open(WEB_ROOT+'/index.html', 'r') as file: 
					html_content = file.read().encode('utf-8') 
					self.wfile.write(html_content) 
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
			elif '.' not in self.path: 
				# Serve static html files 
				requested_path = f'{self.path.lstrip('/')}.html' 
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
				else: 
					self.send_response(404) 
					self.send_header('Content-type', 'text/plain') 
					self.send_header('Content-length', '0') 
					self.end_headers() 
					self.wfile.write(b"404 Not Found") 
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
				else: 
					self.send_response(404) 
					self.send_header('Content-type', 'text/plain') 
					self.send_header('Content-length', '0') 
					self.end_headers() 
					self.wfile.write(b"404 Not Found") 

	def do_POST(self): # API Endpoints 
		logger(self, "Raw request data") 
		if self.path.startswith('/api/0/POST/'): 
			try: content_length = int(self.headers['Content-Length']) 
			except Exception: self.send_response(411); self.end_headers(); return 
			post_data = self.rfile.read(content_length) 
			# self.send_header('Content-type', 'text/html') 
			response = apiHandler.postRequestHandler(endpoint = self.path, data = post_data, client=self) 
			self.send_response(response[1]); self.send_header('Content-Type', 'application/json') 
			if len(response)>3: self.send_header('Content-Length', len(str(response))) 
			self.end_headers() 
			if len(response)>3: self.wfile.write(response[2].encode('utf-8')) 
			return 
		else: 
			self.send_response(418) 
			self.end_headers() 
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee"); return 

	def do_HEAD(self): # Last required method 
		logger(self, "Raw request data") 
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
