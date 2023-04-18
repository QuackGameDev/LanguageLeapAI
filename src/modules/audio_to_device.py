from os import getenv
from pathlib import Path

import keyboard
import mouse
import sounddevice as sd
import soundfile as sf

TTS_WAV_PATH = Path(__file__).resolve().parent.parent / r'audio\tts.wav'
INGAME_PUSH_TO_TALK_KEY = getenv('INGAME_PUSH_TO_TALK_KEY')
mouseButton = getenv('PUSH_MOUSE')

def play_voice(device_id):
    data, fs = sf.read(TTS_WAV_PATH, dtype='float32')

    if INGAME_PUSH_TO_TALK_KEY:
        if mouseButton:
            mouse.press(INGAME_PUSH_TO_TALK_KEY)
        else:
            keyboard.press(INGAME_PUSH_TO_TALK_KEY)

    sd.play(data, fs, device=device_id)
    sd.wait()

    if INGAME_PUSH_TO_TALK_KEY:
        if mouseButton:
            mouse.release(INGAME_PUSH_TO_TALK_KEY)
        else:
            keyboard.release(INGAME_PUSH_TO_TALK_KEY)
