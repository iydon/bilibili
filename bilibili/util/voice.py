__all__ = ('playsound', 'voice_via_baidu', 'voice_via_google', 'music')



import execjs
import hashlib
import json
import music_dl
import os
import requests

music_dl.config.init()

from music_dl.addons.netease import netease_search
from pydub import AudioSegment, playback
from you_get.extractors.netease import netease_download

from ..conf import music_path, voice_path



ctx = execjs.compile('''
    function TL(a) {
        var k = "";
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };

    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
''')



def playsound(path, format=None):
    '''
    Argument:
        path: str
    '''
    song = AudioSegment.from_file(path, format=None)
    playback.play(song)


def voice_via_bing(text, lan='zh-CN', spd=3, gender='Female', dirname=voice_path):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = hashlib.md5(f'{text}-{lan}-{spd}'.encode()).hexdigest()
    path = os.path.join(dirname, f'{filename}.mp3')
    if not os.path.exists(path):
        url = 'https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1?'
        data = f'''<?xml version='1.0' encoding='utf-8'?>
            <speak version='1.0' xml:lang='{lan}'>
                <voice xml:lang='{lan}' xml:gender='{gender}' name='{lan}-HuihuiRUS'>
                    <prosody rate='-20.00%'>{text}</prosody>
                </voice>
            </speak>'''
        headers = {'Content-Type': 'application/ssml+xml'}
        raise NotImplementedError
    return path


def voice_via_baidu(text, lan='zh', spd=3, dirname=voice_path):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = hashlib.md5(f'{text}-{lan}-{spd}'.encode()).hexdigest()
    path = os.path.join(dirname, f'{filename}.mp3')
    if not os.path.exists(path):
        url = 'https://fanyi.baidu.com/gettts'
        params = dict(text=text, lan=lan, spd=spd)
        content = requests.get(url, params=params).content
        if content:
            with open(path, 'wb') as f:
                f.write(content)
    return path


def voice_via_google(text, lan='zh', spd=0.5, dirname=voice_path):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = hashlib.md5(f'{text}-{lan}-{spd}'.encode()).hexdigest()
    path = os.path.join(dirname, f'{filename}.mp3')
    if not os.path.exists(path):
        url = 'https://translate.google.cn/translate_tts'
        params = dict(
            ie='UTF-8', q=text, tl=lan, total=1, idx=0, textlen=len(text),
            tk=ctx.call('TL', text), client='webapp', prev='input', ttsspeed=spd,
        )
        content = requests.get(url, params=params).content
        if content:
            with open(path, 'wb') as f:
                f.write(content)
    return path


class music:
    '''Download music via qq and netease
    '''
    @classmethod
    def qq(cls, text, dirname=music_path):
        songs = requests.get(
            'https://c.y.qq.com/soso/fcgi-bin/client_search_cp',
            headers=dict(referer='https://y.qq.com/portal/search.html'),
            params=dict(w=text, format='json')
        ).json()
        for song in songs['data']['song']['list']:
            data = json.loads(json.loads(
                requests.post(
                    'http://www.douqq.com/qqmusic/qqapi.php',
                    data=dict(mid=song['media_mid'])
                ).text
            ))
            if data['m4a']:
                authors = '-'.join(s['name'] for s in song['singer'])
                path = os.path.join(dirname, f'{song["songname"]}-{authors}.m4a')
                if not os.path.exists(path):
                    with open(path, 'wb') as f:
                        f.write(requests.get(data['m4a']).content)
                return path
        return ''

    @classmethod
    def netease(cls, text, dirname=music_path):
        id = netease_search(text)[0].id
        files = set(os.listdir(dirname))
        netease_download(f'https://music.163.com/#/song?id={id}', dirname)
        for file in set(os.listdir(dirname)).difference(files):
            return os.path.join(dirname, file)
        return ''
