# BiliLive
垃圾一样的Bilibili直播录制工具
![image](https://github.com/hr3lxphr6j/BiliLive/raw/master/screenshot/shot.png)

## 依赖
* requests
* ffmpeg

## 使用
`python start.py`

## config.json配置说明

| 属性 | 说明 |
| :----: | :----:|
| ROOM_IDS | 房间ID |
| POLLING_INTERVAL | 状态查询间隔 |
| LAZY_TIME | 状态确认后录制延迟时间 |
| OUTPUT_FILE_EXT | 输出文件封装方式 |
| OUTPUT_DIR | 输出目录 |
| URL_SELECT | CDN选择 |

## 已知问题
死循环写的，想要退出就`Ctrl+C`就行，或者平常扔screen啥的吧。
还有录制中`Ctrl+C`的话会有进程卡在后台（嗯。。。），自行kill吧Σ( ￣□￣||)，或者等我学到解决办法。。。
代码乱的一笔，小心被恶心到。。。

# DLC AutoSplitVideo
快速分割直播视频用的，非直播视频慎用（IDR区间很短也可以吧。。。）
1小时分割一个，末尾的一个分段如果小于5分钟不分割（想要其他时间自己去改吧，懒得写参数了orz）
## 依赖
* pymediainfo
* MediaInfo
* ffmpeg
## 使用
`python AutoSplitVideo.py <input>`