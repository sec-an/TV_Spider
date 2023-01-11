# -*- coding:utf-8 -*-
from spider import *
from utils import douban
from flask import Flask, abort, request, jsonify
from flask_cors import CORS
from flask_compress import Compress
import concurrent.futures
import json
import copy


app = Flask(__name__)
cors = CORS(app)
Compress(app)


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

        # 分类数据
        if t:
            return douban.cate_filter(t, ext, pg, douban_id)

        # 搜索
        if wd:
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
                except Exception as e:
                    print(e)
                    import atexit
                    atexit.unregister(concurrent.futures.thread._python_exit)
                    executor.shutdown = lambda wait: None
            return jsonify({
                "list": res
            })

        # 详情
        if ac:
            if len(ids.split('$')) < 2:
                vodList = douban.douban_detail(ids)
            else:
                vodList = eval(f"{ids.split('$')[0]}.detailContent")(ids, ali_token)
            return jsonify({
                "list": vodList
            })

        # 播放
        if play and flag:
            playerContent = eval(f"{play.split('___')[0]}.playerContent")(play, flag, ali_token)
            return playerContent


        douban_filter["list"] = douban.subject_real_time_hotest()
        return jsonify(douban_filter)

        # return jsonify({
        #     "list": search_sites
        # })
    except Exception as e:
        print(e)
        return jsonify({
            "list": []
        })


@app.route('/')
def hello_world():  # put application's code here
    abort(403)


if __name__ == '__main__':
    app.run()