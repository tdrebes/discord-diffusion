import io
import os
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from time import sleep
from queue import Queue
import speech_recognition
import torch
import whisper

def main():
    model = whisper.load_model('base')
    record_timeout = 2
    phrase_timeout = 3
    phrase_time = None
    
    last_sample = bytes()
    queue = Queue()
    temp_file = NamedTemporaryFile().name

    recorder = speech_recognition.Recognizer()
    recorder.energy_threshold = 1000
    recorder.dynamic_energy_threshold = False

    source = speech_recognition.Microphone(sample_rate=16000)

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:speech_recognition.AudioData) -> None:
        data = audio.get_raw_data()
        queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Ready.")

    transcription = ['']
    while True:
        try:
            now = datetime.utcnow()
            if not queue.empty():
                phrase_complete = False

                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True

                phrase_time = now

                while not queue.empty():
                    data = queue.get()
                    last_sample += data

                wav_data = io.BytesIO(speech_recognition.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH).get_wav_data())

                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                result = model.transcribe(temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                os.system('cls' if os.name=='nt' else 'clear')
                for line in transcription:
                    print(line)

                print('', end='', flush=True)
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)

if __name__ == "__main__":
    main()
