# -*- coding:utf-8 -*-
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import re
import json
from utils import utils_dy555
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

Tag = "dy555"
Tag_name = "555电影"
siteUrl = "https://555dy.fun"
playerConfig = {
    "xg_app_player": {
        "show": "app全局解析",
        "des": "",
        "ps": "1",
        "parse": "https://www.x-n.cc/api.php?url="
    },
    "duoduozy": {
        "show": "555蓝光",
        "des": "",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newduoduo/555tZ4pvzHE3BpiO838.php",
        "parse": "https://zyz.sdljwomen.com/server_player/?url="
    },
    "ddzy": {
        "show": "多多资源",
        "des": "",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newduoduo/555tZ4pvzHE3BpiO838.php",
        "parse": "https://zyz.sdljwomen.com/server_player/?url="
    },
    "bilibili": {
        "show": "bilibili",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "youku": {
        "show": "优酷",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "qiyi": {
        "show": "爱奇艺",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "mgtv": {
        "show": "芒果",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "qq": {
        "show": "腾讯",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "sohu": {
        "show": "搜狐",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "pptv": {
        "show": "PPTV",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "m1905": {
        "show": "m1905",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "xigua": {
        "show": "西瓜视频",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "fuckapp": {
        "show": "独家线路",
        "des": "555自建资源",
        "ps": "0",
        "parse": "https://dp.dd520.cc/p.php?url="
    },
    "letv": {
        "show": "乐视",
        "des": "",
        "ps": "0",
        "api": "https://jhpc.021huaying.com/newplayer/5348837768203767939.php",
        "parse": "https://jhpc.021huaying.com/newplayer/?url="
    },
    "yemao": {
        "show": "优质线路1",
        "des": "极速蓝光",
        "ps": "0",
        "parse": "https://jx.manduhu.com/?url="
    },
    "sdm3u8": {
        "show": "闪电线路",
        "des": "闪电",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "fsm3u8": {
        "show": "飞速线路",
        "des": "飞速",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "wjm3u8": {
        "show": "无尽线路",
        "des": "无尽",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "dbm3u8": {
        "show": "百度线路",
        "des": "百度",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "tkm3u8": {
        "show": "天空线路",
        "des": "天空",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "kbm3u8": {
        "show": "快播线路",
        "des": "快播",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    },
    "zhibo": {
        "show": "直播",
        "des": "",
        "ps": "1",
        "parse": "http://suoyou.live/dplay/zb.php?url="
    },
    "dujia": {
        "show": "独家专线",
        "des": "",
        "ps": "0",
        "api": "https://zyz.sdljwomen.com/newm3u8/5348837768203767939.php",
        "parse": "https://zyz.sdljwomen.com/newm3u8/?url="
    }
}


def getHeaders(url):
    headers = {}
    headers.setdefault("method", "GET")
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("Accept-Encoding", "gzip: deflate: br")
    headers.setdefault("Upgrade-Insecure-Requests", "1")
    headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    headers.setdefault(
        "Accept",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
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
                videos.append({
                    "vod_id": f'{Tag}${vod.get("id")}',
                    "vod_name": vod.get("name"),
                    "vod_pic": vod.get("pic"),
                    "vod_remarks": Tag_name
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/voddetail/{id}.html"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser")
        # 取基本数据
        sourcediv = doc.select("div.module-item-cover>div")
        data = doc.select("div.module-info-tag-link")
        module_info_items = doc.select("div.module-info-item")
        directors = []
        actors = []
        director = ""
        actor = ""
        vod_remarks = ""
        for item in module_info_items:
            if item.span:
                if "导演" in item.span.get_text():
                    bb = item.select("a")
                    for i in bb:
                        directors.append(i.get_text())
                    director = ",".join(directors)
                elif "主演" in item.span.get_text():
                    aa = item.select("a")
                    for i in aa:
                        actors.append(i.get_text())
                    actor = ",".join(actors)
                elif "更新" in item.span.get_text():
                    vod_remarks = item.select_one("div.module-info-item-content").get_text()
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": sourcediv[0].select_one("div.module-item-pic>img")["alt"],
            "vod_pic": sourcediv[0].select_one("div.module-item-pic>img")["data-original"],
            "type_name": ",".join(item.get_text() for item in data[2].select("a")),
            "vod_year": data[0].a.get_text(),
            "vod_area": ",".join(item.get_text() for item in data[1].select("a")),
            "vod_remarks": vod_remarks,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": doc.select_one("div.module-info-introduction-content>p").get_text().strip()
        }

        vod_play = {}
        # 取播放列表数据
        regexPlay = re.compile("/vodplay/(\\d+)-(\\d+)-(\\d+).html")
        sources = doc.select("div.module-tab-items-box>div>span")
        sourceList = doc.select("div.module-list>div.module-play-list")
        for index, source in enumerate(sources):
            sourceName = source.get_text()
            found = False
            for item in playerConfig:
                if playerConfig[item]["show"] == sourceName:
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
        url = f"{siteUrl}/vodplay/{id}.html"
        headers = {
            "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "origin": "https://player.sakurot.com:3458"
        }
        allScript = BeautifulSoup(requests.get(url=url, headers=getHeaders("")).text, "html.parser").select("script")
        for item in allScript:
            scContent = item.get_text().strip()
            if scContent.startswith("var player_"):
                player = json.loads(scContent[scContent.find('{'):scContent.rfind('}') + 1])
                if player.get("from") in playerConfig:
                    return {
                        "header": json.dumps(headers),
                        "parse": 0,
                        "playUrl": "",
                        "url": utils_dy555.get_m3u8(player.get("url"))
                    }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("壮志凌云", "")
    res = detailContent('555dy$359288', "")
    # func = "playerContent"
    # res = playerContent("555dy___359288-1-1", "", "")
    # res = playerContent("555dy___359288-5-1", "", "")
    # res = eval(func)("68614-1-1")
    print(res)
