from http.server import BaseHTTPRequestHandler, HTTPServer; import ssl; import mimetypes 
import os; from sys import argv; import json, random, time, mysql.connector 
from sqlvalidator.sql_validator import parse as SQLParse 
WEB_ROOT = '../website' 

class SQLConnector(): 
	DB_CONFIGS = [{'host':'localhost','user':'root','password':'','database':'tickets'}, {'host':'localhost','user':'root','password':'','database':'users'}] 
	
	def SQLINJECTIONCHECK(string: str): 
		return [False, 403] if SQLParse(string).is_valid else [True, 202] 

	@staticmethod 
	def validateLogin(username: str, password_hash: str):
		try: 
			testU = SQLConnector.SQLINJECTIONCHECK(username); testP = SQLConnector.SQLINJECTIONCHECK(password_hash) 
			if not testU[0]: return testU 
			if not testP[0]: return testP 
			connection = mysql.connector.connect(**SQLConnector.DB_CONFIGS[1]) 
			cursor = connection.cursor() 
			with open('../backend/userfetch.sql') as script:
				cursor.execute(script) 
				data = cursor.fetchall() 
				cursor.close(); connection.close(); script.close() 
			users = [] 
			for row in data:
				temp = str(row).strip().removeprefix("(").removesuffix(")").split(',') 
				print(f"temp: {temp}")
				users.append({'username':temp[0],'userid':temp[1],'pw_hash':temp[2]}) 
			for i in range(len(users)): 
				if username == users[i]['username'] and password_hash == users[i]['pw_hash']: 
					return [True, 200, users[i]['userid']] 
			return [False, 400]
		except Exception as e: print(str(e)); return [False, 500] 

	@staticmethod
	def getTickets(): 
		connection = mysql.connector.connect(**SQLConnector.DB_CONFIGS[1]) 
		cursor = connection.cursor() 
		with open('../backend/ticketfetch.sql') as script: 
			cursor.execute(script) 
			data = cursor.fetchall() 
			cursor.close; connection.close(); script.close() 
		

class VerificationTracker: 
	length = 20; number = 0; kmax = 2 
	keyArray = [{'key':"",'initialTime': 0} for _ in range(kmax)] 
	choices = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','!','#','%','&','@','$','=','>','<','^','*'] 
	timeout = 60*5 # 5 min in seconds 

	@staticmethod 
	def newKey(userid: int):
		if VerificationTracker.number >= VerificationTracker.kmax-1: return False 
		start = ''.join(random.choice(VerificationTracker.choices, k=VerificationTracker.length)) 
		VerificationTracker.keyArray[VerificationTracker.number] = { 
			'key': start, 
			'initialTime': int(time.time()), 
			'uid': userid 
		}; VerificationTracker.number += 1 
		return VerificationTracker.number 
	
	@staticmethod 
	def checkKeyValidity(key: str): 
		for x in range(len(VerificationTracker.keyArray)): 
			if key == VerificationTracker.keyArray[x]['key']: 
				if abs(VerificationTracker.keyArray[x]['initialTime']%int(time.time))<VerificationTracker.timeout: 
					return True 
		return False 

class Intermediary():
	def postRequestHandler(endpoint: str, data: bytes): 
		target = endpoint.removeprefix('/api/0/POST/') 
		if target == 'login': 
			postd = json.loads(data.decode('utf-8')) 
			username = postd.get('username') 
			pw_hash = postd.get('password_hash') 
			user = SQLConnector.validateLogin(username, pw_hash) 
			if not user[0]: return user 
			return [user[0], user[1], [{'key':VerificationTracker.keyArray[VerificationTracker.newKey(user[2])]['key'],'userid':user[2]}]] if user[0] else [False, 400] 
		else: 
			postd = json.loads(data.decode('utf-8')) 
			if VerificationTracker.checkKeyValidity(postd.get('key')): 
				match target:
					case 'ticket': '' 

	def getRequestHandler(endpoint: str, data: bytes): 
		target = endpoint.removeprefix('/api/0/GET/') 
		getd = json.loads(data.decode('utf-8')) 
		if VerificationTracker.checkKeyValidity(getd.get('key')): 
			match target: 
				case 'data': #! Interface with sql db based on bytes(data) 
					ticketdata = SQLConnector.getTickets() # dict 
					return [True, 200, ticketdata] 

class RequestHandler(BaseHTTPRequestHandler): 
	def do_GET(self): # API Endpoints 
		if self.path.startswith('/api/0/GET/'): 
			try: content_length = int(self.headers['Content-Length']) 
			except Exception: self.send_response(411); self.end_headers(); return 
			get_data = self.rfile.read(content_length) 
			response = Intermediary.getRequestHandler(endpoint = self.path, data = get_data) 
			self.send_response(response[1]); self.send_header('Content-Type', 'application/json'); self.end_headers(); 
			if len(response) >=3: self.wfile.write(response[2].encode('utf-8')) 
			return 
		elif self.path.startswith('/api'): 
			self.send_response(418) 
			self.end_headers() 
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee") 

		else: 
			# Serve index.html for root 
			if self.path == ('/' or ''): 
				self.send_response(200) 
				self.send_header('Content-type', 'text/html') 
				self.end_headers() 
				with open('../website/index.html', 'r') as file: 
					html_content = file.read().encode('utf-8') 
					self.wfile.write(html_content) 
			elif self.path == '/favicon.png': 
				# favicon handler 
				self.send_response(200) 
				self.send_header('Content-Type', 'image/x-icon') 
				self.end_headers() 
				with open('../website/assets/graphics/favicon.png', 'rb') as favicon_file: 
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
					self.end_headers() 
					with open(file_path, 'rb') as f: 
						self.wfile.write(f.read()) 
				else: 
					self.send_response(404) 
					self.send_header('Content-type', 'text/plain') 
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
					self.end_headers() 
					with open(file_path, 'rb') as f: 
						self.wfile.write(f.read()) 
				else: 
					self.send_response(404) 
					self.send_header('Content-type', 'text/plain') 
					self.end_headers() 
					self.wfile.write(b"404 Not Found") 

	def do_POST(self): # API Endpoints 
		if self.path.startswith('/api/0/POST/'): 
			try: content_length = int(self.headers['Content-Length']) 
			except Exception: self.send_response(411); self.end_headers(); return 
			post_data = self.rfile.read(content_length) 
			# self.send_header('Content-type', 'text/html') 
			response = Intermediary.postRequestHandler(endpoint = self.path, data = post_data) 
			self.send_response(response[1]); self.send_header('Content-Type', 'application/json'); self.end_headers() 
			if len(response)<3: self.wfile.write(response[2].encode('utf-8')) 
			return 
		else: 
			self.send_response(418) 
			self.end_headers() 
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee"); return 

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
