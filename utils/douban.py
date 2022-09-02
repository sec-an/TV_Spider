# -*- coding:utf-8 -*-
import requests
import json
import math
import urllib3
import base64



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


def cate_filter(type, ext, pg, douban):
    try:
        if type == "interests":
            data = {}
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
            status = data.get("status", "mark")
            subtype_tag = data.get("subtype_tag", "")
            year_tag = data.get("year_tag", "全部")
            path = f"/user/{douban}/interests"
            res = miniapp_request(path, {
                "type": "movie",
                "status": status,
                "subtype_tag": subtype_tag,
                "year_tag": year_tag,
                "start": (int(pg) - 1) * count,
                "count": count
            })
        elif type == "hot_gaia":
            data = {}
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
            sort = data.get("sort", "recommend")
            area = data.get("area", "全部")
            path = f"/movie/{type}"
            res = miniapp_request(path, {
                "area": area,
                "sort": sort,
                "start": (int(pg) - 1) * count,
                "count": count
            })
        elif type == "tv_hot" or type == "show_hot":
            data = {}
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
            s_type = data.get("type", type)
            path = f"/subject_collection/{s_type}/items"
            res = miniapp_request(path, {
                "start": (int(pg) - 1) * count,
                "count": count
            })
        elif type.startswith("rank_list"):
            id = "movie_real_time_hotest" if type == "rank_list_movie" else "tv_real_time_hotest"
            if ext:
                data = json.loads(base64.b64decode(ext).decode("utf-8"))
                try:
                    id = data.popitem()[1]
                except Exception as e:
                    pass
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
        if type == "tv_hot" or type == "show_hot" or type.startswith("rank_list"):
            items = res['subject_collection_items']
        elif type == "interests":
            items = []
            for item in res["interests"]:
                items.append(item["subject"])
        else:
            items = res["items"]
        lists = []
        for item in items:
            if item.get("type", "") == "movie" or item.get("type", "") == "tv":
                rating = item.get("rating", "").get("value", "") if item.get("rating", "") else ""
                title = item.get("title", "")
                lists.append({
                    "vod_id": f'msearch:{item.get("type", "")}__{item.get("id", "")}',
                    "vod_name": title if title != "未知电影" else "暂不支持展示",
                    "vod_pic": item.get("pic", "").get("normal", ""),
                    "vod_remarks": str(rating if rating else "暂无评分") + " " + " | ".join(honor["title"] for honor in item.get("honor_infos", []))
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
                rating = item.get("rating", "").get("value", "") if item.get("rating", "") else ""
                lists.append({
                    "vod_id": "",
                    "vod_name": item.get("title", ""),
                    "vod_pic": item.get("pic", "").get("normal", ""),
                    "vod_remarks": str(rating if rating else "暂无评分") + " " + " | ".join(honor["title"] for honor in item.get("honor_infos", []))
                })
        return lists
    except Exception as e:
        print(e)
    return []


def douban_detail(ids):
    try:
        id = ids.split(":")[-1].split("__")
        res = miniapp_request(f"/{id[0]}/{id[1]}", {})
        vodList = {
            "vod_id": ids,
            "vod_name": res.get("title", ""),
            "vod_pic": res.get("pic", "").get("normal", ""),
            "type_name": ",".join(item for item in res.get('genres', [])),
            "vod_year": res.get("year", ""),
            "vod_area": ",".join(item for item in res.get('countries', [])),
            "vod_remarks": "请使用快速搜索或升级软件",
            "vod_actor": ",".join(item["name"] for item in res.get("actors", [])),
            "vod_director": ",".join(item["name"] for item in res.get("directors", [])),
            "vod_content": res.get("intro", ""),
            "vod_play_from": "本页面数据来自豆瓣$$$观看影片请点击上方快速搜索$$$或升级至最新版软件",
            "vod_play_url": "$$$"
        }
        return [vodList]
    except Exception as e:
        print(e)
    return []


if __name__ == '__main__':
    # res = cate_filter("movie", "eyLnsbvlnosiOiLllpzliacifQ==", "1")
    # res = cate_filter("rank_list_movie", "", "1")
    res = douban_detail("movie__35131346")
    # res = subject_real_time_hotest()
    print(res)
