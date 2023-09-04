#!/usr/bin/env python3

import json
import ssl
import sys
import os
import concurrent.futures
import asyncio
import base64
import num_to_int
import json
from flask import jsonify, Response
from urllib.request import urlopen
from urllib import request as rqst, parse
import urllib.error

from pathlib import Path
from vosk import KaldiRecognizer, Model
from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable
from aiortc import RTCSessionDescription, RTCPeerConnection
from av.audio.resampler import AudioResampler


ROOT = Path(__file__).parent

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '192.168.10.82')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 5025))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')
# vosk_cert_file = os.environ.get('VOSK_CERT_FILE', '/usr/local/apache2/conf/ssl_crt/server.crt')
# vosk_key_file = os.environ.get('VOSK_KEY_FILE', '/usr/local/apache2/conf/ssl_crt/server.key')
vosk_cert_file = os.environ.get('VOSK_CERT_FILE', None)
vosk_key_file = os.environ.get('VOSK_KEY_FILE', None)
vosk_dump_file = os.environ.get('VOSK_DUMP_FILE', None)

# vosk_model_path = "/home/oldhdd/vosk-server/webrtc/model"
vosk_model_path = "/home/ehz/vosk-server/webrtc/model"
model = Model(vosk_model_path)
pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
dump_fd = None if vosk_dump_file is None else open(vosk_dump_file, "wb")
PREV_TEXT = ""

def process_chunk(rec, message):
    try:
        res = rec.AcceptWaveform(message)
    except Exception:
        result = None
    else:
        if res > 0:
            result = rec.Result()
        else:
            result = rec.PartialResult()
    return result


def getNumber(string):  # get number from workds "জিরো ওয়ান সেভেন ফোর ফোর" = '01744'

    number = [
        "জিরো",
        "ওয়ান",
        "টু",
        "থ্রি",
        "ফোর",
        "ফাইভ",
        "সিক্স",
        "সেভেন",
        "এইট",
        "নাইন",
    ]
    st = string.split(" ")
    wr = ""

    for i, w in enumerate(st):
        for j, n in enumerate(number):
            if w == n:
                if st[i - 1] == "ডাবল" or st[i - 1] == "ডবল":
                    wr = wr + str(j)
                if st[i - 1] == "ট্রিপল":
                    wr = wr + str(j) + str(j)
                wr = wr + str(j)

    print(wr)
    if len(wr) > 1:
        return wr
    else:
        return string


class KaldiTask:
    def __init__(self, user_connection):
        self.__resampler = AudioResampler(format='s16', layout='mono', rate=48000)
        self.__pc = user_connection
        self.__audio_task = None
        self.__track = None
        self.__channel = None
        self.__recognizer = KaldiRecognizer(model, 48000)


    async def set_audio_track(self, track):
        self.__track = track

    async def set_text_channel(self, channel):
        self.__channel = channel

    async def start(self):
        self.__audio_task = asyncio.create_task(self.__run_audio_xfer())

    async def stop(self):
        if self.__audio_task is not None:
            self.__audio_task.cancel()
            self.__audio_task = None

    async def __run_audio_xfer(self):
        loop = asyncio.get_running_loop()

        max_frames = 20
        frames = []
        while True:
            fr = await self.__track.recv()
            frames.append(fr)

            # We need to collect frames so we don't send partial results too often
            if len(frames) < max_frames:
               continue

            dataframes = bytearray(b'')
            for fr in frames:
                for rfr in self.__resampler.resample(fr):
                    dataframes += bytes(rfr.planes[0])[:rfr.samples * 2]
            frames.clear()

            if dump_fd != None:
                dump_fd.write(bytes(dataframes))

            result = await loop.run_in_executor(pool, process_chunk, self.__recognizer, bytes(dataframes))
            print(result)
            self.__channel.send(result)

async def index(request):
    content = open(str(ROOT / 'static' / 'index.html')).read()
    return web.Response(content_type='text/html', text=content)


async def message(request):
    output = request.rel_url.query['output']
    sender = request.rel_url.query['sender']
    original_output = output
    global PREV_TEXT
    if "আপনি কোন প্যাকটি নিতে চাচ্ছেন?" in PREV_TEXT:
        t1 = output.split(" ")
        lst = []
        pkg_dict = {}
        for c, i in enumerate(t1):
            if i == "টাকায়" or i == "টাকা" or i == "টাকারটা" or i == "টাকার":
                lst.append(c)
                pkg_dict[c] = i
            if i == "জিবি" or i == "জিবিরটা" or i == "জিপি" or i == "জিবির":
                lst.append(c)
                pkg_dict[c] = i
            if i == "মিনিটেরটা" or i == "মিনিট":
                lst.append(c)
                pkg_dict[c] = i

        print(lst)
        st = "PKG_"
        for c, i in enumerate(lst):
            if c == 0:
                st += str(num_to_int.spell_to_int(" ".join(t1[:lst[c]])))+"_"+ t1[lst[c]] 
                continue
            st+="_"
            st += str(num_to_int.spell_to_int(" ".join(t1[lst[c-1]+1:lst[c]])))+ "_" + t1[lst[c]]
            
        output = st

    if output == "PKG_":
        output = original_output

    if PREV_TEXT=="স্যার, কত টাকার মধ্যে নিতে চাচ্ছিলেন?":
        output = getNumber(output)
        output = num_to_int.spell_to_int(output)

    print(f"Sending data: ", output)
    sender_data = '{"sender":"'+sender+'","message":"'+output+'","cli": "12346798","metadata":"bn","ivrStatus":""}'
    
    post_data = sender_data.encode('utf-8')
    # print(post_data)
    req = rqst.Request("http://192.168.10.44:5004/webhooks/rest/webhook", data=post_data)
    post_resp = rqst.urlopen(req)
    ai_resp = json.loads(post_resp.read())
    #for tts request
    bot_response=''
    if(len(ai_resp)>0):
        bot_response=ai_resp[0]["text"]
    
    bot_resp = bot_response
    print(bot_response)
    PREV_TEXT = bot_response
    br = urllib.parse.quote(bot_response)
    #url="http://192.168.10.42:5002/api/tts?text="+str(br)+"&speaker_id=Rothi&style_wav=&language_id="
    url="http://192.168.10.39:7070/api/tts?text="+str(br)+"&speaker_id=Rothi&style_wav=&language_id="
    req = rqst.Request(url)
    post_resp = rqst.urlopen(req)
    audio_data = post_resp.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    dat = [{"bt": bot_response, "audio": audio_base64}]
    return web.json_response(dat)


async def offer(request):

    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])

    pc = RTCPeerConnection()

    kaldi = KaldiTask(pc)

    @pc.on('datachannel')
    async def on_datachannel(channel):      
        channel.send('{}') # Dummy message to make the UI change to "Listening"
        await kaldi.set_text_channel(channel)
        await kaldi.start()

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()

    @pc.on('track')
    async def on_track(track):
        if track.kind == 'audio':
            await kaldi.set_audio_track(track)

        @track.on('ended')
        async def on_ended():
            await kaldi.stop()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))


if __name__ == '__main__':

    if vosk_cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(vosk_cert_file, vosk_key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.router.add_post('/offer', offer)

    app.router.add_get('/', index)
    app.router.add_get('/message', message)
    app.router.add_static('/static/', path=ROOT / 'static', name='static')

    #web.run_app(app, port=vosk_port, host="192.168.10.77", ssl_context=ssl_context)
    #web.run_app(app, port=vosk_port, host="noctest.gplex.net", ssl_context=ssl_context)
    web.run_app(app, port=vosk_port, ssl_context=ssl_context)
