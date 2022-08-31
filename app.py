# -*- coding:utf-8 -*-
from spider import *
from utils import douban
from flask import Flask, abort, request, jsonify
from flask_cors import CORS
import concurrent.futures
import json

app = Flask(__name__)
cors = CORS(app)

site_list = [
    "bdys01",
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
    "yiso",
    "zhaoziyuan"
]

with open('./json/douban.json', "r", encoding="utf-8") as f:
    douban_filter = json.load(f)


@app.route('/vod')
def vod():
    try:
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

        sites = request.args.get('sites')
        ali_token = request.args.get('ali_token')
        try:
            timeout = int(request.args.get('timeout'))
        except Exception as e:
            timeout = 5

        if not ali_token:
            ali_token = ""

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
            return douban.cate_filter(t, ext, pg)

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
                    return jsonify({
                        "list": res
                    })
                except Exception as e:
                    print(e)
                    return jsonify({
                        "list": res
                    })

        # 详情
        if ac:
            if len(ids.split('$')) < 2:
                return jsonify({
                    "list": [{
                        "vod_id": "",
                        "vod_name": "请在设置中开启聚合模式，或尝试在上一页面长按图片搜索，或更新软件",
                        "vod_pic": "",
                        "type_name": "",
                        "vod_year": "",
                        "vod_area": "https://github.com/sec-an/TV_Spider",
                        "vod_remarks": "",
                        "vod_actor": "https://github.com/sec-an/TV_Spider",
                        "vod_director": "https://github.com/sec-an/TV_Spider",
                        "vod_content": "T4分类页面由豆瓣APP数据实时生成，与其他网站无关，故无法直接播放，需要开启聚合模式或在上一页面长按图片进入搜索或更新软件至最新版本，感谢理解与支持！"
                    }]
                })
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
    app.run(host='0.0.0.0',port=9000)
