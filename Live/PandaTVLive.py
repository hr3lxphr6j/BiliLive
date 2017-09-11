from .BaseLive import BaseLive


class PandaTVLive(BaseLive):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id
        self.site_name = 'Panda'
        self.site_domain = 'www.panda.tv'

    def get_room_info(self):
        url = 'https://room.api.m.panda.tv/index.php'
        response = self.common_request('GET', url, {
            'method': 'room.shareapi',
            'roomid': self.room_id
        }).json()
        if response['errno'] == '0':
            return {
                'hostname': response['data']['hostinfo']['name'],
                'roomname': response['data']['roominfo']['name'],
                'site_name': self.site_name,
                'site_domain': self.site_domain,
                'status': True if response['data']['roominfo']['status'] == '2' else False
            }

    def get_live_urls(self):
        url = 'https://room.api.m.panda.tv/index.php'
        response = self.common_request('GET', url, {
            'method': 'room.shareapi',
            'roomid': self.room_id
        }).json()
        if response['errno'] == '0' and response['data']['roominfo']['status'] == '2':
            m3u8 = response['data']['videoinfo']['address']
            return [m3u8.replace('_small', '') if '_small' in m3u8 else m3u8]
        pass
