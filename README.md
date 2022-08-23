# TV_Spider
服务端爬虫 T4
### `仅供Python爬虫学习交流使用！切勿用于违法用途，否则开发者不承担任何责任。`
### `欢迎PR`
## 在json中调用
```{"key":"t4test","name":"T4测试","type":4,"api":"http://127.0.0.1:8080/vod","searchable":1,"quickSearch":1,"filterable":0}```
## 安装依赖
```pip install -r requirements.txt```
## 阿里云盘token修改
https://github.com/sec-an/TV_Spider/blob/52fc12898113ed4d26c75eb1d6054cf3f3341d90/utils/ali.py#L7
## 运行
```gunicorn -w 4 -b 0.0.0.0:8080 app:app```

## 说明
1. 部分爬虫代码参考自[Tangsan99999 / TvJar](https://github.com/Tangsan99999/TvJar)
