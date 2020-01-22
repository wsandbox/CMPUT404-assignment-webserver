from urllib import request
import pdb


BASEURL = "http://127.0.0.1:8080"

url = BASEURL + "/base.css"
req = request.urlopen(url, None, 3)
print(req.getcode())
