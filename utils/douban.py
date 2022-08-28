# -*- coding:utf-8 -*-
import requests
import base64
import json
import math
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


douban_api_host = 'https://frodo.douban.com/api/v2'
miniapp_apikey = '0ac44ae016490db2204ce0a042db2916'
count = 30


def miniapp_request(path, query):
    try:
        url = f'{douban_api_host}{path}'
        query.update({
            'apikey': miniapp_apikey
        })
        headers = {
            "Host": "frodo.douban.com",
            "Connection": "Keep-Alive",
            "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat"
        }
        res = requests.get(url=url, params=query, headers=headers)
        res.encoding = res.apparent_encoding
        return res.json()
    except Exception as e:
        print(e)
    return {}


def cate_filter(type, ext, pg):
    try:
        if type.startswith("rank_list"):
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
                id = data.popitem()[1]
            else:
                id = "movie_weekly_best" if type == "rank_list_movie" else "tv_chinese_best_weekly"
            path = f"/subject_collection/{id}/items"
            res = miniapp_request(path, {
                "start": (int(pg) - 1) * count,
                "count": count
            })
        else:
            path = f"/{type}/recommend"
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
                sort = data.pop('sort') if "sort" in data else "T"
                tags = ",".join(item for item in data.values())
                if type == "movie":
                    selected_categories = {
                        "类型": data.get("类型", ""),
                        "地区": data.get("地区", "")
                    }
                else:
                    selected_categories = {
                        "类型": data.get("类型", ""),
                        "形式": data.get(f"{data.get('类型', '')}地区", ""),
                        "地区": data.get("地区", "")
                    }
            else:
                sort = "T"
                tags = ""
                if type == "movie":
                    selected_categories = {
                        "类型": "",
                        "地区": ""
                    }
                else:
                    selected_categories = {
                        "类型": "",
                        "形式": "",
                        "地区": ""
                    }
            params = {
                "tags": tags,
                "sort": sort,
                "refresh": 0,
                "selected_categories": json.dumps(selected_categories, separators=(',', ':'), ensure_ascii=False),
                "start": (int(pg) - 1) * count,
                "count": count
            }
            res = miniapp_request(path, params)
        result = {
            "page": pg,
            "pagecount": math.ceil(res["total"] / count),
            "limit": count,
            "total": res["total"]
        }
        if type.startswith("rank_list"):
            items = res['subject_collection_items']
        else:
            items = res["items"]
        lists = []
        for item in items:
            if item.get("type", "") == "movie" or item.get("type", "") == "tv":
                lists.append({
                    "vod_id": item.get("id", ""),
                    "vod_name": item.get("title", ""),
                    "vod_pic": item.get("pic", "").get("normal", ""),
                    "vod_remarks": item.get("rating", "").get("value", "")
                })
        result.setdefault("list", lists)
        return result
    except Exception as e:
        print(e)
    return {}


def subject_real_time_hotest():
    try:
        res = miniapp_request("/subject_collection/subject_real_time_hotest/items", {})
        lists = []
        for item in res["subject_collection_items"]:
            if item.get("type", "") == "movie" or item.get("type", "") == "tv":
                lists.append({
                    "vod_id": item.get("id", ""),
                    "vod_name": item.get("title", ""),
                    "vod_pic": item.get("pic", "").get("normal", ""),
                    "vod_remarks": item.get("rating", "").get("value", "")
                })
        return lists
    except Exception as e:
        print(e)
    return []


if __name__ == '__main__':
    # res = cate_filter("movie", "eyLnsbvlnosiOiLllpzliacifQ==", "1")
    res = cate_filter("rank_list_movie", "", "1")
    # res = subject_real_time_hotest()
    print(res)
