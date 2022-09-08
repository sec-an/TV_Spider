FROM python:slim-buster	

WORKDIR /TV
COPY . /TV
RUN pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ -r /TV/requirements.txt \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone