import socket
import os

# This imports the Client from your custom database!
# (Make sure your Redis server file is actually named main.py)
from main import Client  

class RequestHandler:
    def __init__(self, request_text):
        self.request_text = request_text

    def process_request(self):
        headers = self.request_text.split('\n')
        if len(headers) == 0 or len(headers[0].split()) < 2:
            return ""

        filename = headers[0].split()[1]
        
        # 1. HTML Routing
        if filename == '/':
            filename = '/index.html'

        # 2. THE API BRIDGE TO BYTECACHE
        elif filename == '/api/status':
            try:
                # Connects to your Redis Vault on port 31337
                db = Client(port=31337) 
                
                # Write to RAM, then read from RAM
                db.set('server_status', 'ByteCache Vault is Online!')
                data = db.get('server_status')
                
                # Clean up the bytes for the browser
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                
                return 'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n' + str(data)
                
            except Exception as e:
                # If your Redis server isn't running, this prevents a crash
                return f'HTTP/1.0 500 INTERNAL SERVER ERROR\r\n\r\nDatabase Offline: {e}'
          
            # 3. THE WRITE PIPELINE: Catching incoming data
        elif filename == '/api/save' and headers[0].startswith('POST'):
            try:
                # Chop the raw request string in half at the double line-break
                # The '1' means only split it once, just in case the body has line breaks
                parts = self.request_text.split('\r\n\r\n', 1)
                
                if len(parts) > 1 and parts[1]:
                    payload = parts[1]
                else:
                    return 'HTTP/1.0 400 BAD REQUEST\r\n\r\nError: No data sent'

                # Open the bridge and save the payload to the database
                db = Client(port=31337) 
                db.set('latest_transmission', payload)
                
                return 'HTTP/1.0 200 OK\r\n\r\nData successfully secured in ByteCache Vault!'
                
            except Exception as e:
                return f'HTTP/1.0 500 INTERNAL SERVER ERROR\r\n\r\nDatabase Offline: {e}'

        # 3. Standard File Serving
        try:
            filepath = os.path.join('frontend', filename.lstrip('/'))
            with open(filepath, 'r') as fin:
                content = fin.read()
            return 'HTTP/1.0 200 OK\r\n\r\n' + content
            
        except FileNotFoundError:
            return 'HTTP/1.0 404 NOT FOUND\r\n\r\n404 File Not Found'


class HTTPServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def run(self):
        self.server_socket.listen(1)
        print(f"Bouncer listening on port {self.port} ...")

        while True:
            client_connection, client_address = self.server_socket.accept()
            request = client_connection.recv(1024).decode()

            if not request:
                client_connection.close()
                continue

            # Hand the raw text to our OOP handler
            handler = RequestHandler(request)
            response = handler.process_request()

            if response:
                client_connection.sendall(response.encode('utf-8'))
            
            client_connection.close()


if __name__ == '__main__':
    server = HTTPServer()
    server.run()