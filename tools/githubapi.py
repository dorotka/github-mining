#!/usr/bin/env python3

from base64 import b64encode
from urllib.request import Request, urlopen

token = '08a571561afba49f3fd31636c6a419d10f61fe6c'
auth = 'Basic ' + b64encode('{}:x-oauth-basic'.format(token).encode()).decode('ascii')

def giturlopen(url):
  # NOTE: The urllib mechanism for authentication relies on the server replying
  # with 401 to the first try. Instead, github replies 404, to not leak info.
  req = Request(url)
  req.add_header('Authorization', auth)
  return urlopen(req)
