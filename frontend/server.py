from http.server import BaseHTTPRequestHandler, HTTPServer 
import ssl 
import subprocess; import os 
import mimetypes
from sys import argv as callargs

WEB_ROOT = '../website'  # Directory where your HTML/CSS/JS lives

class RequestHandler(BaseHTTPRequestHandler): 
	def do_GET(self): 
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

	# def do_POST(self): 
	# 	if self.path == 'api/post/': 
	# 		content_length = int(self.headers['Content-Length']) 
	# 		post_data = self.rfile.read(content_length) 
	# 		self.send_response(200) 
	# 		self.send_header('Content-type', 'text/html') 
	# 		self.end_headers() 
	# 		self.wfile.write(b"POST received: " + post_data) 
	# 	else: 
	# 		self.send_response(404) 
	# 		self.end_headers() 
	# 		self.wfile.write(b"Not Found") 

def run(): 
	try: 
		if ((callargs[1] == ('y' or 'tls' or 'yes') if callargs.count(str)>1 else False) or input("Run with TLS? (y/n) > ").lower()=="y") == True:
			port = 4443 
			handler = RequestHandler 
			server = HTTPServer(('', port), handler) 

			certchain = '../certs/server_chain.pem' 
			keyfile = '../certs/serverkey.pem' 

			context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
			context.load_cert_chain(certfile = certchain, keyfile = keyfile) 

			server.socket = context.wrap_socket(server.socket, server_side=True) 
			print(f"Server running with SSL/TLS") 
			print(f'Local: 127.0.0.1:{port}') 
			server.serve_forever() 

		else: 
			port = 8000 
			handler = RequestHandler 
			server = HTTPServer(('', port), handler) 

			print("Server running") 
			print(f'Local: 127.0.0.1:{port}') 
			server.serve_forever() 

	# except ssl.SSLError as e: 
	# 	print(f"SSL Error: {e}") 
	except Exception as e: 
		print(f"Error: {e}") 

if __name__ == "__main__": 
	# # Create a self-signed certificate if you don't have one (for testing only) // only gonna work with openssl and even then prob only linux 
	# if not path.exists('server.pem'): 
	# 	print("Generating self-signed certificate...") 
	# 	subprocess.run("openssl req -x509 -newkey rsa:4096 -keyout server.pem -out server.pem -nodes -days 365", shell=True) 
	
	run() 
