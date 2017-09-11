FROM python:3.6
MAINTAINER chigusa
RUN apk update && \
    apk add git && \
    pip install pymediainfo && \
    git clone "https://github.com/hr3lxphr6j/BiliLive"
VOLUME /live
CMD python BiliLive/start.py
