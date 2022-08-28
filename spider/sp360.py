# -*- coding:utf-8 -*-
import requests
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


Tag = "sp360"
Tag_name = "360影视"
SiteSearch = "https://api.so.360kan.com"
SiteDetail = "https://api.web.360kan.com"


def getHeaders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; V2049A Build/SP1A.210812.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36",
    }
    return headers


def searchContent(key, token):
    try:
        url = f"{SiteSearch}/index?force_v=1&kw={key}&from=&pageno=1&v_ap=1&tab=all"
        lists = requests.get(url=url, headers=getHeaders()).json()["data"]["longData"]["rows"]
        videos = []
        for vod in lists:
            videos.append({
                "vod_id": f'{Tag}${vod.get("cat_id", "")}_{vod.get("en_id", "")}',
                "vod_name": vod.get("titleTxt", ""),
                "vod_pic": vod.get("cover", ""),
                "vod_remarks": Tag_name + " " + vod.get("score", "")
            })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1].split("_")
        url = f"{SiteDetail}/v1/detail?cat={id[0]}&id={id[1]}"
        data = requests.get(url=url, headers=getHeaders()).json()["data"]
        vodList = {
            "vod_id": ids,
            "vod_name": data.get("title", ""),
            "vod_pic": data.get("cdncover", ""),
            "type_name": ",".join(item for item in data.get("moviecategory", [])),
            "vod_year": data.get("pubdate", ""),
            "vod_area": ",".join(item for item in data.get("area", [])),
            "vod_remarks": data.get("doubanscore", ""),
            "vod_actor": ",".join(item for item in data.get("actor", [])),
            "vod_director": ",".join(item for item in data.get("director", [])),
            "vod_content": data.get("description", ""),
            "vod_play_from": "$$$".join(item for item in data.get("playlink_sites", []))
        }
        delta = 200
        vod_play = {}
        for site in data.get("playlink_sites", []):
            playList = ""
            vodItems = []
            total = int(data["allupinfo"][site])
            for start in range(1, total, delta):
                end = total if (start + delta) > total else start + delta - 1
                vod_data = requests.get(
                    url=url,
                    params={
                        "start": start,
                        "end": end,
                        "site": site
                    },
                    headers=getHeaders()
                ).json()["data"]["allepidetail"]
                for item in vod_data[site]:
                    vodItems.append(item.get("playlink_num", "") + "$" + f"{Tag}___" + item.get("url", ""))
            if len(vodItems):
                playList = "#".join(vodItems)
            if len(playList) == 0:
                continue
            vod_play.setdefault(site, playList)
        if len(vod_play):
            vod_play_url = "$$$".join(vod_play.values())
            vodList.setdefault("vod_play_url", vod_play_url)
        return [vodList]
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        url = ids.split("___")[-1]
        return {
            "parse": 1,
            "playUrl": "",
            "jx": "1",
            "url": url
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("梦华录", "")
    res = detailContent('360kan$2_RbRxbH7lTGTlOH', "")
    print(res)
