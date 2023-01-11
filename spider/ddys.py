# -*- coding:utf-8 -*-
from urllib.parse import quote_plus, quote
import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import time
from Crypto.Cipher import AES
import urllib3
import zlib


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "ddys"
Tag_name = "低端影视"
siteUrl = "https://ddys.tv"


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
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    return headers


def aes_cbc_encrypt(text, key, iv):
    try:
        pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        text = pad(text)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encryptedbytes = cipher.encrypt(text.encode('utf8'))
        encodestrs = base64.b64encode(encryptedbytes)
        enctext = encodestrs.decode('utf8')
        return enctext
    except Exception as e:
        print(e)


def searchContent(key, token):
    try:
        url = siteUrl + "/?s=" + quote_plus(key) + "&post_type=post"
        searchResult = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser")
        videos = []
        lists = searchResult.select("article")
        for vod in lists:
            title = vod.h2.get_text()
            if "(" in title:
                tmp = title.split("(")
                name = tmp[0]
                remark = tmp[1].replace(")", "")
            else:
                name = title
                remark = vod.select_one("time.updated").get_text()
            id = vod.h2.a["href"].split("/")[-1] if vod.h2.a["href"].split("/")[-1] else vod.h2.a["href"].split("/")[-2]
            try:
                vod_pic = vod.img["src"]
            except Exception as e:
                vod_pic = ""
            if key in name:
                videos.append({
                    "vod_id": f'{Tag}${id}',
                    "vod_name": name,
                    "vod_pic": vod_pic,
                    "vod_remarks": Tag_name + " " + remark
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/{id}/"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser")
        # 取基本数据
        title = doc.select_one("h1.post-title").get_text()
        if "(" in title:
            tmp = title.split("(")
            name = tmp[0]
            remark = tmp[1].replace(")", "")
        else:
            name = title
            remark = doc.select_one("time").get_text().strip()
        vod_pic = ""
        type_name = ""
        vod_year = ""
        vod_area = ""
        vod_actor = ""
        vod_director = ""
        vod_content = ""
        if doc.select_one("div.abstract"):
            data = doc.select_one("div.abstract").get_text().replace(" ", "")
            vod_pic = doc.select_one("div.post img")["src"]
            type_name = Regex("类型:(.*)制", data)
            vod_year = Regex("年份:(.*)简", data)
            vod_area = Regex("地区:(.*)年份", data)
            vod_actor = Regex("演员:(.*)类", data)
            vod_director = Regex("导演:(.*)演", data)
            vod_content = Regex("简介:(.*)", data)
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": name,
            "vod_pic": vod_pic,
            "type_name": type_name,
            "vod_year": vod_year,
            "vod_area": vod_area,
            "vod_remarks": remark,
            "vod_actor": vod_actor,
            "vod_director": vod_director,
            "vod_content": vod_content
        }

        # 取播放列表数据
        vodItems = []
        vod_play = {}

        pages = doc.select(".post-page-numbers")
        if pages:
            for index, page in enumerate(pages):
                url = f"{siteUrl}/{id}/{index + 1}/"
                page_doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(url)).text, "html.parser")
                allScript = page_doc.select_one(".wp-playlist-script")
                playList = ""
                scContent = allScript.get_text().strip()
                data = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
                Tracks = data.get("tracks")
                for source in Tracks:
                    zm = "https://ddys.tv/subddr" + source["subsrc"]
                    vodItems.append(source["caption"] + "$" + f"{Tag}___" + source["src0"] + "|" + zm + "|" + source.get("src1", ""))
                if len(vodItems):
                    playList = "#".join(vodItems)
                if len(playList) == 0:
                    continue
                vod_play.setdefault(str(index + 1), playList)
                vodItems.clear()
        else:
            allScript = doc.select_one(".wp-playlist-script")
            playList = ""
            scContent = allScript.get_text().strip()
            data = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
            Tracks = data.get("tracks")
            for source in Tracks:
                zm = "https://ddys.tv/subddr" + source["subsrc"]
                vodItems.append(source["caption"] + "$" + f"{Tag}___" + source["src0"] + "|" + zm + "|" + source.get("src1", ""))
            if len(vodItems):
                playList = "#".join(vodItems)
            if len(playList) == 0:
                return []
            vod_play.setdefault("1", playList)
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
        item = id.split("|")
        if item[-1] == "":
            data = {
                "path": item[0],
                "expire": int(round(time.time() * 1000)) + 600000
            }
            real_id = quote_plus(aes_cbc_encrypt(json.dumps(data, separators=(',', ':')), "gh3Zalc874hD7fcV", "1529076118276120"))
        else:
            real_id = item[-1]
        url = f"https://ddys.tv/getvddr/video?id={real_id}&dim=1080P+&type=mix"
        playUrl = requests.get(
            url=url,
            headers=getHeaders(url)
        ).json()
        ZiMu = item[1]
        result = {
            "header": "",
            "parse": 0,
            "playUrl": "",
            "subf": "/vtt/utf-8",
            "subt": quote(ZiMu)
        }
        if "url" in playUrl:
            real_url = playUrl["url"]
        else:
            m3u8_raw = []
            for character in playUrl["pin"]:
                m3u8_raw.append(ord(character))
            m3u8_raw_data = zlib.decompress(bytes(m3u8_raw), 32 + zlib.MAX_WBITS).decode()
            result["m3u8"] = m3u8_raw_data
            real_url = ""
        result["url"] = real_url
        return result
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("成", "")
    # res = detailContent('ddys$top-gun-maverick', "")
    # res = detailContent('ddys$me-time', "")
    res = playerContent("ddys___/v/movie/Fall.2022.mp4|https://ddys.tv/subddr/v/movie/Fall.2022.ddr|u7q0YdmkLeNnmxmw%2FxfDI5Oz4NLa5556Cl9H88N9eAHC%2F5XgUISnFaHbrOEwUcoj", "1", "")
    # res = eval(func)("68614-1-1")
    print(res)
