import os
import aubio
import numpy as np

def detect_pitch_and_amplitude(filename):
    # 오디오 파일 열기
    win_s = 4096  # window size
    hop_s = 512   # hop size

    samplerate = 0  # 0 means aubio will use the default sample rate of the file
    s = aubio.source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    # 피치 감지 객체 생성
    pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(0.8)

    # 에너지 감지 객체 생성
    # db_o = aubio.db_spl(samplerate)

    pitches = []
    confidences = []
    amplitudes = []

    # 오디오 파일에서 피치 및 진폭 추출
    total_frames = 0
    while True:
        samples, read = s()
        pitch = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()
        amplitude = 20 * np.log10(np.mean(np.abs(samples) + 1e-6))

        pitches.append(pitch)
        confidences.append(confidence)
        amplitudes.append(amplitude)
        total_frames += read
        if read < hop_s: break

    return pitches, confidences, amplitudes

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리로 이동하여 절대 경로 설정
filename = os.path.join(current_dir, '..', '..', 'media', 'audio', 'C chord.m4a')

# 피치 및 진폭 감지
pitches, confidences, amplitudes = detect_pitch_and_amplitude(filename)

# 결과 출력
# print("Detected pitches:", pitches)
# print("Confidences:", confidences)
print("Amplitudes:", amplitudes)
