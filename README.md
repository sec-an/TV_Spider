# TV_Spider
服务端爬虫 T4，基于`Python 3`



[站点支持情况（站点根域名字典序）](https://github.com/sec-an/TV_Spider/wiki/%E7%AB%99%E7%82%B9%E6%94%AF%E6%8C%81%E6%83%85%E5%86%B5%EF%BC%88%E7%AB%99%E7%82%B9%E6%A0%B9%E5%9F%9F%E5%90%8D%E5%AD%97%E5%85%B8%E5%BA%8F%EF%BC%89)


[参数说明及如何在TVBoxOSC中调用](https://github.com/sec-an/TV_Spider/wiki/%E5%A6%82%E4%BD%95%E5%9C%A8TVBoxOSC%E4%B8%AD%E8%B0%83%E7%94%A8)

### [DEMO(不支持bdys)](https://t4.secan.icu/vod)：`https://t4.secan.icu/vod?sites=all&ali_token=xxxxxxxxx&timeout=10`
### [备用(不支持bdys,cokemv)](https://t4.run.goorm.io/vod)：`https://t4.run.goorm.io/vod?sites=all&ali_token=xxxxxxxxx&timeout=10`

---

### [腾讯云函数版本](https://github.com/sec-an/TV_Spider/tree/scf)
### 安装及使用说明，请参考[Wiki](https://github.com/sec-an/TV_Spider/wiki)
### 爬虫失效及其它问题，请移步[Issues](https://github.com/sec-an/TV_Spider/issues)


### `仅供Python爬虫学习交流使用！切勿用于违法用途，否则开发者不承担任何责任。`
### `欢迎Star 欢迎PR`

---
### 安装依赖
```pip install -r requirements.txt```
### 运行
```gunicorn -w 4 -b 0.0.0.0:8080 app:app```
### 说明
1. 部分爬虫代码参考自[Tangsan99999 / TvJar](https://github.com/Tangsan99999/TvJar)
