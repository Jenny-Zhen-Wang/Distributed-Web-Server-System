import time
from socket import *
import os
import sys
from datetime import datetime
from socket import *
import threading
#from threading import Thread


# define HOST and PORT
HOST = '127.0.0.1'

'''
This sets the listening port, default port 8887
'''
if sys.argv[3:]:
    if sys.argv[3].casefold() == '-port'.casefold():
        PORT = int(sys.argv[4])
    else:
        PORT = 8887
else:
    PORT = 8887


if sys.argv[1:3]:
    if sys.argv[1].casefold() == '-document_root'.casefold():
        os.chdir(sys.argv[2])
        DOCUMENT_ROOT = sys.argv[2]
    else:
        DOCUMENT_ROOT = os.getcwd() + '/files'
else:
    DOCUMENT_ROOT = os.getcwd()+'/files'

# construct 200 response to normal request
def normal_response(f_path, f_type):
    date = datetime.now()

    # code200 = '''HTTP/1.1 200 OK\r
    # Date: {}\r
    # Content-Type: {}\r
    # Content-Length: {}\r
    # \r
    # '''
    code200 = 'HTTP/1.1 200 OK\r\nDate: {d}\r\nConnection: keep-alive\r\nContent-Length: {l}\r\nContent-Type: {t}\r\n\r\n'
    with open(f_path, 'rb') as file:
        file_content = file.read()
        file_size = len(file_content)
        response = code200.format(d=date, l=file_size, t=f_type).encode() + file_content
    return response


# construct 404 response to not found request
def notfound_response(f_path, f_type):
    date = datetime.now()
    code404 = 'HTTP/1.1 404 Not Found\r\nDate: {d}\r\nConnection: keep-alive\r\nContent-Length: None\r\nContent-Type: {t}\r\n\r\n\nERROR ' \
              '404: Page Not Found\nThe requested URL was not found in this server\n '
    response = code404.format(d=date, t=None).encode()
    return response


# construct 400 response to bad request
def bad_response():
    date = datetime.now()
    code400 = 'HTTP/1.1 400 Bad Request\r\nDate: {d}\r\nConnection: keep-alive\r\nContent-Length: None\r\nContent-Type: None\r\n\r\n\n' \
              'ERROR 400: Request Error\nYour client has issued a malformed or illegal request.\n'
    response = code400.format(d=date).encode()
    return response


# construct 403 response to forbidden request
def forbidden_response():
    date = datetime.now()
    code403 = 'HTTP/1.1 403 Forbidden\r\nDate: {d}\r\nConnection: keep-alive\r\nContent-Length: None\r\nContent-Type: None\r\n\r\n\n' \
              'ERROR 403: Forbidden Access\nAccess to this resource on this server is denied.\n'
    response = code403.format(d=date).encode()
    return response


def server_process(connection_socket,numthread):
    while True:
        request_message = connection_socket.recv(1024).decode()
        
        breakflag = False
        if numthread < 100:
            connection_socket.settimeout(300)   # If a connection is idle for 60 seconds, server ends this connections
        elif numthread < 200:
            connection_socket.settimeout(60)   # If a connection is idle for 60 seconds, server ends this connections
        else:
            breakflag = True
            
        
        

        # parse the request message, find http method and relative file name
        request_message_temp = request_message.split(' ')
        http_method, relative_filename = request_message_temp[0], request_message_temp[1]

        # set default file: if no file is specified, use /index.html
        if relative_filename == '/':
            relative_filename = '/index.html'

        # figure out standard content type of requested file
        content_type = relative_filename.split('.')[-1]
        mime_type = {
            'html': 'text/html',
            'jpg': 'image/jpg',
            'gif': 'image/gif',
            'txt': 'text/plain'
        }
        # if the content type is beyond what the server can handle, let standard content type equal None
        if content_type in mime_type:
            content_type_standard = mime_type[content_type]
        else:
            content_type_standard = None

        # translate relative file name to absolute file name
        absolute_filename = DOCUMENT_ROOT + relative_filename



        # determine if it is a bad request
        if content_type_standard is None:
            response_message = bad_response()
            connection_socket.sendall(response_message)
            break

        else:
            try:
                response_message = normal_response(absolute_filename, content_type_standard)
                connection_socket.sendall(response_message)
                if breakflag:
                    break
            except FileNotFoundError:
                response_message = notfound_response(absolute_filename, content_type_standard)
                connection_socket.sendall(response_message)
                break
            except PermissionError:
                response_message = forbidden_response()
                connection_socket.sendall(response_message)
                break
            
    connection_socket.close()
    print("Connection closed")


def main():

    # build server socket and listen for connection
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    print("socket binded to port", PORT)
    server_socket.listen(6)
    print("socket is listening")

    numthread = 0
    while True:
        # establish connection and receive request message from client
        connection_socket, address = server_socket.accept()
        print("Connected to:", address[0], ":", address[1])
        # Using multithread to process client request
        thread = threading.Thread(target=server_process, args=(connection_socket,numthread))
        thread.start()
        numthread = threading.activeCount() - 1 
        print(f"Runing thread number: {numthread}")

    # close socket
    server_socket.close()
    print("socket closed")


if __name__ == '__main__':
    main()
