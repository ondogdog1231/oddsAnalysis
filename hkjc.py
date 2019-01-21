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



url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=20181222&enddate=20190121&teamid=default"


r = requests.get(url)

print r.content.decode("gbk").encode("utf-8")