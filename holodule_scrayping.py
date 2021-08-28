from bs4 import BeautifulSoup
import config as cf
import requests
import json

with open('./members.json') as f:
    data = json.load(f)
members = data['hololive']['members']
load_url = "https://schedule.hololive.tv/"
html = requests.get(load_url)
soup = BeautifulSoup(html.content, "html.parser")
stream_list = []

# ホロジュールのHTMLが改良されたら要修正
for x in soup.find_all('a'):
    try:
        if x['onclick'].startswith('gtag('):
            # 文字列からjson部分をjson形式に変換して抽出
            # 例: gtag('event','advClick',{'event_category':'AZKi','event_label':'https://virtual.spwn.jp/events/210829-TOFES','value':1});
            str_json = (','.join(x['onclick'].split(',')[2:]))[:-2].replace("'", '"')
            json_data = json.loads(str_json)
            stream_list.append(json_data)
            # break
    except BaseException:
        pass

# ホロジュールから取得した配信一覧
hololive_list = [x for x in stream_list if x['event_category'] in members]

for hololive in hololive_list:
    if (hololive['event_label'].startswith('https://www.youtube.com/watch?v=')):
        # api 投げる
        print(hololive)
