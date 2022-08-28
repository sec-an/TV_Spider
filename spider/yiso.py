# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from utils import ali
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "yiso"
Tag_name = "易搜"
siteUrl = "https://yiso.fun"


def getHeaders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; V2049A Build/SP1A.210812.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36",
        "Referer": "https://yiso.fun/"
    }
    return headers


def searchContent(key, token):
    try:
        if not token:
            return []
        url = siteUrl + "/api/search?name=" + quote_plus(key) + "&from=ali"
        lists = requests.get(url=url, headers=getHeaders(), verify=False).json()["data"]["list"]
        videos = []
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod["url"]}',
                "vod_name": vod["fileInfos"][0]["fileName"],
                "vod_pic": "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
                "vod_remarks": Tag_name + " " + vod['gmtCreate']
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(url, token):
    try:
        if not token:
            return []
        share_url = url.strip().split("$")[-1]
        return ali.getdetailContent(Tag, share_url, token)
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        if not token:
            return {}
        id = ids.split("___")[-1]
        return ali.getplayerContent(id, flag, token)
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("老友记")
    print(res)
