import requests
import json

BOT_API_KEY = "5786692222:AAHHmHXf4fGx1d6x855IdPNjFt_uJVYgXOU"

# methods = "getUpdates"
methods = "sendMessage"
url = f"https://api.telegram.org/bot{BOT_API_KEY}/{methods}"



# response_text = f"Time: {}, {} vs {}, prediction: {}, home: {}, away: {}"


data = {
    'chat_id': '@soccer_predictor_1999',
    # 'chat_id': '-1001542096288',
    # 'text': 'Match Time: 2022-10-25 00:45 <strong>歐冠盃</strong> 國際米蘭 vs 柏辛域陀尼亞 \n\n\nhome',
    'text': '<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>',
    'parse_mode': "HTML"
}




headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)
jsonParsed = json.loads(r.content)
print(json.dumps(jsonParsed, indent=4, ensure_ascii=False))