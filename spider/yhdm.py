# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import urllib3
from Crypto.Cipher import AES


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "yhdm"
Tag_name = "樱花动漫"
siteUrl = "https://www.857dm.com"


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


def aes_cbc_decrypt(text, key, iv):
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        content = base64.b64decode(text)
        text = cipher.decrypt(content).decode('utf-8')
        # dec_text是bytes类型的数据，可根据实际需要base64等操作，这里是转str
        return text.rstrip("\x01").\
            rstrip("\x02").rstrip("\x03").rstrip("\x04").rstrip("\x05").\
            rstrip("\x06").rstrip("\x07").rstrip("\x08").rstrip("\x09").\
            rstrip("\x0a").rstrip("\x0b").rstrip("\x0c").rstrip("\x0d").\
            rstrip("\x0e").rstrip("\x0f").rstrip("\x10")
    except Exception as e:
        print(e)


def searchContent(key, token):
    try:
        url = siteUrl + "/search/-------------.html?wd=" + quote_plus(key) + "&submit="
        searchResult = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser")
        videos = []
        lists = searchResult.select("li.clearfix")
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
        url = f"{siteUrl}/video/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders("")).text, "html.parser")
        # 取基本数据
        data = doc.select("p.data")
        vodList = {
            "vod_id": ids,
            "vod_name": doc.select_one("div.myui-content__detail h1").get_text(),
            "vod_pic": doc.select_one("div.myui-content__thumb img")["data-original"],
            "type_name": Regex("类型：(\\S+)", data[0].get_text()),
            "vod_year": Regex("年份：(\\S+)", data[0].get_text()),
            "vod_area": Regex("地区：(\\S+)", data[0].get_text()),
            "vod_remarks": Regex("更新：(\\S+)", data[-1].get_text()),
            "vod_actor": Regex("主演：(\\S+)", data[1].get_text()),
            "vod_director": Regex("导演：(\\S+)", data[1].get_text()),
            "vod_content": doc.select_one("div.col-pd.text-collapse.content").select_one("span.data").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        regexPlay = re.compile("/play/(\d+)-(\d+)-(\d+).html")
        sourceList = doc.select("ul.myui-content__list")
        sources = doc.select("ul.nav.nav-tabs.active li")[:len(sourceList)]
        for index, source in enumerate(sources):
            sourceName = source.get_text().strip()
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

        url = f"{siteUrl}/play/{id}.html"
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser").select("script")
        for item in allScript:
            scContent = item.get_text().strip()
            if scContent.startswith("var player_"):
                player = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
                jx_data = requests.get(f"https://danmu.yhdmjx.com/m3u8.php?url={player.get('url')}", headers=getHeaders(url)).text
                iv = Regex(r'bt_token = "(\w*)"', jx_data)
                text = Regex(r'getVideoInfo\("([^"]*)"', jx_data)
                real_url = aes_cbc_decrypt(text, "57A891D97E332A9D", iv)
                return {
                    "parse": "0",
                    "playUrl": "",
                    "url": real_url
                }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("名侦探", "")
    # res = detailContent("yhdm$2949", "")
    res = playerContent("yhdm___7105-1-1", "", "")
    # res = eval(func)("68614-1-1")
    print(res)
