# -*- coding:utf-8 -*-
import requests
from aligo import *
import re
import json
import threading
import inspect
import ctypes
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None


ali = ""


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class ali_login(threading.Thread):
    def __init__(self, token):
        threading.Thread.__init__(self)
        self.token = token

    def run(self):
        self._return = Aligo(self.token, refresh_token=self.token)

    def join(self):
        super().join(timeout=3)
        return self._return


def login(token):
    try:
        login_thread = ali_login(token)
        login_thread.daemon = True
        login_thread.start()
        ali = login_thread.join()
        return ali
    except Exception as e:
        if login_thread.is_alive():
            stop_thread(login_thread)
        print(e)
        return ""


Folder = re.compile("www.aliyundrive.com/s/([\w]+)(/folder/([\w]+))?")


def get_file_list(file_list, share_id, share_token, file_id):
    try:
        global ali
        body = GetShareFileListRequest(
            share_id=share_id,
            all=True,
            parent_file_id=file_id,
            image_thumbnail_process="image/resize,w_160/format,jpeg",
            image_url_process="image/resize,w_1920/format,jpeg",
            order_by="updated_at",
            order_direction="DESC",
            video_thumbnail_process="video/snapshot,t_1000,f_jpg,ar_auto,w_300"
        )
        folder_list = []
        file_list_items = ali.get_share_file_list(body=body, share_token=share_token.share_token)
        for item in file_list_items:
            if item.type == "folder":
                folder_list.append(item.file_id)
            else:
                if "video" in item.mime_type or "vnd.rn-realmedia-vbr" in item.mime_type or "video" in item.category:
                    file_name = item.name.replace("#", "_").replace("$", "_")
                    file_list.setdefault(file_name, share_id + "__" + share_token + "__" + item.file_id + "__" + item.category)
        for folder in folder_list:
            try:
                get_file_list(file_list, share_id, share_token, folder)
            except Exception as e:
                print(e)
                return
    except Exception as e:
        print(e)


def getpreviewUrl(share_id, share_token, file_id):
    try:
        global ali
        url = "https://api.aliyundrive.com/v2/file/get_share_link_video_preview_play_info"
        data = {
            "share_id": share_id,
            "category": "live_transcoding",
            "file_id": file_id,
            "template_id": ""
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
            "Referer": "https://www.aliyundrive.com/",
            "x-share-token": share_token,
            "authorization": ali._auth.token.access_token
        }
        res = requests.post(url=url, data=json.dumps(data), headers=headers).json()
        if "code" in res:
            print(res["message"])
            return ""
        live_transcoding_task_list = res['video_preview_play_info']['live_transcoding_task_list']
        live_transcoding_task_list.reverse()
        redirect_headers = requests.get(url=live_transcoding_task_list[0]["url"], headers=headers, allow_redirects=False).headers
        if "Location" in redirect_headers:
            preview_url = redirect_headers["Location"]
        else:
            preview_url = redirect_headers["location"]
        return preview_url
    except Exception as e:
        print(e)
    return ""


def getdownloadUrl(share_id, share_token, file_id, category):
    try:
        global ali
        body = GetShareLinkDownloadUrlRequest(
            share_id=share_id,
            file_id=file_id
        )
        if category == "audio":
            body.get_audio_play_info = True
        return ali.get_share_link_download_url(body=body, share_token=share_token)
    except Exception as e:
        print(e)
    return ""


def getdetailContent(tag, url, token):
    try:
        global ali
        if ali == "":
            ali = login(token)
        pattern = Folder
        matcher = pattern.search(url)
        if not matcher:
            return []
        share_id = matcher.group(1)
        if matcher.re.groups == 3:
            file_id = matcher.group(3)
        else:
            file_id = ""
        share_info = ali.get_share_info(share_id=share_id)
        try:
            data = json.loads(share_info.response.text)
            if "code" in data:
                print(data.get("message", "unknown error"))
                return []
        except Exception as e:
            pass
        file_infos = share_info.file_infos
        if len(file_infos) == 0:
            print("该文件夹下没有分享的文件")
            return []
        fileinfo = file_infos[0]
        if not file_id:
            file_id = fileinfo.file_id
        vodList = {
            "vod_id": f"{tag}${url}",
            "vod_name": share_info.share_name,
            "vod_pic": share_info.avatar,
            "vod_content": url,
            "vod_play_from": "AliYun原画$$$AliYun"
        }
        file_type = fileinfo.type
        if file_type != "folder":
            if file_type == "file" and fileinfo.category == "video":
                file_id = "root"
            else:
                print(f"such file is a {fileinfo.category}")
                return []
        share_token = ali.get_share_token(share_id=share_id)
        file_list = {}
        get_file_list(file_list, share_id, share_token, file_id)
        vodItems = []
        for file in sorted(file_list):
            vodItems.append(file + "$" + f"{tag}___" + file_list[file])
        vodList.setdefault("vod_play_url", "#".join(vodItems) + "$$$" + "#".join(vodItems))
        return [vodList]
    except Exception as e:
        print(e)
    return []


def getplayerContent(id, flag, token):
    try:
        global ali
        if ali == "":
            ali = login(token)
        split = id.split("__")
        headers = {
            "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
            "Referer": " https://www.aliyundrive.com/"
        }
        if flag == "AliYun":
            return {
                "header": json.dumps(headers),
                "parse": 0,
                "playUrl": "",
                "url": getpreviewUrl(split[0], split[1], split[2])
            }
        else:
            DownloadURL = getdownloadUrl(split[0], split[1], split[2], split[3]).download_url
            redirect_headers = requests.get(
                url=DownloadURL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
                    "Referer": "https://www.aliyundrive.com/"
                },
                allow_redirects=False
            ).headers
            if "Location" in redirect_headers:
                url = redirect_headers["Location"]
            else:
                url = redirect_headers["location"]
            return {
                "header": json.dumps(headers),
                "parse": 0,
                "playUrl": "",
                "url": url
            }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = getdetailContent("yiso", "https://www.aliyundrive.com/s/ovXEyo9rXZA")
    # res = getdetailContent("yiso", "https://www.aliyundrive.com/s/ovXEyo9rXZA/folder/620901133b89c3f1a3934fd1a9662cdb9cd8744a")
    res = getplayerContent("ovXEyo9rXZA+eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21Kc29uIjoie1wiZG9tYWluX2lkXCI6XCJiajI5XCIsXCJzaGFyZV9pZFwiOlwib3ZYRXlvOXJYWkFcIixcImNyZWF0b3JcIjpcIjViOWQwYTNhMGJjZDQzZjlhZTlmZmFmMzFhMmU4Mjg4XCIsXCJ1c2VyX2lkXCI6XCJhbm9ueW1vdXNcIn0iLCJjdXN0b21UeXBlIjoic2hhcmVfbGluayIsImV4cCI6MTY2MTI3NjM5MCwiaWF0IjoxNjYxMjY5MTMwfQ.g2UWvLg14f_Bo-ev3Cx1TcQOBlma747XuxLh7ZAhqBe6bTd1jZPYmHA3SsaU5yiXLuHJAOvmcWgSTl63PZEQbhoITqk1pmxWj1jYuZMsC6gRkWBkcNBf47-3uX47_taB0RXKf_GYrnMeKQPNrHpd-tcRxTlTToHkWFx1J6i9vM0+6304dc47df5760b706354d7eab33db3c0066ce76+video", "AliYun")
    print(res)
