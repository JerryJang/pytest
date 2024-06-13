import asyncio
import websockets
import numpy as np
import librosa
import sounddevice as sd
import tensorflow as tf
import magenta.music as mm
from magenta.models.onsets_frames_transcription import configs
from magenta.models.onsets_frames_transcription import infer
from magenta.models.onsets_frames_transcription import train_util

# 모델 설정
checkpoint_dir = '/Users/jangsiyoung/Desktop/pytest/testproject/blog/onsets_frames_transcriptions'  # 실제 모델 체크포인트 경로로 변경

hparams = configs.CONFIG_MAP['onsets_frames'].hparams
hparams.use_cudnn = False

# 인퍼런스 함수 설정
def transcribe(model, audio):
    frames, onsets, _, _ = model.transcribe(audio)
    # 주파수를 추출
    pitches, magnitudes = librosa.core.piptrack(y=audio, sr=44100)
    detected_frequencies = []
    for t in range(pitches.shape[1]):
        if onsets[t]:
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            detected_frequencies.append(pitch)
    return frames, onsets, detected_frequencies

# 모델 로드
model = infer.InferenceModel(
    hparams,
    checkpoint_dir,
    note_sequence_converter=train_util.melody_converter(hparams)
)

# 피아노 소리 인식을 위한 임계값 설정
AMPLITUDE_THRESHOLD = 0.01

def is_significant_sound(y, sr):
    energy = np.sum(y ** 2) / len(y)
    return energy > AMPLITUDE_THRESHOLD

def frequency_to_note_name(frequency):
    return librosa.hz_to_note(frequency)

async def audio_stream_handler(websocket, path):
    audio_buffer = np.array([], dtype=np.float32)
    while True:
        async for message in websocket:
            audio_chunk = np.frombuffer(message, dtype=np.float32)
            audio_buffer = np.append(audio_buffer, audio_chunk)
            if len(audio_buffer) >= 44100:  # 1초 단위로 처리
                y = audio_buffer[:44100]
                audio_buffer = audio_buffer[44100:]
                sr = 44100
                if is_significant_sound(y, sr):
                    frames, onsets, frequencies = transcribe(model, y)
                    notes = [frequency_to_note_name(freq) for freq in frequencies if freq > 0]
                    if notes:
                        result = ', '.join(notes)
                        await websocket.send(result)

async def start_server():
    server = await websockets.serve(audio_stream_handler, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    asyncio.get_event_loop().run_forever()
