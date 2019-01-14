import sys
import os

import requests
import re
import time
import threading
from datetime import datetime
import hashlib
import json
# from library.bs4 import BeautifulSoup
from bs4 import BeautifulSoup

url = "http://liansai.500.com/zuqiu-4826/"

r = requests.get(url)

content = r.content.decode("gbk").encode("utf-8")

# print content
f = open("./result.txt", "w+")
f.write(content)
f.close()
