__all__ = ('playsound', 'voice_via_baidu', 'voice_via_google', 'music')



import execjs
import hashlib
import os
import requests
import subprocess
import tempfile
import warnings

from fuzzywuzzy import process

from music_dl import config
from music_dl.source import MusicSource

from ..conf import voice_path



config.init()
ms = MusicSource()
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



def playsound(path):
    '''
    TODO:
        Maybe we can consider `playsound.playsound`.
    '''
    warnings.warn('It remains to be improved...', DeprecationWarning, stacklevel=2)
    with tempfile.TemporaryFile('w') as null:
        subprocess.check_call(['mplayer', path], stdout=null, stderr=null)
    # os.system(f'mplayer "{path}" &')


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
        response = requests.get(url, params=params)
        with open(path, 'wb') as f:
            f.write(response.content)
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
        response = requests.get(url, params=params)
        with open(path, 'wb') as f:
            f.write(response.content)
    return path


def music(text):
    '''Download music via `music_dl`.
    '''
    songs = ms.search(text, config.get('source').split(' '))
    name, _ = process.extractOne(text, map(lambda x: x.name, songs))
    for song in songs:
        if song.name == name:
            if not os.path.exists(name):
                song.download()
            return name
