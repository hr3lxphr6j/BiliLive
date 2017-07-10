import requests


class LiveRoom(object):
    def __init__(self, room_id):
        self.room_id = room_id
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'Host': 'api.live.bilibili.com',
            'Origin': 'http://live.bilibili.com',
            'Referer': 'http://live.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36 '
        }
        self.session = requests.session()

    def common_request(self, method, url, params=None, data=None):
        connection = None
        if method == 'GET':
            connection = self.session.get(url, headers=self.headers, params=params)
        if method == 'POST':
            connection = self.session.get(url, headers=self.headers, params=params, data=data)
        return connection

    def get_room_info(self):
        url = 'http://api.live.bilibili.com/live/getInfo'
        return self.common_request('GET', url, {'roomid': self.room_id}).json()['data']

    def get_live_urls(self):
        live_urls = []
        url = 'http://live.bilibili.com/api/playurl'
        durls = self.common_request('GET', url, {
            'cid': self.room_id,
            'otype': 'json',
            'quality': 0,
            'platform': 'web'
        }).json()
        for durl in durls['durl']:
            live_urls.append(durl['url'])
        return live_urls
