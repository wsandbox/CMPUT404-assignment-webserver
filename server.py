#  coding: utf-8 
import socketserver, os, pdb
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

    
class MyWebServer(socketserver.BaseRequestHandler):
    def setup(self):
        pass

    def handle(self):
        ok_header = bytes("""HTTP/1.1 200 OK\r\n""",'utf-8')
        bad_method_header = bytes("""HTTP/1.1 405 Method Not Allowed\r\n""", 'utf-8')
        not_found_header = bytes("""HTTP/1.1 404 Not Found\r\n""", 'utf-8')
        redirect_header = bytes("""HTTP/1.1 301 Moved Permanently\r\n""", "utf-8")

        data = self.request.recv(4096)#.strip()
        attr = data.split()
        # pdb.set_trace()
        host = attr[4].decode('utf-8')
        # self.request.sendall(bytearray("Host: http://127.0.0.1:8080\r\n", 'utf-8'))
        # self.request.sendall(bytes("Transfer-encoding: chunked\r\n", "utf-8"))
        # self.request.sendall(bytes("Accept-encoding: *\r\n", "utf-8"))

        # pdb.set_trace()
        self.request_type = attr[0].decode("utf-8")
        self.filepath = attr[1].decode("utf-8")
        if self.filepath[0] == "/":
            self.filepath = self.filepath[1:]
        if self.request_type == "GET":
            try:
                site = open(self.filepath, 'r')
                reply = site.read()
                filetype = self.filepath.split('.')[1]
                self.request.sendall(ok_header)
                content = "text/"+filetype+"; charset=utf-8"
                # set_content = bytearray("Content-Type: "+content+"\r\n", 'UTF-8')
                set_content = bytearray("Content-Type: mimetype\r\n", 'UTF-8')

                self.request.sendall(set_content)
                self.request.sendall(bytearray(reply+'\r\n', 'utf-8'))
            except FileNotFoundError as e:
                self.request.sendall(bytes("""404: File Not Found\r\n""", 'utf-8'))
                self.request.sendall(not_found_header)
            
            except IsADirectoryError as e:
                if self.filepath[-1] != "/":
                    new_location = "127.0.0.1:8080/"+self.filepath + "/\r\n"
                    reply = "Location: "+new_location
                    self.request.sendall(redirect_header)
                    self.request.sendall(bytearray(reply, 'utf-8'))
                    return
                else:
                    self.request.sendall(not_found_header)


            except Exception as e:
                self.handle_error(e)
        
        elif self.request_type in ["PUT", "POST", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE", "CONNECT"]:
            self.request.sendall(bad_method_header)
        
    def handle_error(self, e):
        print(e,'\n')
        self.request.sendall(bytearray("Other Error Occured", "utf-8"))

if __name__ == "__main__":
    #changed localhost to 127.0.0.1 to allow curl to successfully retrieve site
    HOST, PORT = "127.0.0.1", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
