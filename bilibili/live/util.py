__all__ = ('send', )


import time

from ..util.session import session


class send:
    @classmethod
    def danmaku(cls, text, room_id, color=16777215, fontsize=25, mode=1, limit=20, scale=0.1):
        '''发送弹幕

        Argument:
            - text: str
            - room_id: int
            - color: int, default is 16777215
            - fontsize: int, default is 25
            - mode: int, default is 1
            - limit: int, text length limit
            - scale: float, send text interval
        '''
        if len(text) > limit:
            flag = send.danmaku(text[:limit], room_id, color, fontsize, mode, limit, scale)
            if not flag:
                return False
            time.sleep(scale*max(limit, len(text)-limit))
            return send.danmaku(text[limit:], room_id, color, fontsize, mode, limit, scale)
        url = 'https://api.live.bilibili.com/msg/send'
        data = dict(
            msg=text, roomid=room_id,
            color=color, fontsize=fontsize, mode=mode, rnd=int(time.time()),
        )
        return cls._post(url, data).json()['code'] == 0

    @classmethod
    def bag_gift(cls, from_uid, to_uid, room_id, gift_number=1, gift_id=1):
        '''发送背包礼物（暂定辣条）

        Argument:
            - from_uid: int, gift from user id
            - to_uid: int, gift to user id
            - room_id: int
            - gift_number: int
            - gift_id: int, 1 for 辣条

        TODO:
            - 简化参数
        '''
        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        data = dict(
            uid=from_uid, gift_id=gift_id, ruid=to_uid, biz_id=room_id,
            rnd=int(time.time()), price=0, gift_num=None, bag_id=None,
        )
        bags = cls._bags(gift_id)
        if gift_number > sum(bags.values()):
            return False
        for bag_id, number in bags.items():
            data['bag_id'] = bag_id
            data['gift_num'] = gift_number if gift_number<=number else number
            if cls._post(url, data).json()['code'] != 0:
                return False
            if gift_number <= number:
                break
            gift_number -= number
        return True

    @classmethod
    def _bags(cls, gift_id=None):
        # {bag_id: gift_num}
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list'
        cookies = dict(SESSDATA=session.session.cookies['SESSDATA'])
        headers = dict(Referer='https://live.bilibili.com/')
        data = session.requests.get(url, headers=headers, cookies=cookies).json()
        return {
            item['bag_id']: item['gift_num']
            for item in sorted(data['data']['list'], key=lambda x: x['expire_at'])
            if gift_id is None or item['gift_id']==gift_id
        }

    @classmethod
    def _post(cls, url, data):
        data['csrf_token'] = data['csrf'] = session.session.cookies['bili_jct']
        cookies = dict(
            SESSDATA=session.session.cookies['SESSDATA'],
            bili_jct=session.session.cookies['bili_jct'],
        )
        headers = dict(Referer='https://live.bilibili.com/')
        response = session.requests.post(url, data=data, headers=headers, cookies=cookies)
        return response
