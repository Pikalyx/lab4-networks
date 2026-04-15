import sys
from socket import *

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip] : It is the IP Address Of Proxy Server')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8080))
tcpSerSock.listen(1)

while True:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(4096)
    print(message)
    # Extract the filename from the given message
    filename = message.split()[1].partition(b"/")[2]  # Extract filename
    print(filename)
    fileExist = False
    filetouse = b"/" + filename
    print(filetouse)
    try:
        # Check whether the file exists in the cache
        with open(filetouse[1:], "rb") as f:
            outputdata = f.readlines()
            fileExist = True
            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send(b"HTTP/1.1 200 OK\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n")
            for line in outputdata:
                tcpCliSock.send(line)
                print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if not fileExist:
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace(b"www.", b"", 1)
            print(hostn.decode())
            try:
                # Connect to the socket to port 80
                c.connect((hostn.decode(), 80))
                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                request = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(hostn.decode())
                c.sendall(request.encode())
                # Read the response into buffer
                # Fill in start
                buffer = b""
                while True:
                    data = c.recv(4096)
                    if not data:
                        break
                    buffer += data
                # Fill in end
                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                with open(b"./" + filename, "wb") as tmpFile:
                    # Fill in start
                    tmpFile.write(buffer)
                    tcpCliSock.sendall(buffer)
                    c.close()
                    # Fill in end
            except Exception as e:
                print("Illegal request:", e)

        else:
            # HTTP response message for file not found
            # Fill in start
            tcpCliSock.send(b"HTTP/1.1 404 Not Found\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n\r\n")
            tcpCliSock.send(b"<html><body><h1>404 Not Found</h1></body></html>")
            # Fill inend
    # Close the client and the server sockets
    tcpCliSock.close()
tcpSerSock.close()
