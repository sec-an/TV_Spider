#!/bin/bash
rm -rf ./src
echo "开始下载源码"
wget --no-check-certificate -qO- "https://codeload.github.com/sec-an/TV_Spider/zip/refs/heads/scf" -O './tvsp_scf.zip'
echo "下载成功"
mkdir ./tvsp_scf
echo "准备解压源码"
unzip ./tvsp_scf.zip -d ./tvsp_scf  >/dev/null 2>&1
echo "解压成功，准备更新文件"
mv -vf ./tvsp_scf/TV_Spider-scf ./src
echo "解压完成，准备安装依赖"
rm -rf ./tvsp_scf.zip
rm -rf ./tvsp_scf
cd src/
pip3 install -r requirements.txt -t .
echo "更新结束"
exit
