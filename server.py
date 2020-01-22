#  coding: utf-8 
import socketserver, pdb
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

ok_header = bytearray("""HTTP/1.1 200 OK\r\n""",'utf-8')
bad_method_header = bytearray("""HTTP/1.1 405 Method Not Allowed\r\n""", 'utf-8')
not_found_header = bytearray("""HTTP/1.1 404 Not Found\r\n""", 'utf-8')
redirect_header = bytearray("""HTTP/1.1 301 Moved Permanently\r\n""", "utf-8")
    

class MyWebServer(socketserver.BaseRequestHandler):

    def return200(self):
        self.request.sendall(ok_header)
        return
    
    def return301(self):
        self.request.sendall(bytearray("301: Permanently Redirected\r\n", "utf-8"))
        self.request.sendall(redirect_header)
        return        

    def return405(self):
        self.request.sendall(bytearray("405: Bad Method\r\n", "utf-8"))
        self.request.sendall(bad_method_header)
        return

    def setup(self):
        self.data = self.request.recv(1024).strip()
        self.data_split = self.data.split()
        self.host = self.data_split[4].decode('utf-8')
        self.request_type = self.data_split[0].decode("utf-8")
        self.target = self.data_split[1].decode("utf-8")[1:]
        print("Host:", self.host)
        print("Request type:", self.request_type)
        print("Path:", self.target)


    def handle(self):
        if self.request_type == "GET":
            #verify filepath is either www/ or deep/
            if self.target == "/":
                reply = "Cannot access root files"
                print(reply)
                self.request.sendall(bytearray(reply+"\r\n", "utf-8"))
                self.request.sendall(bytearray("404: File Not Found\r\n", 'utf-8'))
                self.request.sendall(not_found_header)
            elif (self.target[:3] != "www" and self.target[:4] != "deep"):
                print(self.target, "Not a valid target directory")
                self.request.sendall(bytearray("404: File Not Found\r\n", 'utf-8'))
                self.request.sendall(not_found_header)

            else:
                if self.target[-3:] == "www" or self.target[-4:] == "deep":
                    print("this")
                    self.target+="/"
                try:
                    site = open(self.target, 'r')
                    reply = site.read()
                    self.request.sendall(ok_header)
                    self.request.sendall(bytearray("Accept: text/html, text/css\r\n", "utf-8"))
                    self.request.sendall(bytearray("Content-Type: text/html; charset:UTF-8\r\n", "utf-8"))
                    self.request.sendall(bytearray(reply+"\r\n", "utf-8"))
                except FileNotFoundError:
                    print("FNF", self.target)
                    self.request.sendall(bytearray("404: File Not Found\r\n", 'utf-8'))
                    self.request.sendall(not_found_header)
            
            #redirect www to www/ to www/index.html, same for deep
                except IsADirectoryError:
                    print("IADE", self.target)
                    self.request.sendall(redirect_header)
                    reply = "Location: http://"+self.host+"/"+self.target +"index.html"
                    print(reply)
                    self.request.sendall(bytearray(reply+"\r\n", "utf-8"))
                    # self.target_file = self.target+"/index.html"
                    # print("New target:", self.target_file)
                    # try:
                    #     site = open(self.target, 'r')
                    #     reply = site.read()
                    #     self.request.sendall(ok_header)
                    #     self.request.sendall(bytearray("Accept: text/html, text/css\r\n", "utf-8"))
                    #     self.request.sendall(bytearray("Content-Type: text/html; charset:UTF-8\r\n", "utf-8"))
                    #     self.request.sendall(bytearray(reply+"\r\n", "utf-8"))
                    # except:
                    #     self.request.sendall(bytearray("404: File Not Found\r\n", 'utf-8'))
                    #     self.request.sendall(not_found_header)
        
        elif self.request_type in ["PUT", "POST", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE", "CONNECT"]:
            print("405:", self.request_type, "not supported")
            self.request.sendall(bytearray("405: Bad Method\r\n", "utf-8"))
            self.request.sendall(bad_method_header)
        
        else: 
            print("Something was wrong with the request\n", self.data)
            self.request.sendall(bytearray("404: File Not Found\r\n", 'utf-8'))
            self.request.sendall(not_found_header)


if __name__ == "__main__":
    #changed localhost to 127.0.0.1 to allow curl to successfully retrieve site
    HOST, PORT = "127.0.0.1", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
