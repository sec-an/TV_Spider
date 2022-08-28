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
    res = searchContent("冰雨火")
    res = detailContent('zhaoziyuan$YoboboO1vFY81')

    print(res)
