# -*- coding:utf-8 -*-
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import base64
from Crypto.Cipher import AES
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "bttwoo"
Tag_name = "两个BT"
siteUrl = "https://www.bttwoo.com"


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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    }
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


def get_item(item, tag):
    data = []
    for i in item.select(tag):
        data.append(i.get_text())
    return ",".join(data)


def searchContent(key, token):
    try:
        url = siteUrl + "/xssearch?q=" + quote_plus(key)
        jS = BeautifulSoup(requests.get(url=url, headers=getHeaders()).text, "html.parser")
        videos = []
        lists = jS.select("div.mi_ne_kd > ul > li")
        for vod in lists:
            name = vod.h3.a.get_text().strip()
            if key in name:
                videos.append({
                    "vod_id": f'{Tag}${vod.a["href"].split("/")[-1].split(".")[0]}',
                    "vod_name": name,
                    "vod_pic": vod.img["data-original"],
                    "vod_remarks": Tag_name + " " + vod.span.get_text()
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/movie/{id}.html"
        detail = requests.get(url=url, headers=getHeaders())
        detail.encoding = "utf-8"
        doc = BeautifulSoup(detail.text, "html.parser")
        # 取基本数据
        sourcediv = doc.select_one("div.mi_ne_kd.dypre")
        data = sourcediv.select("li")
        type_name = ""
        vod_area = ""
        vod_year = ""
        vod_remarks = ""
        vod_actor = ""
        vod_director = ""
        for item in data:
            if "类型" in item.get_text()[:3]:
                type_name = get_item(item, "a")
            elif "地区" in item.get_text()[:3]:
                vod_area = get_item(item, "a")
            elif "年份" in item.get_text()[:3]:
                vod_year = get_item(item, "a")
            elif "上映" in item.get_text()[:3]:
                vod_remarks = get_item(item, "span")
            elif "主演" in item.get_text()[:3]:
                vod_actor = get_item(item, "a")
            elif "导演" in item.get_text()[:3]:
                vod_director = get_item(item, "a")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": sourcediv.h1.get_text(),
            "vod_pic": sourcediv.img["src"],
            "type_name": type_name,
            "vod_year": vod_year,
            "vod_area": vod_area,
            "vod_remarks": vod_remarks,
            "vod_actor": vod_actor,
            "vod_director": vod_director,
            "vod_content": doc.select_one("div.yp_context").get_text().strip(),
            "vod_play_from": "两个BT"
        }

        # 取播放列表数据
        sources = doc.select("div.paly_list_btn > a")
        vodItems = []
        for source in sources:
            sourceName = source.get_text()
            playURL = Regex("/v_play/(.*)\\.html", source["href"])
            if not playURL:
                continue
            vodItems.append(sourceName + "$" + f"{Tag}___" + playURL)
        if len(vodItems):
            playList = "#".join(vodItems)
        vodList.setdefault("vod_play_url", playList)
        return [vodList]
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        id = ids.split("___")[-1]
        url = f"{siteUrl}/v_play/{id}.html"
        K2 = requests.get(url=url, headers=getHeaders()).text
        UR = BeautifulSoup(K2, "html.parser")
        Y = re.compile("\"([^\"]+)\";var [\\d\\w]+=function dncry.*md5.enc.Utf8.parse\\(\"([\\d\\w]+)\".*md5.enc.Utf8.parse\\(([\\d]+)\\)")
        pY = re.compile("video: \\{url: \"([^\"]+)\"")
        m = re.compile("subtitle: \\{url:\"([^\"]+\\.vtt)\"")
        matcher = Y.search(K2)
        if matcher:
            group = matcher.group(1)
            KEY = matcher.group(2)
            IV = matcher.group(3)
            str5 = aes_cbc_decrypt(group, KEY, IV)
            matcher2 = pY.search(str5)
            str3 = matcher2.group(1) if matcher2 else ""
            matcher3 = m.search(str5)
            str4 = matcher3.group(1) if matcher3 else ""
        else:
            str4 = ""
            str3 = str4
        G8 = UR.select_one("div.videoplay").iframe
        if not str3 and G8:
            pY2 = G8["src"]
            X = re.compile("var time = ['\"]([^'\"]+)['\"]")
            a = re.compile("var url = ['\"]([^'\"]+)['\"]")
            K = re.compile("var vkey = ['\"]([^'\"]+)['\"]")
            Oe = re.compile("var fvkey = ['\"]([^'\"]+)['\"]")
            fi = re.compile("var ua = ['\"]([^'\"]+)['\"]")
            M = re.compile("var cip = ['\"]([^'\"]+)['\"]")
            Q = re.compile("src: '([^']+\\.\\w*)',")
            if "jx.xmflv.com" in pY2:
                K3 = requests.get(url=pY2, headers=getHeaders()).text
                matcher4 = X.search(K3)
                if not matcher4:
                    return {}
                group2 = matcher4.group(1)
                matcher5 = a.search(K3)
                if not matcher5:
                    return {}
                group3 = matcher5.group(1)
                K4 = requests.get(
                    url="https://jx.xmflv.com/player.php?time=" + group2 + "&url=" + group3,
                    headers=getHeaders()).text
                matcher6 = K.search(K4)
                if not matcher6:
                    return {}
                group4 = matcher6.group(1)
                matcher7 = Oe.search(K4)
                if not matcher7:
                    return {}
                group5 = matcher7.group(1)
                matcher8 = fi.search(K4)
                if not matcher8:
                    return {}
                group6 = matcher8.group(1)
                matcher9 = M.search(K4)
                if not matcher9:
                    return {}
                group7 = matcher9.group(1)
                matcher10 = X.matcher(K4)
                if not matcher10:
                    return {}
                group8 = matcher10.group(1)
                return {}
            else:
                text = requests.get(url=pY2, headers=getHeaders()).text
                matcher11 = Q.search(text)
                if matcher11:
                    str3 = matcher11.group(1)
        return {
            "header": "",
            "parse": "0",
            "playUrl": "",
            "url": str3
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("冰雨火", "")
    res = detailContent('bttwoo$52995', "")
    # func = "playerContent"
    # res = playerContent("bttwoo___bXZfODA5NzQtbm1fMg==", "", "")
    # res = eval(func)("68614-1-1")
    print(res)
