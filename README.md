# TV_Spider
服务端爬虫 T4

基于Python 3


### `仅供Python爬虫学习交流使用！切勿用于违法用途，否则开发者不承担任何责任。`
### `欢迎Star 欢迎PR`
---
## 安装方法

### 1. Docker安装步骤

创建镜像：

docker image build -t tv:latest  .

运行容器：

docker run --name TV --net="host" -v /opt/TV（源码所在目录）:/TV tv:latest gunicorn -w 4 -b 0.0.0.0:8080 app:app

脚本安装、更新：

注意：需要提前安装unzip。openwrt：opkg update && opkg install unzip。ubuntu、debian：apt-get update && apt-get install unzip。其他系统自行百度。

---
### 2. 自定义脚本安装--Docker
下载T4update.sh脚本到任意目录，赋予执行权限。如果有需要自定义内容，请进入脚本在响应位置自行修改。

![T4update说明](https://raw.githubusercontent.com/lm317379829/TV-Spider/main/pic/T4update%E8%AF%B4%E6%98%8E.jpg)

运行脚本，完成安装。

---
### 3. 一键安装--Docker
一键安装命令：

wget --no-check-certificate -qO- "https://raw.githubusercontent.com/sec-an/TV_Spider/main/T4update.sh" -O '/tmp/T4update.sh' && chmod +x /tmp/T4update.sh && bash /tmp/T4update.sh && rm /tmp/T4update.sh

---
### 4. 使用宝塔安装

[使用宝塔安装的简略步骤](https://github.com/sec-an/TV_Spider/blob/main/doc/install_through_btpanel.md)

---

## 当前支持的站点（站点根域名字典序）
|Tag|Name|
| :----: | :----: |
|`bdys01`|[哔滴影视](https://www.bdys01.com)|
|`bttwoo`|[两个BT](https://www.bttwoo.com/)|
|`cokemv`|[COKEMV影视](https://cokemv.me/)|
|`czspp`|[厂长资源](https://czspp.com/)|
|`ddys`|[低端影视](https://ddys.tv/)|
|`dy555`|[555电影](https://555dy.fun/)|
|`gitcafe`|[小纸条](https://u.gitcafe.net/)|
|`libvio`|[LIBVIO影视](https://www.libvio.me/)|
|`onelist`|[Onelist](https://onelist.top/)|
|`smdyy`|[神马影院](https://www.smdyy.cc/)|
|`voflix`|[VOFLIX HD](https://www.voflix.com/)|
|`yiso`|[易搜-网盘搜索](https://yiso.fun/)|
|`zhaoziyuan`|[找资源](https://zhaoziyuan.me/)|
## 在json中调用
```
{
    "key":"t4test",
    "name":"T4测试",
    "type":4,
    // 参数sites可筛选站点，tag用,隔开，不加或sites=all为搜索所有支持的站点
    // 参数ali_token提供阿里系的搜索播放功能（非必须）
    // 参数timeout提供聚合搜索限时返回结果功能，超时数据不再等待，默认5秒
    "api":"http://127.0.0.1:8080/vod?sites=all&ali_token=3xx9cfxxxx509bxx&timeout=5",
    // "api":"http://127.0.0.1:8080/vod",
    // "api":"http://127.0.0.1:8080/vod?sites=czspp,yiso",
    // "api":"http://127.0.0.1:8080/vod?ali_token=3xx9cfxxxx509bxx",
    "searchable":1,
    "quickSearch":1,
    "filterable":0
}
```
## 安装依赖
```pip install -r requirements.txt```
## 运行
```gunicorn -w 4 -b 0.0.0.0:8080 app:app```

## 说明
1. 部分爬虫代码参考自[Tangsan99999 / TvJar](https://github.com/Tangsan99999/TvJar)
