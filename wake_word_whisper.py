import speech_recognition as sr
import os
import wave
import pyaudio
import numpy as np
import time
import subprocess
import requests  # Spring Boot API 요청을 위한 라이브러리
import pyttsx3

# 음성 녹음 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_LIMIT = 2  # 침묵 시간이 2초 이상이면 녹음 종료
THRESHOLD = 2000  # 소음 감지 임계값

# Whisper 실행 및 오디오 파일 저장 경로
WHISPER_DIR = "./whisper"  # whisper 폴더에서 실행
AUDIO_FILE = os.path.join(WHISPER_DIR, "my_audio.wav")
TEXT_FILE = os.path.join(WHISPER_DIR, "my_audio.wav.txt")


def detect_wake_word():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 '자비스'를 호출하세요...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="ko-KR")
        print(f"👂 감지된 음성: {text}")

        if "자비스" in text:
            print("✅ 웨이크 워드 감지됨! 녹음 시작...")
            record_audio()
            process_with_whisper()

    except sr.UnknownValueError:
        print("❌ 음성을 인식할 수 없습니다.")
    except sr.RequestError:
        print("❌ Google API 요청 실패")


def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)

    print("🎙 녹음 중... 말하세요!")
    frames = []
    recording = True
    silence_counter = 0

    while recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        if np.max(audio_data) > THRESHOLD:  # 소음 감지
            frames.append(data)
            silence_counter = 0
        elif len(frames) > 0:
            silence_counter += 1
            if silence_counter > (SILENCE_LIMIT * RATE / CHUNK):  # 침묵 감지
                print("🛑 녹음 종료")
                recording = False

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # WAV 파일 저장 (whisper 폴더 내에 저장)
    wf = wave.open(AUDIO_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"✅ {AUDIO_FILE} 파일 저장 완료!")



def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def process_with_whisper():
    print("📝 Whisper 실행 중...")

    whisper_cmd = f"./whisper/build/bin/whisper-cli -m {WHISPER_DIR}/models/ggml-medium.bin -f {AUDIO_FILE} -l ko --output-txt"
    
    # Whisper 실행 (Whisper가 끝날 때까지 대기)
    subprocess.run(whisper_cmd, shell=True, check=True)

    # Whisper 변환이 완료될 때까지 대기
    while not os.path.exists(TEXT_FILE):
        print("⏳ Whisper 변환 대기 중...")
        time.sleep(0.5)

    # 변환된 텍스트 읽기
    with open(TEXT_FILE, "r") as file:
        user_input = file.read().strip()

    print(f"📨 Whisper 변환 결과: {user_input}")

    # Spring Boot API로 텍스트 전송
    api_url = "http://localhost:8080/api/process-text"
    response = requests.post(api_url, json={"text": user_input})

    if response.status_code == 200:
        ai_response = response.text
        print(f"🤖 AI 응답: {ai_response}")
        text_to_speech(ai_response)

        # # AI 응답을 TTS 변환 후 음성 출력
        # os.system(f'tts --text "{ai_response}" --out_path whisper/output.wav')
        # os.system("afplay whisper/output.wav")  # Mac에서 음성 출력
    else:
        print(f"❌ API 요청 실패: {response.status_code}")


if __name__ == "__main__":
    while True:
        detect_wake_word()  # "자비스" 감지 대기


# import speech_recognition as sr
# import os
# import wave
# import pyaudio
# import numpy as np
# import time
# import subprocess

# # 음성 녹음 설정
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# CHUNK = 1024
# SILENCE_LIMIT = 2  # 침묵 시간이 2초 이상이면 녹음 종료
# THRESHOLD = 2000  # 소음 감지 임계값

# # Whisper 실행 및 오디오 파일 저장 경로
# WHISPER_DIR = "./whisper"  # whisper 폴더에서 실행
# AUDIO_FILE = os.path.join(WHISPER_DIR, "my_audio.wav")
# TEXT_FILE = os.path.join(WHISPER_DIR, "my_audio.wav.txt")


# def detect_wake_word():
#     recognizer = sr.Recognizer()
#     mic = sr.Microphone()

#     with mic as source:
#         print("🎤 '자비스'를 호출하세요...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         text = recognizer.recognize_google(audio, language="ko-KR")
#         print(f"👂 감지된 음성: {text}")

#         if "자비스" in text:
#             print("✅ 웨이크 워드 감지됨! 녹음 시작...")
#             record_audio()
#             process_with_whisper()

#     except sr.UnknownValueError:
#         print("❌ 음성을 인식할 수 없습니다.")
#     except sr.RequestError:
#         print("❌ Google API 요청 실패")


# def record_audio():
#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
#                         input=True, frames_per_buffer=CHUNK)

#     print("🎙 녹음 중... 말하세요!")
#     frames = []
#     recording = True
#     silence_counter = 0

#     while recording:
#         data = stream.read(CHUNK, exception_on_overflow=False)
#         audio_data = np.frombuffer(data, dtype=np.int16)

#         if np.max(audio_data) > THRESHOLD:  # 소음 감지
#             frames.append(data)
#             silence_counter = 0
#         elif len(frames) > 0:
#             silence_counter += 1
#             if silence_counter > (SILENCE_LIMIT * RATE / CHUNK):  # 침묵 감지
#                 print("🛑 녹음 종료")
#                 recording = False

#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     # WAV 파일 저장 (whisper 폴더 내에 저장)
#     wf = wave.open(AUDIO_FILE, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(audio.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()

#     print(f"✅ {AUDIO_FILE} 파일 저장 완료!")


# def process_with_whisper():
#     print("📝 Whisper 실행 중...")

#     # Whisper 실행 (whisper 폴더 내에서 실행)
#     whisper_cmd = f"./whisper/build/bin/whisper-cli -m {WHISPER_DIR}/models/ggml-medium.bin -f {AUDIO_FILE} -l ko --output-txt"
    
#     # subprocess.run을 사용하여 Whisper 실행이 끝날 때까지 대기
#     subprocess.run(whisper_cmd, shell=True, check=True)

#     # Whisper 변환이 완료될 때까지 파일이 생성될 때까지 기다림
#     while not os.path.exists(TEXT_FILE):
#         print("⏳ Whisper 변환 대기 중...")
#         time.sleep(0.5)  # 0.5초 대기 후 다시 확인

#     # 변환된 텍스트 읽기
#     with open(TEXT_FILE, "r") as file:
#         user_input = file.read().strip()

#     print(f"📨 Whisper 변환 결과: {user_input}")


# if __name__ == "__main__":
#     while True:
#         detect_wake_word()  # "자비스" 감지 대기

