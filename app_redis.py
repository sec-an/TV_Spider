# -*- coding:utf-8 -*-
from spider import *
from utils import douban
from flask import Flask, abort, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from flask_compress import Compress
import concurrent.futures
import json
import random
import string
import time
import copy

T4_Url = "https://t4.secan.icu"


redis_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 3
}


app = Flask(__name__)
cors = CORS(app)
Compress(app)
cache = Cache(app=app, config=redis_config)
cache.clear()

site_list = [
    "bdys01",
    "bdys_old",
    "bttwoo",
    "cokemv",
    "czspp",
    "ddys",
    "dy555",
    "gitcafe",
    "lezhutv",
    "libvio",
    "onelist",
    "smdyy",
    "sp360",
    "voflix",
    "yhdm",
    "yiso",
    "zhaoziyuan"
]

ali_sites = ["gitcafe", "yiso", "zhaoziyuan"]

with open('./json/douban.json', "r", encoding="utf-8") as f:
    douban_basic = json.load(f)


@app.route('/vod')
def vod():
    try:
        douban_filter = copy.deepcopy(douban_basic)
        wd = request.args.get('wd')
        ac = request.args.get('ac')
        quick = request.args.get('quick')
        play = request.args.get('play')
        flag = request.args.get('flag')
        filter = request.args.get('filter')
        t = request.args.get('t')
        pg = request.args.get('pg')
        ext = request.args.get('ext')
        ids = request.args.get('ids')
        q = request.args.get('q')
        douban_id = request.args.get('douban')

        sites = request.args.get('sites')
        ali_token = request.args.get('ali_token')
        try:
            timeout = int(request.args.get('timeout'))
        except Exception as e:
            timeout = 10

        if not ali_token:
            ali_token = ""

        if not douban_id:
            douban_id = ""
            douban_filter["class"].pop(0)
            douban_filter["filters"].pop("interests")

        # 站点筛选
        search_sites = []
        if not sites or sites == "all":
            search_sites = site_list
        else:
            try:
                for site in sites.split(","):
                    if site in site_list:
                        search_sites.append(site)
            except Exception as e:
                print(e)
                search_sites = site_list
        sites_key = "".join(sorted(search_sites))

        # 分类数据
        if t:
            if t == "interests":
                res = cache.get(f"{t}_{ext}_{pg}_{douban_id}")
                if not res:
                    res = douban.cate_filter(t, ext, pg, douban_id)
                    if res:
                        cache.set(f"{t}_{ext}_{pg}_{douban_id}", res, timeout=60 * 15)
            else:
                res = cache.get(f"{t}_{ext}_{pg}")
                if not res:
                    res = douban.cate_filter(t, ext, pg, douban_id)
                    if res:
                        cache.set(f"{t}_{ext}_{pg}", res, timeout=60*60*2)
            return res

        # 搜索
        if wd:
            key_name = f"search__{wd}__{sites_key}"
            if ali_token:
                key_name += "__ali"
            res = cache.get(key_name)
            if res:
                return jsonify({
                    "list": res
                })
            else:
                res = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(search_sites)) as executor:
                    to_do = []
                    for site in search_sites:
                        future = executor.submit(eval(f"{site}.searchContent"), wd, ali_token)
                        to_do.append(future)
                    try:
                        for future in concurrent.futures.as_completed(to_do, timeout=timeout):  # 并发执行
                            # print(future.result())
                            res.extend(future.result())
                        if res:
                            cache.set(key_name, res, timeout=60*30)
                    except Exception as e:
                        print(e)
                        import atexit
                        atexit.unregister(concurrent.futures.thread._python_exit)
                        executor.shutdown = lambda wait: None
                    finally:
                        return jsonify({
                            "list": res
                        })

        # 详情
        if ac:
            vodList = cache.get(f"detail__{ids}")
            if not vodList:
                if len(ids.split('$')) < 2:
                    vodList = douban.douban_detail(ids)
                    if vodList:
                        cache.set(f"detail__{ids}", vodList, 60 * 60 * 24)
                else:
                    vodList = eval(f"{ids.split('$')[0]}.detailContent")(ids, ali_token)
                    if vodList:
                        if ids.split('$')[0] not in ali_sites:
                            cache.set(f"detail__{ids}", vodList, 60 * 20)
                    # else:
                    #     with open("error_detail.txt", "a") as f:
                    #         f.write(f"{ids}\n")
            return jsonify({
                "list": vodList
            })

        # 播放
        if play and flag:
            playerContent = eval(f"{play.split('___')[0]}.playerContent")(play, flag, ali_token)
            if len(playerContent) == 0:
                pass
                # with open("error_play.txt", "a") as f:
                #     f.write(f"{play}\n")
            else:
                if "m3u8" in playerContent:
                    file_name = ''.join(random.sample(string.ascii_letters + string.digits, 5)) + '_' + str(
                        int(round(time.time() * 1000)))
                    cache.set(f"m3u8_{file_name}", playerContent.pop("m3u8"), 60 * 5)
                    playerContent["url"] = f"{T4_Url}/m3u8proxy/{file_name}"
            return playerContent

        real_time_hotest = cache.get("real_time_hotest")
        if not real_time_hotest:
            real_time_hotest = douban.subject_real_time_hotest()
            if real_time_hotest:
                cache.set("real_time_hotest", real_time_hotest, 60*60)
        douban_filter["list"] = real_time_hotest
        return jsonify(douban_filter)

        # return jsonify({
        #     "list": search_sites
        # })
    except Exception as e:
        print(e)
        return jsonify({
            "list": []
        })


@app.route('/m3u8proxy/<string:file_name>')
def m3u8_proxy(file_name):
    try:
        m3u8_raw = cache.get(f"m3u8_{file_name}")
        return m3u8_raw, 200, {'Content-Type': 'application/vnd.apple.mpegurl'}
    except Exception as e:
        print(e)
        abort(404)


@app.route('/')
def hello_world():  # put application's code here
    abort(403)


if __name__ == '__main__':
    app.run()
