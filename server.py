#  coding: utf-8 
import socketserver, pdb, os
# importing Handlers to manage URL searches

# Copyright 2013 Warren Thomas 
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
# 

ok_header = bytearray("""HTTP/1.1 200 OK\r\n""",'utf-8')
bad_method_header = bytearray("""HTTP/1.1 405 Method Not Allowed\r\n\r\n""", 'utf-8')
not_found_header = bytes("""HTTP/1.1 404 Not Found\r\n""", 'utf-8')
redirect_header = bytearray("""HTTP/1.1 301 Moved Permanently\r\n""", "utf-8")
    

class MyWebServer(socketserver.BaseRequestHandler):
    def setup(self):
        try:
            self.data = self.request.recv(1024).strip()
            self.data_split = self.data.split()
            self.host = "127.0.0.1:8080"
            self.request_type = self.data_split[0].decode("utf-8")
            self.path = self.data_split[1].decode("utf-8")
        except IndexError as e:
            print("IndexError:",e)
            return

        print("Log: Host:", self.host)
        print("Log: Request type:", self.request_type)
        print("Log: Path:", self.path)


    def handle(self):
        if self.request_type == "GET":
            try:
                cwd = os.getcwd() + "/www"
                temp = self.path
                cwd = cwd.split('/')
                for t in temp[1:].split('/'):
                    if t == "..":
                        cwd = cwd[:-1]
                    else:
                        cwd.append(t)
                if "www" not in cwd:
                    print("Log: Files accessed above root directory")
                    self.return404()
                else:
                    site = open("www"+self.path, 'r')
                    reply = site.read()
                    self.filesize = len(reply)
                    self.filetype = self.path.split('.')[1]
                    # pdb.set_trace()
                    self.return200()
                    self.request.sendall(bytearray("Content-Type: text/"+self.filetype+"; charset: UTF-8\r\n", "utf-8"))
                    print("Log: Content-Type: text/"+self.filetype)
                    self.request.sendall(bytearray("\r\n"+reply+"\r\n", "utf-8"))
                    return

            except FileNotFoundError:
                print("Log: FNF /www"+ self.path)
                self.return404()
                return
                
            except IsADirectoryError:
                if self.path[-1] != "/":
                    self.path += "/"
                    self.return301()
                    print("Log: Redirecting: http://"+self.host+self.path)
                    self.request.sendall(bytearray("Location: http://"+self.host+self.path+"\r\n\r\n", "utf-8"))
                    return
                else:
                    print("Log: IADE: Retrieving /www"+self.path+"index.html")
                    self.return200()
                    site = open("www"+self.path+"index.html", 'r')
                    reply = site.read()
                    self.request.sendall(bytearray("Content-Type: text/html; charset: UTF-8\r\n", "utf-8"))
                    self.request.sendall(bytearray("\r\n"+reply+"\r\n", "utf-8"))
                    return
            
        
        elif self.request_type in ["PUT", "POST", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE", "CONNECT"]:
            print("Log: 405:", self.request_type, "not supported")
            self.return405()
            return
        
        else: 
            print("Log: Something else was wrong with the request\n", self.data)
            self.return404()
            return

    def return200(self):
        self.request.sendall(ok_header)
        print("Log: "+(ok_header).decode())
        return

    def return301(self):
        self.request.sendall(redirect_header)
        print("Log: "+(redirect_header).decode())
        return

    def return404(self):
        self.request.sendall(not_found_header)
        print("Log: "+(not_found_header).decode())
        self.request.sendall(bytearray("404 Not Found\r\n", 'utf-8'))
        return
        

    def return405(self):
        self.request.sendall(bad_method_header)
        print("Log: "+(bad_method_header).decode())
        self.request.sendall(bytearray("405: Bad Method\r\n", "utf-8"))
        return



if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
