from bs4 import BeautifulSoup
from apiclient.discovery import build

import requests
import json
from settings import settings
import datetime

# youtube apiを叩く準備
API_KEY = settings.API_KEY
YOUTUBE_API_SERVICE_NAME = settings.YOUTUBE_API_SERVICE_NAME
YOUTUBE_API_VERSION = settings.YOUTUBE_API_VERSION


# ホロジュールのHTMLが改良されたら要修正
def get_holodule_list(members):
    load_url = "https://schedule.hololive.tv/"
    html = requests.get(load_url)
    soup = BeautifulSoup(html.content, "html.parser")
    stream_list = []
    for x in soup.find_all('a'):
        try:
            if x['onclick'].startswith('gtag('):
                # 文字列からjson部分をjson形式に変換して抽出
                # 例: gtag('event','advClick',{'event_category':'AZKi','event_label':'https://virtual.spwn.jp/events/210829-TOFES','value':1});
                str_json = (','.join(x['onclick'].split(',')[2:]))[
                    :-2].replace("'", '"')
                json_data = json.loads(str_json)
                stream_list.append(json_data)
                # break
        except BaseException:
            pass

    # ホロジュールから取得した配信一覧
    return [x for x in stream_list if x['event_category'] in members]


def get_processed_video_ids(today, holodule_list):
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )
    processed_video_ids = []
    for hololive in holodule_list:
        if (hololive['event_label'].startswith(
                'https://www.youtube.com/watch?v=')):
            video_id = hololive['event_label'].split(
                'https://www.youtube.com/watch?v=')[1]
            print(video_id)
            video_response = youtube.videos().list(
                part='status, liveStreamingDetails',
                id=video_id,
            ).execute()
            video_item = video_response['items'][0]
            if (video_item.get('liveStreamingDetails')
                    and video_item['liveStreamingDetails'].get('actualEndTime')):
                # 日本時間で+9時間
                end_time = datetime.datetime.strptime(video_item['liveStreamingDetails'].get(
                    'actualEndTime'), '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=+9)
                end_date = datetime.date(
                    end_time.year, end_time.month, end_time.day)
                # プログラム実行時の日付と配信終了日が同一 and 配信終了のもの
                if (today ==
                        end_date and video_item['status']['uploadStatus'] == 'processed'):
                    print(video_item)
                    processed_video_ids.append(
                        {"video_id": video_id, "status": "do"})

    return processed_video_ids


def main():
    members = []
    with open('./members/members.json') as f:
        data = json.load(f)
        members = data['hololive']['members']
    holodule_list = get_holodule_list(members)
    today = datetime.date.today()
    processed_video_ids = get_processed_video_ids(today, holodule_list)

    with open(f'./video_list/${today}.json', 'w') as f:
        json.dump(processed_video_ids, f, indent=4)


if __name__ == '__main__':
    main()
