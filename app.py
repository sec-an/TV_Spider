from spider import *
from flask import Flask, abort, request, jsonify
from flask_cors import CORS
import concurrent.futures

app = Flask(__name__)
cors = CORS(app)


sites = [
    "cokemv",
    "czspp",
    "libvio",
    "smdyy",
    "voflix",
    "yiso"
]


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

        # 搜索
        if wd:
            res = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                to_do = []
                for site in sites:
                    future = executor.submit(eval(f"{site}.searchContent"), wd)
                    to_do.append(future)
                try:
                    for future in concurrent.futures.as_completed(to_do, timeout=5):  # 并发执行
                        # print(future.result())
                        res.extend(future.result())
                except Exception as e:
                    print(e)
            return jsonify({
                "list": res
            })

        # 详情
        if ac and ids:
            vodList = eval(f"{ids.split('$')[0]}.detailContent")(ids)
            return jsonify({
                "list": vodList
            })

        # 播放
        if play and flag:
            playerContent = eval(f"{play.split('___')[0]}.playerContent")(play, flag)
            return playerContent

        return jsonify({
            "list": []
        })
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
