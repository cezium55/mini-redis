import socket

server_host = '127.0.0.1'
server_port = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_host, server_port))
server_socket.listen(1)
print('listening on port %s ...' % server_port)

while True:
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Get the client request by decoding it 
    request = client_connection.recv(1024).decode()
    
    # SAFETY PRECAUTION: If the browser sends an empty request, skip it.
    if not request:
        client_connection.close()
        continue

    print(request)

    # Parse http headers safely
    headers = request.split('\n')
    filename = headers[0].split()[1]

    # Get the content of the file to the main page
    if filename == '/':
        filename = '/index.html'

    # Get the content from the location of frontend/index.html
    try:
        fin = open('frontend' + filename)
        content = fin.read()
        fin.close()

        # Send http response
        response = 'HTTP/1.0 200 OK\r\n\r\n' + content
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\r\n\r\n404 File Not Found'
    
    # FIX: These are now outside the except block!
    # They will run whether the file is found or not.
    client_connection.sendall(response.encode())
    client_connection.close()