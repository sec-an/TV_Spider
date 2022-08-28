# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import base64
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "libvio"
Tag_name = "LIBVIO影视"
siteUrl = "https://www.libvio.me"
playerConfig = {
    "duoduozy": {"sh": "LINE100", "pu": "https://play.shtpin.com/xplay/?url=", "sn": 1,
                "or": 999},
    "LINE405": {"sh": "LINE405", "pu": "https://sh-data-s01.chinaeast2.cloudapp.chinacloudapi.cn/lb.php?url=", "sn": 1,
                "or": 999},
    "LINE406": {"sh": "LINE406", "pu": "https://sh-data-s01.chinaeast2.cloudapp.chinacloudapi.cn/zm.php?url=", "sn": 1,
                "or": 999},
    "LINE407": {"sh": "LINE407", "pu": "https://sh-data-s01.chinaeast2.cloudapp.chinacloudapi.cn/lb.php?url=", "sn": 1,
                "or": 999}, "LINE408": {"sh": "LINE408", "pu": "", "sn": 0, "or": 999},
    "p300": {"sh": "LINE300", "pu": "", "sn": 0, "or": 999},
    "p301": {"sh": "LINE301", "pu": "", "sn": 0, "or": 999},
    "line402-日语": {"sh": "LINE402", "pu": "", "sn": 0, "or": 999},
    "LINE400": {"sh": "LINE400", "pu": "https://sh-data-s01.chinaeast2.cloudapp.chinacloudapi.cn/lb.php?url=", "sn": 1,
                "or": 999},
    "line401": {"sh": "LINE401", "pu": "", "sn": 0, "or": 999}
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
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("DNT", "1")
    headers.setdefault("Upgrade-Insecure-Requests", "1")
    headers.setdefault("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
    headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")
    return headers


def searchContent(key, token):
    try:
        url = siteUrl + "/search/-------------.html?wd=" + quote_plus(key) + "&submit="
        searchResult = BeautifulSoup(requests.get(
            url=url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            }
        ).text, "html.parser")
        videos = []
        lists = searchResult.select(".col-md-6.col-sm-4.col-xs-3")
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod.a["href"].split("/")[-1].split(".")[0]}',
                "vod_name": vod.h4.a.get_text().strip(),
                "vod_pic": vod.a["data-original"],
                "vod_remarks": Tag_name + " " + vod.select_one(".pic-text.text-right").get_text()
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/detail/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders("")).text, "html.parser")
        # 取基本数据
        data = doc.select("p.data")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": doc.select_one("div.stui-content__detail h1").get_text(),
            "vod_pic": doc.select_one("div.stui-content__thumb a img")["data-original"],
            "type_name": Regex("类型：(\\S+)", data[0].get_text()),
            "vod_year": Regex("年份：(\\S+)", data[0].get_text()),
            "vod_area": Regex("地区：(\\S+)", data[0].get_text()),
            "vod_remarks": Regex("更新：(\\S+)", data[4].get_text()),
            "vod_actor": Regex("主演：(\\S+)", data[1].get_text()),
            "vod_director": Regex("导演：(\\S+)", data[1].get_text()),
            "vod_content": doc.select_one("span.detail-content").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        regexPlay = re.compile("/play/(\d+)-(\d+)-(\d+).html")
        sources = doc.select("div.stui-vodlist__head h3")
        sourceList = doc.select("ul.stui-content__playlist")
        for index, source in enumerate(sources):
            sourceName = source.get_text().strip()
            found = False
            for item in playerConfig:
                if playerConfig[item]["sh"] == sourceName:
                    found = True
                    break
            if not found:
                continue
            playList = ""
            playListA = sourceList[index].select("li a")
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
        headers.setdefault("origin", " https://www.libvio.me/")
        headers.setdefault("User-Agent",
                           " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
        headers.setdefault("Accept", " */*")
        headers.setdefault("Accept-Language", " zh-CN,zh;q=0.9,en-US;q=0.3,en;q=0.7")
        headers.setdefault("Accept-Encoding", " gzip, deflate")
        headers.setdefault("referer", " https://www.libvio.me/")

        url = f"{siteUrl}/play/{id}.html"
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser").select("script")
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
                        matcher = Regex("(?<=urls\\s=\\s').*?(?=')", scContents)
                        if matcher:
                            return {
                                # "header": json.dumps(headers),
                                "parse": 0,
                                "playUrl": "",
                                "url": matcher
                            }
                        else:
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
                                # "header": json.dumps(headers),
                                "parse": 0,
                                "playUrl": "",
                                "url": playurl
                            }
                else:
                    return {
                        "parse": 1,
                        "playUrl": "",
                        "url": url
                    }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("医院五日", "")
    # res = detailContent(100456)
    # func = "playerContent"
    # res = playerContent("100456-2-11")
    # res = eval(func)("68614-1-1")
    print(res)
