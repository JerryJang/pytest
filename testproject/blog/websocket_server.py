import asyncio
import websockets
import numpy as np
import struct
import io
import math
from scipy.signal import butter, lfilter
import aubio

async def detect_pitch_and_amplitude(samples, samplerate):
    print("피치 함수에 진입")

    # 피치 감지 객체 생성
    win_s = 4096  # window size
    hop_s = 512  # hop size

    pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(0.8)

    amplitudes = []

    # 피치 및 진폭 추출
    total_frames = len(samples)
    for i in range(0, total_frames, hop_s):
        frame = samples[i:i + hop_s]
        if len(frame) < hop_s:
            break
        pitch = pitch_o(frame)[0]
        confidence = pitch_o.get_confidence()
        amplitude = np.sqrt(np.mean(frame ** 2))

        # 진폭 값을 조정하여 데시벨 값이 양수가 되도록 함
        amplitude_db = amplitude * 1000  # 진폭 값을 1000배로 키움
        db = 20 * np.log10(amplitude_db) if amplitude_db > 0 else -100.0  # 데시벨로 변환
        print(f"~~~~~~ amplitude_DB: {amplitude_db}, amplitude: {amplitude}, db: {db}")
        amplitudes.append(db)

    print(f"amplitudes that gain from about: {amplitudes}")
    return amplitudes

async def note_detect(samples ,samplerate):
    print("note_detect function called")  # 디버그 출력

    sound = samples.astype(np.float32)
    # sound = samples.astype(np.float32) / 32768.0  # Scale to range -1 to 1
    print(f"Sound data after scaling: {sound[:10]}")  # 디버그 출력

    # Apply moving average filter to smooth the signal
    # window_size = 5
    # sound = np.convolve(sound, np.ones(window_size) / window_size, mode='valid')

   # sound = np.divide(sound, float(2 ** 15))
    # Apply a band-pass filter to isolate piano frequencies (27.5 Hz to 4186 Hz)
    # freq_low = 27.5
    # freq_high = 4186.0
    # nyquist = 0.5 * samplerate
    # low = freq_low / nyquist
    # high = freq_high / nyquist

    # def butter_bandpass(lowcut, highcut, fs, order=5):
    #     b, a = butter(order, [lowcut, highcut], btype='band')
    #     return b, a

    # def bandpass_filter(data, lowcut, highcut, fs, order=5):
    #     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    #     y = lfilter(b, a, data)
    #     return y
    #
    # sound = bandpass_filter(sound, low, high, samplerate, order=6)

    fourier = np.fft.fft(sound)
    fourier = np.absolute(fourier)
    imax = np.argmax(fourier)

    print(f"Fourier data: {fourier[:10]}")  # 디버그 출력
    print(f"Fourier dataII: {len(fourier)}")
    print(f"imax: {imax}")  # 디버그 출력

    i_begin = -1
    threshold = 0.35 * fourier[imax]
    for i in range(0, imax + 100):
        if fourier[i] >= threshold:
            if i_begin == -1:
                i_begin = i
        if i_begin != -1 and fourier[i] < threshold:
            break
    i_end = i
    imax = np.argmax(fourier[0:i_end + 100])
    print(f"imaxII: {imax}")

    freq = (imax * samplerate) / len(samples)
    print("suisou"+str(len(sound)))
    print("샘플수 + "+str(len(samples)))
    # Frequency range for piano notes (27.5 Hz to 4186 Hz)
    if freq < 27.5 or freq > 4186.0:
        return None, 0

    note = 0
    name = np.array(
        ["C0","C0","C0","C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
         "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
         "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G2#", "A2", "A2#", "B2",
         "C3", "C3#", "D3", "D3#", "E3", "F3", "F3#", "G3", "G3#", "A3", "A3#", "B3",
         "C4", "C4#", "D4", "D4#", "E4", "F4", "F4#", "G4", "G4#", "A4", "A4#", "B4",
         "C5", "C5#", "D5", "D5#", "E5", "F5", "F5#", "G5", "G5#", "A5", "A5#", "B5",
         "C6", "C6#", "D6", "D6#", "E6", "F6", "F6#", "G6", "G6#", "A6", "A6#", "B6",
         "C7", "C7#", "D7", "D7#", "E7", "F7", "F7#", "G7", "G7#", "A7", "A7#", "B7",
         "C8", "C8#", "D8", "D8#", "E8", "F8", "F8#", "G8", "G8#", "A8", ])
    #"A8#", "B8", "Beyond B8"

    frequencies = np.array(

        [27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91,
         55.00, 58.27, 61.74, 65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00, 103.83,
         110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65,
         220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30,
         440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61,
         880.00, 932.33, 987.77, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22,
         1760.00, 1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96,
         3322.44, 3520.00, 3729.31, 3951.07, 4186.01])

    print(f"***************** freq : {freq}\n")
    for i in range(0, frequencies.size - 1):
        if freq < frequencies[0]:
            note = name[0]
            break
        if freq > frequencies[-1]:
            note = name[-1]
            break
        if frequencies[i] <= freq < frequencies[i + 1]:
            if freq - frequencies[i] < (frequencies[i + 1] - frequencies[i]) / 2:
                note = name[i]
            else:
                note = name[i + 1]
            break
    print("aka"+note)

    amplitude = np.max(sound)
    return note, amplitude


async def recognize_notes(websocket, path):
    buffer = np.array([], dtype=np.float32)
    samplerate = 22050  # 또는 44100, 오디오의 샘플레이트

    async for message in websocket:
        try:
            audio_chunk = np.frombuffer(message, dtype=np.float32)
            buffer = np.append(buffer, audio_chunk)

            if len(buffer) >= samplerate:
                audio_data = buffer[:samplerate]
                buffer = buffer[samplerate:]

                amplitudes = await detect_pitch_and_amplitude(audio_data, samplerate)
                note, amplitude = await note_detect(audio_data, samplerate)

                if note and int(amplitudes[0]) > 7.0:
                    result = f"{note}"
                else:
                    result = ""

                await websocket.send(result)
        except Exception as e:
            print(f"Error processing audio data: {e}")
            await websocket.send(f"Error: {str(e)}")

start_server = websockets.serve(recognize_notes, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


# async def recognize_notes(websocket, path):
#     async for message in websocket:
#         try:
#             audio_data = np.frombuffer(message, dtype=np.float32)
#             samplerate = 22050
#             amplitudes = await detect_pitch_and_amplitude(audio_data, samplerate)
#             note, amplitude = await note_detect(audio_data, samplerate)
#
#             if note and int(amplitudes[0])>6.0:
#                 result = f"{note}"
#             else:
#                 result = ""
#
#             await websocket.send(result)
#         except Exception as e:
#             print(f"Error processing audio data: {e}")
#             await websocket.send(f"Error: {str(e)}")

# start_server = websockets.serve(recognize_notes, "localhost", 5000)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
