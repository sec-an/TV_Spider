# TV_Spider
服务端爬虫 T4

基于Python 3

[Docker安装步骤]
创建镜像：
docker image build -t tv:latest  .
运行容器：
docker run --name TV --net="host" -v /opt/TV（源码所在目录）:/TV tv:latest gunicorn -w 4 -b 0.0.0.0:8080 app:app

[使用宝塔安装的简略步骤](https://github.com/sec-an/TV_Spider/blob/main/doc/install_through_btpanel.md)
### `仅供Python爬虫学习交流使用！切勿用于违法用途，否则开发者不承担任何责任。`
### `欢迎Star 欢迎PR`
## 当前支持的站点（站点根域名字典序）
|Tag|Name|
| :----: | :----: |
|`cokemv`|[COKEMV影视](https://cokemv.me/)|
|`czspp`|[厂长资源](https://czspp.com/)|
|`gitcafe`|[小纸条](https://u.gitcafe.net/)|
|`libvio`|[LIBVIO影视](https://www.libvio.me/)|
|`smdyy`|[神马影院](https://www.smdyy.cc/)|
|`voflix`|[VOFLIX HD](https://www.voflix.com/)|
|`yiso`|[易搜-网盘搜索](https://yiso.fun/)|
## 在json中调用
```
{
    "key":"t4test",
    "name":"T4测试",
    "type":4,
    // 参数sites可筛选站点，tag用,隔开，不加或sites=all为搜索所有支持的站点
    "api":"http://127.0.0.1:8080/vod?sites=all",
    // "api":"http://127.0.0.1:8080/vod?sites=czspp,yiso",
    "searchable":1,
    "quickSearch":1,
    "filterable":0
}
```
## 安装依赖
```pip install -r requirements.txt```
## 并发搜索超时设置（单位：秒）
https://github.com/sec-an/TV_Spider/blob/1a1a5e5c5b64091e23ac7d8ab510103d98675d6f/app.py#L57
## 阿里云盘token修改
https://github.com/sec-an/TV_Spider/blob/1a1a5e5c5b64091e23ac7d8ab510103d98675d6f/utils/ali.py#L7
## 运行
```gunicorn -w 4 -b 0.0.0.0:8080 app:app```

## 说明
1. 部分爬虫代码参考自[Tangsan99999 / TvJar](https://github.com/Tangsan99999/TvJar)
