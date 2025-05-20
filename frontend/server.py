from http.server import BaseHTTPRequestHandler, HTTPServer 
import ssl; import subprocess; from os import path 

class RequestHandler(BaseHTTPRequestHandler): 
	def do_GET(self): 
		if self.path == '/': 
			self.send_response(200) 
			self.send_header('Content-type', 'text/html') 
			self.end_headers() 
			self.wfile.write(b"Hello, GET!") 
	# 	elif self.path == '/post': 
	# 		self.send_response(200) 
	# 		self.send_header('Content-type', 'text/html') 
	# 		self.end_headers() 
	# 		self.wfile.write(b"Hello, this is the POST endpoint!") 
	
	# def do_POST(self): 
	# 	if self.path == '/post': 
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
		port = 8000 
		handler = RequestHandler 
		server = HTTPServer(('', port), handler) 
		server.socket = ssl.wrap_socket( 
			server.socket, 
			certfile='server.pem',  # Path to your certificate 
			server_side=True, 
			ssl_version=ssl.PROTOCOL_TLSv1_2, 
			keyfile='server.pem'  # If you have a separate key file, use it here 
		) 
		
		print(f"Server running on port {port} with SSL/TLS") 
		server.serve_forever() 
	except ssl.SSLError as e: 
		print(f"SSL Error: {e}") 
	except Exception as e: 
		print(f"Error: {e}") 

if __name__ == "__main__": 
	# Create a self-signed certificate if you don't have one (for testing only) 
	if not path.exists('server.pem'): 
		print("Generating self-signed certificate...") 
		subprocess.run("openssl req -x509 -newkey rsa:4096 -keyout server.pem -out server.pem -nodes -days 365", shell=True) 
	
	run() 
