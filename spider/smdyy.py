# -*- coding:utf-8 -*-
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

Tag = "smdyy"
Tag_name = "神马影院"
siteUrl = "https://www.smdyy.cc"
playerConfig = {
    "duoduozy": {"show": "高清线路", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "sohu": {"show": "优选7", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "qq": {"show": "优选3", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "bilibili": {"show": "bilibili", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "youku": {"show": "优选1", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "qiyi": {"show": "优选2", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "letv": {"show": "优选6", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "xigua": {"show": "西瓜视频", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "mgtv": {"show": "优选4", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "tkm3u8": {"show": "备用", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="},
    "pptv": {"show": "优选5", "or": 999, "ps": "0", "parse": "https://player.6080kan.cc/player/play.php?url="}
}


def Regex(pattern, content):
    try:
        matcher = re.findall(pattern, content)
        if matcher:
            return matcher[0]
    except Exception as e:
        print(e)
    return ""


def getHeaders(url):
    headers = {}
    headers.setdefault("method", "GET")
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("Accept-Encoding", "gzip: deflate: br")
    headers.setdefault("Upgrade-Insecure-Requests", "1")
    headers.setdefault(
                       "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    headers.setdefault(
                       "Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.9")
    return headers


def searchContent(key, token):
    try:
        currentTime = str(int(round(time.time() * 1000)))
        limit = 10
        url = siteUrl + "/index.php/ajax/suggest?mid=1&wd=" + quote_plus(
            key) + f"&limit={limit}&timestamp=" + currentTime
        searchResult = requests.get(url=url, headers=getHeaders(url)).json()
        videos = []
        if searchResult.get("total") > 0:
            lists = searchResult.get("list")
            for vod in lists:
                cover = vod.get("pic")
                if cover and not cover.startswith("http"):
                    cover = siteUrl + cover
                videos.append({
                    "vod_id": f'{Tag}${vod.get("id")}',
                    "vod_name": vod.get("name"),
                    "vod_pic": cover,
                    "vod_remarks": Tag_name
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/kan/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser")
        # 取基本数据
        cover = doc.select_one("a.pic img")["data-original"]
        if cover and not cover.startswith("http"):
            cover = siteUrl + cover
        data = doc.select("p.data")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": doc.select_one("div.stui-content__detail h1.title").get_text(),
            "vod_pic": cover,
            "type_name": Regex("类型：(\\S+)", data[0].get_text()),
            "vod_year": Regex("年份：(\\S+)", data[0].get_text()),
            "vod_area": Regex("地区：(\\S+)", data[0].get_text()),
            "vod_remarks": "",
            "vod_actor": Regex("主演：(\\S+)", data[1].get_text()),
            "vod_director": Regex("导演：(\\S+)", data[2].get_text()),
            "vod_content": doc.select_one("span.detail-content").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        regexPlay = re.compile("/play/(\\d+)-(\\d+)-(\\d+).html")
        sources = doc.select("div.stui-vodlist__head")
        # sourceList = doc.select("div.stui-vodlist__head > ul.stui-content__playlist")
        for source in sources:
            sourceName = source.select_one("h3").get_text().strip()
            found = False
            for item in playerConfig:
                if playerConfig[item]["show"] == sourceName:
                    found = True
                    break
            if not found:
                continue
            playList = ""
            playListA = source.select("ul.stui-content__playlist > li > a")
            vodItems = []
            for vod in playListA:
                matcher = regexPlay.match(vod["href"])
                if not matcher:
                    continue
                playURL = matcher.group(1) + "-" + matcher.group(2) + "-" + matcher.group(3)
                vodItems.append(vod.get_text() + "$" + f"{Tag}___" + playURL)
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
        headers = {}
        headers.setdefault("Referer", " https://www.smdyy.cc/")
        headers.setdefault("User-Agent", " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
        headers.setdefault("Accept", " text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
        headers.setdefault("Accept-Language", " zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6")
        headers.setdefault("Accept-Encoding", " gzip, deflate")
        url = f"{siteUrl}/play/{id}.html"
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser").select("script")
        for item in allScript:
            scContent = item.get_text().strip()
            if scContent.startswith("var player_"):
                player = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
                if player.get("from") in playerConfig:
                    pCfg = playerConfig.get(player.get("from"))
                    # jxurl = "https://player.tjomet.com/lgyy/?url=" + player.get("url")
                    jxurl = pCfg.get("parse") + player.get("url")
                    session = requests.session()
                    doc = BeautifulSoup(session.get(url=jxurl, headers=getHeaders(jxurl)).text, "html.parser")
                    script = doc.select("body>script")
                    for j in script:
                        Content = j.get_text().strip()
                        urlt = Regex("\"url\": *\"([^\"]*)\",", Content)
                        if not urlt:
                            return {}
                        token = Regex("\"token\": *\"([^\"]*)\"", Content)
                        if not token:
                            return {}
                        vkey = Regex("\"vkey\": *\"([^\"]*)\",", Content)
                        if not vkey:
                            return {}
                        hashmap = {
                            "sign": "smdyycc",
                            "url": urlt,
                            "vkey": vkey,
                            "token": token
                        }
                        res = session.post(url="https://player.6080kan.cc/player/xinapi.php", data=hashmap, headers={"user-agent":"okhttp/3.12.11"}).json()["url"][8:].encode("utf-8")
                        playurl = str(base64.b64decode(res), "utf-8")[8:-8]
                        return {
                            "header": json.dumps(headers),
                            "parse": 0,
                            "playUrl": "",
                            "url": playurl
                        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("壮志凌云")
    # res = detailContent(68614)
    # func = "playerContent"
    # res = playerContent("smdyy___69684-1-3")
    # res = eval(func)("68614-1-1")
    print(res)
