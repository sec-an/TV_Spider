# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from utils import ali
from bs4 import BeautifulSoup
import re
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "zhaoziyuan"
Tag_name = "找资源"
siteUrl = "https://zhaoziyuan.me"


def searchContent(key, token):
    try:
        if not token:
            return []
        url = siteUrl + "/so?filename=" + quote_plus(key)
        searchResult = BeautifulSoup(requests.get(url).text, "html.parser")
        lists = searchResult.select("div.li_con div.news_text")
        regexVid = re.compile("(\\S+)")
        videos = []
        for vod in lists:
            sourceName = ""
            if vod.select_one("div.news_text a h3"):
                sourceName = vod.select_one("div.news_text a h3").get_text()
            if key in sourceName:
                list1 = vod.select_one("div.news_text a")["href"]
                matcher = regexVid.search(list1)
                if matcher:
                    videos.append({
                        "vod_id": f'{Tag}${matcher.group(1)}',
                        "vod_name": sourceName,
                        "vod_pic": "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
                        "vod_remarks": Tag_name + " " + vod.select_one("div.news_text a p").get_text()
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
        matcher = aliyun.search(requests.get("https://zhaoziyuan.me/" + share_url).text)
        if not matcher:
            return []
        return ali.getdetailContent(Tag, matcher.group(1), token)
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
    # res = searchContent("冰雨火")
    res = detailContent('zhaoziyuan$https://www.aliyundrive.com/s/i3E3Zvq5f3H', "")
    # res = playerContent('zhaoziyuan___3xfBjW6JbHR__eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21Kc29uIjoie1wiZG9tYWluX2lkXCI6XCJiajI5XCIsXCJzaGFyZV9pZFwiOlwiM3hmQmpXNkpiSFJcIixcImNyZWF0b3JcIjpcImVlNDhjYjcwNmNhYTQ4MjZhNTFiM2ExZTVhMTA1YjhlXCIsXCJ1c2VyX2lkXCI6XCJhbm9ueW1vdXNcIn0iLCJjdXN0b21UeXBlIjoic2hhcmVfbGluayIsImV4cCI6MTY2MTg3NjE0NSwiaWF0IjoxNjYxODY4ODg1fQ.V4Wl_4s6A9V8k0UX3Y_wao4CzMSH8_mE_No1WduKfDSx37q1qqeARTItMkN_rpibVtsm9N3gzdvYCAsX9JoWW0mWg801iwPFkUME-BAtp5wdoHZ10KAJK5pfxsc1xorJp_2_1MopolHP9ZIwMSr9mGef2VQ2QgNZNsCKqrSueh4__630c949c9e0789ac7121425a9156efe6f1aa5348__video', "AliYun原画", "")

    print(res)
