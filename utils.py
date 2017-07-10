import json
import time


# 返回当前时间
def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


# 加载配置
def load_config(file="config.json"):
    with open(file, 'r') as config:
        return json.load(config)
