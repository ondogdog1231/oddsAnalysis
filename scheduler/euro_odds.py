# coding=utf-8
import sys
import os


projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')


import requests
import datetime
import re
import json
import time
from config import connector
import utils.handicap as h


