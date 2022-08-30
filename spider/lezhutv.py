# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import base64
import hashlib

urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

Tag = "lezhutv"
Tag_name = "乐猪TV"
siteUrl = "http://www.lezhutv.com"
playerConfig = {"线路1": {"status": 1, "or": 900, "show": "线路1", "des": "aa.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路2": {"status": 1, "or": 890, "show": "线路2", "des": "ab.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路3": {"status": 1, "or": 880, "show": "线路3", "des": "ac.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路4": {"status": 1, "or": 870, "show": "线路4", "des": "ad.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路5": {"status": 1, "or": 760, "show": "线路5", "des": "ae.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路6": {"status": 1, "or": 750, "show": "线路6", "des": "af.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"},
                "线路7": {"status": 1, "or": 740, "show": "线路7", "des": "ag.com", "ps": "1",
                          "parse": "http://www.lezhutv.com/hls2/index.php?url=", "tip": "无需安装任何插件"}}


def getHeaders(url):
    headers = {}
    headers.setdefault("method", "GET")
    headers.setdefault("DNT", "1")
    headers.setdefault("Upgrade-Insecure-Requests", "1")
    headers.setdefault("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")
    return headers


def get_md5(value):
    b64 = base64.b64encode((base64.b64encode(value.encode()).decode() + "NTY2").encode()).decode()
    md5 = hashlib.md5(b64.encode()).hexdigest()
    return "".join(char if char.isdigit() else "zyxwvutsrqponmlkjihgfedcba"["abcdefghijklmnopqrstuvwxyz".find(char)] for char in md5)


def searchContent(key, token):
    try:
        url = siteUrl + "/search-pg-1-wd-" + quote_plus(key) + ".html"
        searchResult = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser")
        videos = []
        lists = searchResult.select("ul.tbox_m li")
        for vod in lists:
            name = vod.a["title"]
            if key in name:
                videos.append({
                    "vod_id": f'{Tag}${vod.a["href"].split("/")[-1].split(".")[0]}',
                    "vod_name": name,
                    "vod_pic": vod.a["data-original"],
                    "vod_remarks": Tag_name + " " + vod.a.span.get_text()
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/detail/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser")
        yac = doc.select_one("p.yac").get_text().split('/')
        vodList = {
            "vod_id": ids,
            "vod_name": doc.select_one("div.data h4").contents[0].get_text(),
            "vod_pic": doc.select_one("div.dbox div.img")["data-original"],
            "type_name": "",
            "vod_year": yac[0].strip() if len(yac) >= 0 else "",
            "vod_area": yac[1].strip() if len(yac) >= 1 else "",
            "vod_remarks": yac[2].strip() if len(yac) >= 2 else "",
            "vod_actor": doc.select_one("p.act").contents[1].get_text() if len(doc.select_one("p.act").contents) > 1 else "",
            "vod_director": doc.select_one("p.dir").contents[1].get_text() if len(doc.select_one("p.dir").contents) > 1 else "",
            "vod_content": doc.select_one("div.tbox_js").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        sources = doc.select("ul.list_block")
        for index, source in enumerate(sources):
            sourceName = f"线路{index + 1}"
            playList = ""
            playListA = source.select("a")
            vodItems = []
            for vod in playListA:
                vodItems.append(vod.get_text() + "$" + f"{Tag}___" + vod["href"].split("/")[-1].split(".")[0])
            if len(vodItems):
                playList = "#".join(vodItems)
            if len(playList) == 0:
                continue
            vod_play.setdefault(sourceName, playList)
        if len(vod_play):
            vod_play_from = "$$$".join(vod_play.keys())
            vod_play_url = "$$$".join(vod_play.values())
            vodList.setdefault("vod_play_from", vod_play_from)
            vodList.setdefault("vod_play_url", vod_play_url)
        return [vodList]
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        id = ids.split("___")[-1]
        url = f"{siteUrl}/play/{id}.html"
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders("")).text, "html.parser").select_one("div.mplayer").script.get_text()
        view_path = allScript[(allScript.find("var view_path = '") + 17):(allScript.rfind("var view_from") - 4)]
        hls_url = f"{siteUrl}/hls2/index.php?url={view_path}"
        value = BeautifulSoup(requests.get(url=hls_url, headers=getHeaders("")).text, "html.parser").input["value"]
        md5 = get_md5(value)
        data = {
            "id": view_path,
            "type": "vid",
            "siteuser": "",
            "md5": md5,
            "referer": url,
            "hd": "",
            "lg": ""
        }
        res = requests.post(url="http://www.lezhutv.com/hls2/url.php", data=data, headers=getHeaders("")).json()
        return {
            "header": "",
            "parse": 0,
            "playUrl": "",
            "url": res["media"]["url"]
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("苍兰诀", "")
    # res = detailContent('lezhutv$221915', "")
    res = playerContent("lezhutv___221964-2-1", "", "")
    print(res)
