from .BaseLive import BaseLive


class BiliBiliLive(BaseLive):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id
        self.site_name = 'BiliBili'
        self.site_domain = 'live.bilibili.com'

    def get_room_info(self):
        url = 'http://api.live.bilibili.com/live/getInfo'
        response = self.common_request('GET', url, {'roomid': self.room_id}).json()
        if response['msg'] == 'OK':
            return {
                'hostname': response['data']['ANCHOR_NICK_NAME'],
                'roomname': response['data']['ROOMTITLE'],
                'site_name': self.site_name,
                'site_domain': self.site_domain,
                'status': True if response['data']['_status'] == 'on' else False
            }

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
