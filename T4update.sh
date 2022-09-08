#!/bin/bash
#定义变量
md5o="aaaa"
dkdir=/opt/TV-Spider #(改成自己的目录)
imgtag=tvsp:latest  #(改成自己的镜像TAG)
contname=TV-Spider #(改成自己的容器名称)
cmd='CMD ["gunicorn", "-w 4", "-b 0.0.0.0:8080", "app:app"]' #(从这里更改启动端口)
#判断目录是否存在
if [ ! -d $dkdir ];then
 mkdir $dkdir
else
 echo "文件夹已经存在"
fi
#下载源码
wget --no-check-certificate -qO- "https://codeload.github.com/sec-an/TV_Spider/zip/refs/heads/main" -O '/tmp/tvsp.zip'
md5n=$(md5sum /tmp/tvsp.zip | awk '{print $1}')
#更新
if [[ $md5n != $md5o && -s /tmp/tvsp.zip ]];then
 echo 开始更新。。。
 docker stop $contname
 cudir=$(cd $(dirname $0); pwd)
 sed -i "s/$md5o/$md5n/g" $cudir/T4update.sh
 #解压缩
 mkdir /tmp/tvsp/
 unzip /tmp/tvsp.zip -d /tmp/tvsp/  >/dev/null 2>&1
#文件变更，更新文件 
 echo 爬虫文件变更，正在更新文件开始更新。。。
 rm -rf $dkdir/app.py
 rm -rf $dkdir/utils/
 rm -rf $dkdir/spider/
 rm -rf $dkdir/json/
 cp  /tmp/tvsp/TV_Spider-main/app.py $dkdir/app.py
 cp -r /tmp/tvsp/TV_Spider-main/utils/ $dkdir/utils/
 cp -r /tmp/tvsp/TV_Spider-main/spider/ $dkdir/spider/
 cp -r /tmp/tvsp/TV_Spider-main/json/ $dkdir/json/
 rqmd5o=$(md5sum /tmp/tvsp/TV_Spider-main/requirements.txt | awk '{print $1}')
 rqmd5n=$(md5sum $dkdir/requirements.txt | awk '{print $1}')
 #依赖变更，更新镜像
 if [[ $rqmd5n != $rqmd5o && -s /tmp/tvsp/TV_Spider-main/requirements.txt ]];then
  echo 依赖变更，正在更新镜像。。。
  rm -rf $dkdir/*
  mv /tmp/tvsp/TV_Spider-main/requirements.txt $dkdir/requirements.txt
  mv /tmp/tvsp/TV_Spider-main/dockerfile $dkdir/dockerfile
  echo "">>$dkdir/dockerfile
  echo $cmd >>$dkdir/dockerfile
  docker rm $contname
  docker rmi $imgtag
  cd $dkdir
  docker image build -t $imgtag .
  cd $cudir
  mv /tmp/tvsp/TV_Spider-main/app.py $dkdir/app.py
  mv /tmp/tvsp/TV_Spider-main/utils/ $dkdir/utils/
  mv /tmp/tvsp/TV_Spider-main/spider/ $dkdir/spider/
  mv /tmp/tvsp/TV_Spider-main/json/ $dkdir/json/
  #运行DOCKER
  docker run --restart=always --name $contname --net="host" -v $dkdir:/TV $imgtag 2>&1 &
 fi
#删除临时文件
 rm -rf /tmp/tvsp/
#重启DOCKER
 docker start $contname
 echo 更新完成。
else
 echo 无需更新。
fi
rm -rf /tmp/tvsp.zip

exit
