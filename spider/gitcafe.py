# -*- coding:utf-8 -*-
from urllib.parse import urlencode
import requests
from utils import ali
import re
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

Tag = "gitcafe"
Tag_name = "小纸条"
siteUrl = "https://gitcafe.net"


def searchContent(key, token):
    try:
        if not token:
            return []
        url = siteUrl + "/tool/alipaper/"
        data = {
            "action": "search",
            "keyword": key
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; V2049A Build/SP1A.210812.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36",
            "Referer": "https://u.gitcafe.net/",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        lists = requests.post(url=url, data=urlencode(data), headers=headers).json()
        videos = []
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod["key"]}',
                "vod_name": vod["title"],
                "vod_pic": "https://www.lgstatic.com/i/image2/M01/15/7E/CgoB5lysLXCADg6ZAABapAHUnQM321.jpg",
                "vod_remarks": Tag_name + " " + vod['cat']
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(url, token):
    try:
        if not token:
            return []
        aliyun = re.compile("(https://www.aliyundrive.com/s/[^\"]+)")
        share_url = url.strip().split("$")[-1]
        if aliyun.search(share_url):
            return ali.getdetailContent(Tag, share_url, token)
        else:
            share_url = "https://www.aliyundrive.com/s/" + url.strip().split("$")[-1]
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
    res = searchContent("苍兰诀")
    print(res)
