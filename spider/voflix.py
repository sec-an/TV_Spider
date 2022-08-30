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


Tag = "voflix"
Tag_name = "VOFLIX HD"
siteUrl = "https://www.voflix.com"
playerConfig = {
    "duoduozy": {"sh": "VOFLIX", "pu": "https://play.shtpin.com/xplay/?url=", "sn": 0, "or": 999}
}


def Regex(pattern, content):
    try:
        matcher = re.findall(pattern, content)
        if matcher:
            return matcher[0]
    except Exception as e:
        print(e)
    return ""


def getHeaders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    return headers


def searchContent(key, token):
    try:
        url = siteUrl + "/search/-------------.html?wd=" + quote_plus(key)
        searchResult = BeautifulSoup(requests.get(url=url, headers=getHeaders()).text, "html.parser")
        videos = []
        lists = searchResult.select(".module-card-item.module-item")
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod.a["href"].split("/")[-1].split(".")[0]}',
                "vod_name": vod.strong.get_text().strip(),
                "vod_pic": vod.img["data-original"],
                "vod_remarks": Tag_name + " " + vod.select_one(".module-item-note").get_text()
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/detail/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders()).text, "html.parser")
        # 取基本数据
        sourcediv = doc.select("div.module-item-cover>div")
        data = doc.select("div.module-info-tag-link")
        aa = doc.select("div.module-info-item-content")[2].select("a")
        actors = []
        for i in aa:
            actors.append(i.get_text())
        actor = ",".join(actors)
        bb = doc.select("div.module-info-item-content")[0].select("a")
        directors = []
        for i in bb:
            directors.append(i.get_text())
        director = ",".join(directors)
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": sourcediv[0].select_one("div.module-item-pic>img")["alt"],
            "vod_pic": sourcediv[0].select_one("div.module-item-pic>img")["data-original"],
            "type_name": data[2].a.get_text(),
            "vod_year": data[0].a.get_text(),
            "vod_area": data[1].a.get_text(),
            "vod_remarks": doc.select("div.module-info-item-content")[-1].get_text(),
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": doc.select_one("div.module-info-introduction-content>p").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        regexPlay = re.compile("/play/(\\d+)-(\\d+)-(\\d+).html")
        sources = doc.select("div.module-tab-items-box>div>span")
        sourceList = doc.select("div.module-list>div.module-play-list")
        for index, source in enumerate(sources):
            sourceName = source.get_text()
            found = False
            for item in playerConfig:
                if playerConfig[item]["sh"] == sourceName:
                    found = True
                    break
            if not found:
                continue
            playList = ""
            playListA = sourceList[index].select("div.module-play-list-content>a")
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
        headers.setdefault("origin", " https://www.voflix.com")
        headers.setdefault("User-Agent", " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
        headers.setdefault("Accept", " */*")
        headers.setdefault("Accept-Language", " zh-CN,zh;q=0.9,en-US;q=0.3,en;q=0.7")
        headers.setdefault("Accept-Encoding", " gzip, deflate")

        url = f"{siteUrl}/play/{id}.html"
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders()).text, "html.parser").select("script")
        for item in allScript:
            scContent = item.get_text().strip()
            if scContent.startswith("var player_"):
                player = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
                if player.get("from") in playerConfig:
                    pCfg = playerConfig.get(player.get("from"))
                    videoUrl = pCfg.get("pu") + player.get("url")
                    allScripts = BeautifulSoup(requests.get(
                        url=videoUrl,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
                            "Referer": "https://www.libvio.me/"
                        }).text, "html.parser").select("body script")
                    for j in allScripts:
                        scContents = j.get_text().strip()
                        urlt = Regex("\"url\": *\"([^\"]*)\",", scContents)
                        if not urlt:
                            return {}
                        token = Regex("\"token\": *\"([^\"]*)\"", scContents)
                        if not token:
                            return {}
                        vkey = Regex("\"vkey\": *\"([^\"]*)\",", scContents)
                        if not vkey:
                            return {}
                        hashmap = {
                            "tm": str(int(round(time.time() * 1000))),
                            "url": urlt,
                            "vkey": vkey,
                            "token": token,
                            "sign": "F4penExTGogdt6U8",
                        }
                        res = requests.post(
                            url="https://play.shtpin.com/xplay/555tZ4pvzHE3BpiO838.php",
                            params=hashmap,
                            headers={
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
                            }).json()["url"][8:].encode("utf-8")
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
    # res = searchContent("成")
    res = detailContent("voflix$197", "")
    # func = "playerContent"
    # res = playerContent("11201-1-1")
    # res = eval(func)("68614-1-1")
    print(res)
