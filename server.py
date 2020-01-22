#  coding: utf-8 
import socketserver, os, pdb, mimetypes
# importing Handlers to manage URL searches

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

ok_header = bytes("""HTTP/1.1 200 OK\r\n""",'utf-8')
bad_method_header = bytes("""HTTP/1.1 405 Method Not Allowed\r\n""", 'utf-8')
not_found_header = bytes("""HTTP/1.1 404 Not Found\r\n""", 'utf-8')
redirect_header = bytes("""HTTP/1.1 301 Moved Permanently\r\n""", "utf-8")

class MyWebServer(socketserver.BaseRequestHandler):

    def return200(self):
        self.request.sendall(ok_header)
        return
    
    def return301(self):
        self.request.sendall(bytes("301: Permanently Redirected\r\n", "utf-8"))
        self.request.sendall(redirect_header)
        return

    def return_404(self):
        self.request.sendall(bytes("""404: File Not Found\r\n""", 'utf-8'))
        self.request.sendall(not_found_header)
        return

    def return405(self):
        self.request.sendall(bytes("405: Bad Method\r\n", "utf-8"))
        self.request.sendall(bad_method_header)
        return

    def setup(self):
        self.data = self.request.recv(1024).strip()
        self.data_split = self.data.split()
        self.host = self.data_split[4].decode('utf-8')
        self.request_type = self.data_split[0].decode("utf-8")
        self.target = self.data_split[1].decode("utf-8")

        print("Host:", self.host)
        print("Request type:", self.request_type)
        print("Path:", self.target)


    def handle(self):
        #verify filepath is either www/ or deep/
        if self.target == "/":
            reply = "Cannot access root files"
            print(reply)
            self.request.sendall(bytes(reply+"\r\n", "utf-8"))
            self.request404()
            return
        elif (self.target[:4] != "/www" and self.target[:5] != "/deep"):
            print(self.target)
            self.return404()

        if len(self.target)>2:
            try:
                self.filepath = self.target[1:]
            except IndexError:
                print("Cannot access files from root")
                self.request.sendall(bytes("""404: File Not Found\r\n""", 'utf-8'))
                self.request.sendall(not_found_header)

        if self.request_type == "GET":
            try:
                filetype = self.filepath.split('.')[1]
                self.request.sendall(ok_header)
                self.request.sendall(bytes("Host: " +self.host +"\r\n", "utf-8"))
                self.request.sendall(bytes("Accept: */*\r\n", "utf-8"))
                # self.request.sendall(bytes("Accept-Encoding: gzip, deflate, br\r\n", "utf-8"))
                # set_content = bytearray("Content-Type: "+content+"\r\n", 'utf-8')
                set_content = bytearray("Content-Type: text/html\r\n", 'utf-8')
                        
                self.request.sendall(set_content)
                # self.request.sendall(bytes("Connection: keep-alive\r\n", "utf-8"))

                site = open(self.filepath, 'r')
                reply = site.read()
                self.request.sendall(bytes(reply+'\r\n', 'utf-8'))
            except FileNotFoundError as e:
                print(e)
                self.request.sendall(bytes("""404: File Not Found\r\n""", 'utf-8'))
                self.request.sendall(not_found_header)
            
            except IsADirectoryError as e:
                print(e)
                if self.filepath[-1] != "/":
                    new_location = "127.0.0.1:8080/"+self.filepath + "/\r\n"
                    reply = "Location: "+new_location
                    self.request.sendall(redirect_header)
                    self.request.sendall(bytearray(reply, 'utf-8'))
                    return
                else:
                    self.request.sendall(bytes("404: Page Not Found\r\n", "utf-8"))
                    self.request.sendall(not_found_header)


            except Exception as e:
                print(e)
                self.return404()
        
        elif self.request_type in ["PUT", "POST", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE", "CONNECT"]:
            self.request.sendall(bytes("405: Bad Method\r\n", "utf-8"))
            self.request.sendall(bad_method_header)

if __name__ == "__main__":
    #changed localhost to 127.0.0.1 to allow curl to successfully retrieve site
    HOST, PORT = "127.0.0.1", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
