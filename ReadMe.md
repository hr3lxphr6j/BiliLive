# 依赖
* requests
* ffmpeg

# 使用
`python start.py`

# config.json配置说明

| 属性 | 说明 |
| :----: | :----:|
| ROOM_IDS | 房间ID |
| POLLING_INTERVAL | 状态查询间隔 |
| LAZY_TIME | 状态确认后录制延迟时间 |
| OUTPUT_FILE_EXT | 输出文件封装方式 |
| OUTPUT_DIR | 输出目录 |
| URL_SELECT | CDN选择 |
| CYCLE | 录制结束后是否继续 |