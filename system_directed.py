import io
import os
import pyaudio
import wave
import pyttsx
import json

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
    
def pc_speak(output):
    print("speaking: ", output)
    engine = pyttsx.init()
    engine.say(output)
    engine.runAndWait()

def record_user(filename):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def transcribe_audio(filename):
    """
    Code used from Google Cloud Speech API Client Libraries documentation
    """
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = os.path.join(os.path.dirname(__file__), filename)

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    for result in response.results:
        print(result)
        return result.alternatives[0].transcript


def main():
    fn = 'output.wav'

    data = {
        'Temperature': '',
        'Blood pressure': '',
        'Pulse': '',
        'Pain level': ''
    }

    for key, _ in data.items():
        pc_speak("What is your {}".format(key))
        record_user(fn)
        value = transcribe_audio(fn)
        data[key] = value
        pc_speak("Okay, You said your {} is {}".format(key, value))

    print(data)
    with open('user_data', 'w') as pd_f:
        pd_f.write(json.dumps(data))

if __name__ == "__main__":
    main()