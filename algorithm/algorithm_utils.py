# Core Functional Algorithms Used
import asyncio
import wave
from scipy.io import wavfile
import noisereduce as nr
import numpy as np
import pyaudio
import speech_recognition
import speech_recognition as sr
import difflib as dl
import os

from scipy import fftpack
import deepspeech
import win32api

from logger.zw_logger import ZwLogger


class SpeechRecognitionUtil:
    wave_ratio = 0
    model = deepspeech.Model('./deepspeech-0.9.3-models.pbmm')
    engine = "ds"

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = "ds"

    def interpret_from_file(self, path):
        if SpeechRecognitionUtil.engine == "ds":
            fin = wave.open(path, 'rb')
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
            return SpeechRecognitionUtil.model.stt(audio)
        else:
            file = sr.AudioFile(path)
            with file as f:
                audio = self.recognizer.record(f)
            return self.recognizer.recognize_sphinx(audio)

    def interpret_from_microphone_v1(self):
        microphone = sr.Microphone()
        try:
            with microphone as m:
                self.recognizer.adjust_for_ambient_noise(m)
                audio = self.recognizer.listen(m)
            result = self.recognizer.recognize_sphinx(audio)
            ZwLogger().log(ZwLogger.ROLE_ALSR, ZwLogger.LV_INFO, "Interpreted Result:" + str(result))
        except speech_recognition.UnknownValueError:
            ZwLogger().log(ZwLogger.ROLE_ALSR, ZwLogger.LV_WARN, "The engine encountered the unknown value")
            return None
        return result

    def interpret_from_microphone(self, callback_function=None):
        result = ""
        while True:
            microphone = sr.Microphone()
            try:
                self.record_audio("./temp.wav", callback_function)
                result = self.interpret_from_file("./temp.wav")
                ZwLogger().log(ZwLogger.ROLE_ALSR, ZwLogger.LV_INFO, "Interpreted Result:" + str(result))
                if result != "":
                    break
            except speech_recognition.UnknownValueError:
                ZwLogger().log(ZwLogger.ROLE_ALSR, ZwLogger.LV_WARN, "The engine encountered the unknown value")
                continue
        return result

    def interpret_from_microphone_cont(self):
        pass

    def record_audio_b(self):
        microphone = sr.Microphone()
        try:
            with microphone as m:
                self.recognizer.adjust_for_ambient_noise(m)
                audio = self.recognizer.listen(m)
            print(audio)
        except speech_recognition.UnknownValueError:
            ZwLogger().log(ZwLogger.ROLE_ALSR, ZwLogger.LV_WARN, "The engine encountered the unknown value")
            return None
        return None

    def env_noise_record(self, wave_out_path):
        ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Detecting noise")
        chunk = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(rate)
        ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Start to listening the Recorder")
        for i in range(int(rate / chunk)):
            data = stream.read(chunk)
            wf.writeframes(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Noise detection completed")

    def record_audio(self, wave_out_path, callback_function=None):
        async def callback_wrapper(**kwargs):
            await asyncio.sleep(1)
            if callback_function is not None:
                callback_function(**kwargs)

        chunk = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(rate)
        occupied = False
        stopflag = 0
        stopflag2 = 0
        threshold = 7000
        ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Start to listening the Recorder")
        while True:
            data = stream.read(chunk)
            rt_data = np.frombuffer(data, np.dtype('<i2'))
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
            SpeechRecognitionUtil.wave_ratio = sum(fft_data) // len(fft_data)
            if sum(fft_data) // len(fft_data) > threshold:
                stopflag += 1
                if not occupied:
                    ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Start recording. Power gained via FFT:" +
                                   str(sum(fft_data) // len(fft_data)))
                    occupied = True
                    stopflag = 0
                    stopflag2 = 0
            else:
                stopflag2 += 1
                if not occupied:
                    continue
            ons = rate / chunk * 2
            if stopflag2 + stopflag > ons:
                if stopflag2 > ons * 0.8:
                    ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Record completed")
                    break
                else:
                    stopflag2 = 0
                    stopflag = 0

            wf.writeframes(data)
            # ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        rate, data = wavfile.read(wave_out_path)
        _, noise_data = wavfile.read("./noise.wav")
        reduced_noise = nr.reduce_noise(y=data, y_noise=noise_data, sr=rate)
        wavfile.write(wave_out_path, rate, reduced_noise)


class TextUtil:
    def __init__(self):
        pass

    def similarity(self, seq_a, seq_b):
        try:
            return dl.SequenceMatcher(a=seq_a, b=seq_b).quick_ratio()
        except AttributeError:
            ZwLogger().log(ZwLogger.ROLE_ALTX, ZwLogger.LV_WARN, "DiffLib reported an abnormal situation")
            return 0


class ShellUtil:
    @staticmethod
    def execute(path: str):
        ZwLogger().log(ZwLogger.ROLE_ALWIN, ZwLogger.LV_INFO, "Executing "+str(path))
        win32api.ShellExecute(0, 'open', path, '', '', 1)
        # return os.system(path)


class Responder:
    def __init__(self):
        self.text_analyst = TextUtil()
        self.application_map = {
            "open notepad": ["shell", "Notepad"],
            "notepad": ["shell", "Notepad"],
            "write notes": ["shell", "Notepad"],
            "write something": ["shell", "Notepad"],
            "take notes": ["shell", "Notepad"],
            "play music": ["shell", "Music Player"],
            "music": ["shell", "Music Player"],
            "play songs": ["shell", "Music Player"],
            "listen to music": ["shell", "Music Player"],
            "open calculator": ["shell", "Calculator"],
            "watch a movie": ["web_browse", "movie"],
            "movie": ["web_browse", "movie"],
            "watch movies": ["web_browse", "movie"],
            "a movie": ["web_browse", "movie"],
            "roll a dice": ["event", "dice"],
            "play dice": ["event", "dice"],
            "roll the dice": ["event", "dice"],
            "throw the dice": ["event", "dice"],
            "roll dice": ["event", "dice"]
        }

    def waiting_and_respond(self,
                            callback_function: callable = None,
                            is_member_function: bool = False,
                            parent_node: object = None):
        async def callback_wrapper(**kwargs):
            ZwLogger().log(ZwLogger.ROLE_ALRSP, ZwLogger.LV_INFO, "Initiating the callback procedure"
                                                                  " to the event handler")
            await asyncio.sleep(1)
            if callback_function is not None:
                if is_member_function:
                    callback_function(**kwargs)
                else:
                    callback_function(**kwargs)

        sr = SpeechRecognitionUtil()
        tx = TextUtil()
        while True:
            rec = sr.interpret_from_microphone(None)
            action = None
            for key in self.application_map.keys():
                if tx.similarity(key, rec) > 0.8:
                    action = self.application_map[key]
                    break
            asyncio.run(callback_wrapper(initiator="responder", action=action, result=rec))
