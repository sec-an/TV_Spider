# -*- coding:utf-8 -*-
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import ddddocr
import urllib3
import re
import base64
import zlib


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "bdys_old"
Tag_name = "哔滴影视"
siteUrl = "https://www.52bdys.com"


def getHeaders(url):
    headers = {}
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    return headers


def add_domain(matched):
    url = "https://vod.bdys.me/" + matched.group(0)
    return url


def cacu(code):
    if "=" in code:
        code = code[:code.find("=")]
    elif code[-1] == "2" or code[-1] == "7":
        code = code[:-1]
        if code[-1] == "4" or code[-1] == "-":
            code = code[:-1]
    code = code.replace("I", "1")
    code = code.replace("l", "1")
    if code.isdigit():
        if len(code) > 4:
            code = code[:4]
        return int(code[:2]) - int(code[2:])
    elif "+" in code:
        code = code.split("+")
        return int(code[0]) + int(code[1])
    elif "-" in code:
        code = code.split("-")
        return int(code[0]) - int(code[1])
    elif "x" in code:
        code = code.split("x")
        return int(code[0]) * int(code[1])


def verifyCode(key):
    retry = 5
    while retry:
        try:
            session = requests.session()
            ocr = ddddocr.DdddOcr()
            img = session.get(
                url=f"{siteUrl}/search/verifyCode?t={str(int(round(time.time() * 1000)))}",
                headers=getHeaders(siteUrl)
            ).content
            # with open("verifyCode.jpg", 'wb') as f:
            #     f.write(img)
            code = cacu(ocr.classification(img))
            url = f"{siteUrl}/search/{quote_plus(key)}?code={code}"
            res = session.get(
                url=url,
                headers=getHeaders(url.split("?")[0])
            ).text
            if "/search/verifyCode?t=" not in res:
                return res
            # time.sleep(1)
        except Exception as e:
            print(e)
            if e.__class__.__name__ == 'ConnectTimeout':
                break
        finally:
            retry = retry - 1


def searchContent(key, token):
    try:
        res = verifyCode(key)
        searchResult = BeautifulSoup(res, "html.parser")
        videos = []
        lists = searchResult.select("div.card")
        for vod in lists:
            vod_name = vod.select_one("div.content").a["title"]
            if key in vod_name:
                videos.append({
                    "vod_id": f'{Tag}${vod.a["href"].split(".")[0]}',
                    "vod_name": vod_name,
                    "vod_pic": vod.img["src"],
                    "vod_remarks": Tag_name + " " + vod.select_one("div.content").a.get_text()
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}{id}.htm"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser").select_one("div.ui.container.movie-info")
        # 取基本数据
        sourcediv = doc.select_one("div.info0")
        module_info_items = sourcediv.select("li")
        director = ""
        actor = ""
        remark_match = re.match("[A-Za-z0-9_ .]*", str(doc.section.p.contents[-1]))
        vod_remarks = remark_match.group(0) if remark_match else ""
        type_name = ""
        vod_year = ""
        vod_area = ""
        for item in module_info_items:
            if item.strong:
                if "导演" in item.strong.get_text():
                    director = ",".join(i.get_text() for i in item.select("a"))
                elif "主演" in item.strong.get_text():
                    actor = ",".join(i.get_text() for i in item.select("a"))
                elif "类型" in item.strong.get_text():
                    type_name = ",".join(i.get_text() for i in item.select("a"))
                elif "上映日期" in item.strong.get_text():
                    vod_year = str(item.contents[-1])
                elif "制片国家/地区" in item.strong.get_text():
                    vod_area = item.get_text().replace("制片国家/地区", "").replace("[", "").replace("]", "")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": doc.h2.get_text().strip(),
            "vod_pic": sourcediv.img["src"],
            "type_name": type_name,
            "vod_year": vod_year,
            "vod_area": vod_area,
            "vod_remarks": vod_remarks,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": doc.select_one("div.summary").get_text().replace("剧情简介：", "").strip()
        }

        vod_play = {}
        # 取播放列表数据
        sources = doc.select("a.ui.secondary.mini.button")
        lines_count = 0
        for source in sources:
            demo = requests.get(url=f'{siteUrl}{source["href"]}', headers=getHeaders(siteUrl))
            demo.encoding = "utf-8"
            lines_count = len(re.findall(r"https:[A-Za-z0-9_ ./\\]*\.m3u8", demo.text))
            if lines_count:
                break
        for i in range(lines_count):
            sourceName = f"线路{i + 1}"
            vodItems = []
            playList = ""
            for source in sources:
                vodItems.append(source.get_text() + "$" + f"{Tag}___" + source["href"].split(".")[0] + f"__{(i + 1) % lines_count}")
                if len(vodItems):
                    playList = "#".join(vodItems)
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
        ids = ids.split("___")
        url = ids[-1].split("__")[0]
        play_from = int(ids[-1].split("__")[-1])
        text = requests.get(url=f"{siteUrl}{url}.htm", headers=getHeaders(siteUrl)).text
        m3u8_url = re.findall(r"https:[A-Za-z0-9_ ./\\]*\.m3u8", text)[play_from].replace("\\", "")
        data = list(requests.get(url=m3u8_url, headers=getHeaders("")).content)[3354:]
        data = zlib.decompress(bytes(data), 16 + zlib.MAX_WBITS).decode()
        m3u8_raw_data = re.sub(r".*?\.ts", add_domain, data)
        return {
            "header": "",
            "parse": "0",
            "playUrl": "",
            "m3u8": m3u8_raw_data
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    res = searchContent("灰影人", "")
    # res = detailContent('bdys_old$/jingsong/22401', "")
    # res = detailContent('bdys_old$/meiju/21647', "")
    # func = "playerContent"
    # res = playerContent("bdys_old___/play/22401-0__1", "", "")
    # res = eval(func)("68614-1-1")
    print(res)
