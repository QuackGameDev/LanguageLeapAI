﻿import wave
from os import getenv
from pathlib import Path
from time import sleep

import deepl
import googletrans
import keyboard
import pyaudio
import requests
from dotenv import load_dotenv

from modules.asr import speech_to_text
from modules.tts import speak

# 英語→カタカナ変換機(https://www.sljfaq.org/cgi/e2k_ja.cgi)からスクレイピング
import urllib
from bs4 import BeautifulSoup

load_dotenv()

TARGET_LANGUAGE = getenv('TARGET_LANGUAGE_CODE')
MIC_ID = int(getenv('MICROPHONE_ID'))
RECORD_KEY = getenv('MIC_RECORD_KEY')
LOGGING = getenv('LOGGING', 'False').lower() in ('true', '1', 't')
MIC_AUDIO_PATH = Path(__file__).resolve().parent / r'audio/mic.wav'
CHUNK = 1024
FORMAT = pyaudio.paInt16


def replaceSpaces(string):
    return string.replace(" ", "+")

def english_to_katakana(word, question):
    url = 'https://www.sljfaq.org/cgi/e2k_ja.cgi'
    url_q = url + '?word=' + replaceSpaces(word)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    request = urllib.request.Request(url_q, headers=headers)
    html = urllib.request.urlopen(request)
    soup = BeautifulSoup(html, 'html.parser')
    katakana_string = soup.find_all(class_='katakana-string')[0].string.replace('\ ', '').replace('・', '')
    if question:
        katakana_string = katakana_string + '?'
    return katakana_string

def on_press_key(_):
    global frames, recording, stream
    if not recording:
        frames = []
        recording = True
        stream = p.open(format=FORMAT,
                        channels=MIC_CHANNELS,
                        rate=MIC_SAMPLING_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=MIC_ID)


def on_release_key(_):
    global recording, stream
    recording = False
    stream.stop_stream()
    stream.close()
    stream = None

    # if empty audio file
    if not frames:
        print('No audio file to transcribe detected.')
        return

    # write microphone audio to file
    wf = wave.open(str(MIC_AUDIO_PATH), 'wb')
    wf.setnchannels(MIC_CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(MIC_SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # transcribe audio
    try:
        eng_speech = speech_to_text(MIC_AUDIO_PATH, 'transcribe', 'en')
    except requests.exceptions.JSONDecodeError:
        print('Too many requests to process at once')
        return

    question = False

    if eng_speech:
        if '?' in eng_speech:
            question = True
        translated_speech = english_to_katakana(eng_speech, question)


        if LOGGING:
            print(f'English: {eng_speech}')
            print(f'Translated: {translated_speech}')

        speak(translated_speech, TARGET_LANGUAGE)

    else:
        print('No speech detected.')


if __name__ == '__main__':
    p = pyaudio.PyAudio()

    # get channels and sampling rate of mic
    mic_info = p.get_device_info_by_index(MIC_ID)
    MIC_CHANNELS = mic_info['maxInputChannels']
    MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])

    frames = []
    recording = False
    stream = None

    keyboard.on_press_key(RECORD_KEY, on_press_key)
    keyboard.on_release_key(RECORD_KEY, on_release_key)

    try:
        try:
            while True:
                if recording and stream:
                    data = stream.read(CHUNK)
                    frames.append(data)
                else:
                    sleep(0.5)
        except:
            print("crashed for some reason")
    except KeyboardInterrupt:
        print('Closing voice translator.')
