# BiliLive
垃圾一样的Bilibili直播录制工具   
目前支持哔哩哔哩，熊猫TV

![image](https://github.com/hr3lxphr6j/BiliLive/raw/master/screenshot/shot.png)

## 依赖
* python3.x(推荐3.6)
* requests
* ffmpeg

## 使用
`python start.py`

## config.json配置说明

目录下的config.json为演示文件，默认会读取`$HOME/.bililive/config.json`

| 属性 | 说明 |
| :----: | :----:|
| ROOM_URLS | 直播间URL |
| POLLING_INTERVAL | 状态查询间隔 |
| LAZY_TIME | 状态确认后录制延迟时间 |
| OUTPUT_FILE_EXT | 输出文件封装方式 |
| OUTPUT_DIR | 输出目录 |


# DLC AutoSplitVideo
快速分割直播视频用的，非直播视频慎用（IDR区间很短也可以吧。。。）
1小时分割一个，末尾的一个分段如果小于5分钟不分割（想要其他时间自己去改吧，懒得写参数了orz）
## 依赖
* pymediainfo
* MediaInfo
* ffmpeg
## 使用
`python AutoSplitVideo.py <input>`