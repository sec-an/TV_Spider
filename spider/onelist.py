# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "onelist"
Tag_name = "Onelist"
siteUrl = "https://onelist.top"


def getHeaders(url):
    headers = {}
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    headers.setdefault("Origin", siteUrl)
    return headers


def searchContent(key, token):
    try:
        url = f"{siteUrl}/v1/api/video/search?q={quote_plus(key)}&page=1&size=24"
        lists = requests.post(url=url, headers=getHeaders("")).json()["data"]
        videos = []
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod["ID"]}',
                "vod_name": vod["title"],
                "vod_pic": vod["image"],
                "vod_remarks": Tag_name + " " + vod["UpdatedAt"]
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/v1/api/video/id?id={id}"
        data = requests.post(url=url, headers=getHeaders("")).json()["data"]
        play_url = data["url_content"].replace("\n", "#").replace("$", f"${Tag}___")
        return [{
            "vod_id": f'{Tag}${id}',
            "vod_name": data["title"],
            "vod_pic": data["image"],
            "type_name": data["video_tags"],
            "vod_year": data["year"],
            "vod_area": "",
            "vod_remarks": data["UpdatedAt"],
            "vod_actor": data["authors"],
            "vod_director": data["director"],
            "vod_content": data["content"].strip(),
            "vod_play_from": "onelist",
            "vod_play_url": play_url
        }]
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        id = ids.split("___")[-1]
        return {
            "header": "",
            "parse": "",
            "playUrl": "",
            "url": id
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("暗黑", "")
    # res = detailContent('onelist$767', "")

    print(res)
