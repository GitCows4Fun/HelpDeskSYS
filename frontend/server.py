from http.server import BaseHTTPRequestHandler, HTTPServer 
import ssl; import mimetypes 
import os; import subprocess 
from sys import argv as args 

WEB_ROOT = '../website'  # Directory where your HTML/CSS/JS lives

class Interfacer():
	def postRequestHandler(endpoint = str(), data = bytes()): 
		target = endpoint.removeprefix('/api/0/POST/') 
		match target: 
			case _: '' 

	def getRequestHandler(endpoint = str(), data = bytes()): 
		target = endpoint.removeprefix('/api/0/GET/') 
		match target: 
			case 'data': '' #! Interface with sql db based on bytes(data) 

class RequestHandler(BaseHTTPRequestHandler): 
	def do_GET(self): 
		if self.path.startswith('/api/0/GET/'):
			content_length = int(self.headers['Content-Length']) 
			get_data = self.rfile.read(content_length) 
			self.send_response(200) if Interfacer.getRequestHandler(endpoint = self.path, data = get_data) else self.send_response(500); self.end_headers() 
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
		if self.path.startswith('/api/0/POST'): 
			content_length = int(self.headers['Content-Length']) 
			post_data = self.rfile.read(content_length) 
			# self.send_response(200) 
			# self.send_header('Content-type', 'text/html') 
			# self.end_headers() 
			# self.wfile.write(b"POST received: " + post_data) 
			self.send_response(200) if Interfacer.postRequestHandler(endpoint = self.path, data = post_data) else self.send_response(500); self.end_headers() 
		else: 
			self.send_response(418) 
			self.end_headers() 
			self.wfile.write(b"I'm a teapot\nYou asked a teapot to brew coffee") 

def run(): 
	try: 
		SSLOn = True if (args[1].lower() if len(args) > 1 else input("Use TLS? (y/n) > ").strip().lower()) in ("y", "yes", "tls") else False 
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
