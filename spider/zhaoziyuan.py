# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from utils import ali
from bs4 import BeautifulSoup
import re


Tag = "zhaoziyuan"
siteUrl = "https://zhaoziyuan.me"


def searchContent(key):
    try:
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
                        "vod_remarks": Tag + " " + vod.select_one("div.news_text a p").get_text()
                    })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(url):
    try:
        aliyun = re.compile("(https://www.aliyundrive.com/s/[^\"]+)")
        share_url = url.strip().split("$")[-1]
        if aliyun.search(share_url):
            return ali.getdetailContent(Tag, share_url)
        matcher = aliyun.search(requests.get("https://zhaoziyuan.me/" + share_url).text)
        if not matcher:
            return []
        return ali.getdetailContent(Tag, matcher.group(1))
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag):
    try:
        id = ids.split("___")[-1]
        return ali.getplayerContent(id, flag)
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("冰雨火")
    res = detailContent('zhaoziyuan$YoboboO1vFY81')

    print(res)
