import requests


referer = "http://zq.titan007.com/cn/SubLeague/8.html"

headers = {
    'referer': referer,
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

url = "https://zq.titan007.com/cn/League/8.html"


result = requests.get(url, headers=headers)
print(result.text)
