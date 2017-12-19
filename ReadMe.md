# BiliLive
直播录制工具   
目前支持哔哩哔哩，熊猫TV，火猫直播，战旗TV

![image](https://github.com/hr3lxphr6j/BiliLive/raw/master/screenshot/shot.png)

## 依赖
* python3.x(推荐3.6)
* Requests
* lxml
* ffmpeg

## 使用
`python start.py [config.json]`

## config.json配置说明

目录下的config.json为演示文件，如果不指令路径默认会读取`$HOME/.bililive/config.json`

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

# DLC2 SplitVideo
AutoSplitVideo的替代品,可根据yml配置分段视频
## 依赖
* ffmpeg
* ffprobe
## 使用
`python SplitVideo.py <input.yml>`
## Demo.yml
```yaml
GlobalConfig:
  # 是否限制Part长度
  LimitPartLength: true
  # 每段视频最大长度
  PartTime: '1:00:00'
  # 视频长度对PartTime取余数(最后1Part长度)，如果时长不超过PartTime * GreedyPercentage则不独立分段
  GreedyPercentage: 0.25
  # 是否先重封装为Mp4，提供索引加快分段速度
  RemuxToMp4: false
  # 并行处理数量
  ProcessThread: 4
Projects:
    # 文件所在路径
  - Path: '/Users/chigusa/Movies'
    # 视频文件
    Files:
      - 2017-12-06 18-39-48 【王老菊】开启鸡眼模式.flv
    # 是否重编码(x264 2pass 1750k,aac 128k，可用于b站投稿)
    Rip: true
    Parts:
      # 最后的数字代表以哪段文件为准，从0开始计算，-1代表总时长
      # StartTime若为空或为定义，取上一part的EndTime。若为起始part但未定义，取00:00:00
      # EndTime中使用00:00:00代表到结尾
      - Name: 吃鸡
        StartTime: ['00:00:00',-1]
        EndTime: ['04:05:20',-1]
      - Name: 彩虹六号
        StartTime: ['04:05:20',-1]
        EndTime: ['05:13:40',-1]
      - Name: Slay the Spire
        StartTime: ['05:13:40',-1]
        EndTime: ['00:00:00',-1]
```