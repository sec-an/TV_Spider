# -*- coding:utf-8 -*-
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import ddddocr
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "bdys01"
Tag_name = "哔滴影视"
siteUrl = "https://www.bdys01.com"


def getHeaders(url):
    headers = {}
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("Accept-Encoding", "gzip, deflate, br")
    headers.setdefault("DNT", "1")
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    headers.setdefault("Accept", "*/*")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")
    return headers


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
                url=f"https://www.bdys01.com/search/verifyCode?t={str(int(round(time.time() * 1000)))}",
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
        finally:
            retry = retry - 1

def searchContent(key, token):
    try:
        res = verifyCode(key)
        searchResult = BeautifulSoup(res, "html.parser")
        videos = []
        lists = searchResult.select("div.row.row-0")
        for vod in lists:
            vod_name = vod.select_one("div.card-body.py-0.pe-1").a["title"]
            if key in vod_name:
                videos.append({
                    "vod_id": f'{Tag}${vod.a["href"].split(".")[0]}',
                    "vod_name": vod_name,
                    "vod_pic": vod.img["src"],
                    "vod_remarks": Tag_name + " " + vod.select_one("div.card-body.py-0.pe-1").a.get_text()
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/{id}.htm"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser").select_one("div.container-xl.clear-padding-sm.my-3.py-1")
        # 取基本数据
        sourcediv = doc.select_one("div.card-body")
        module_info_items = sourcediv.select("p")
        director = ""
        actor = ""
        vod_remarks = ""
        type_name = ""
        vod_year = ""
        vod_area = ""
        for item in module_info_items:
            if item.strong:
                if "导演" in item.strong.get_text():
                    director = ",".join(i.get_text() for i in item.select("a"))
                elif "主演" in item.strong.get_text():
                    actor = ",".join(i.get_text() for i in item.select("a"))
                elif "摘要" in item.strong.get_text():
                    vod_remarks = item.span.get_text()
                elif "类型" in item.strong.get_text():
                    type_name = ",".join(i.get_text() for i in item.select("a"))
                elif "上映日期" in item.strong.get_text():
                    vod_year = ",".join(i.get_text() for i in item.select("a"))
                elif "制片国家/地区" in item.strong.get_text():
                    vod_area = item.get_text().replace("制片国家/地区", "").replace("[", "").replace("]", "")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": sourcediv.h2.get_text(),
            "vod_pic": sourcediv.img["src"],
            "type_name": type_name,
            "vod_year": vod_year,
            "vod_area": vod_area,
            "vod_remarks": vod_remarks,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": doc.select_one("div.card.collapse").select_one("div.card-body").get_text().strip(),
            "vod_play_from": "哔滴磁力"
        }

        # 取播放列表数据
        sources = doc.select_one("tbody").select("tr")
        vodItems = []
        for source in sources:
            sourceName = source.select_one("td.text-muted").get_text()
            vodItems.append(sourceName + "$" + source.a["href"])
        if len(vodItems):
            playList = "#".join(vodItems)
        vodList.setdefault("vod_play_url", playList)
        return [vodList]

        # sources = doc.select_one("tbody").select("tr")
        # vodItems = []
        # result = []
        # for source in sources:
        #     sourceName = source.select_one("td.text-muted").get_text()
        #     vodList["vod_play_url"] = sourceName + "$" + source.a["href"]
        #     result.append(vodList.copy())
        # return result
    except Exception as e:
        print(e)
    return []


if __name__ == '__main__':
    # res = searchContent("冰雨火", "")
    res = detailContent('bdys01$/guoju/22288', "")
    # func = "playerContent"
    # res = playerContent("40542-1-1")
    # res = eval(func)("68614-1-1")
    print(res)
