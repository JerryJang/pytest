import pyaudio
import wave
import numpy as np
import struct
import os
import math
import matplotlib.pyplot as plt

# This program recognize note every 0.25s (4 notes/sec)
FRAME_PACKET = 22050  # 1024 # notes /s ### 22050 = 2 fois /min
CHANNELS = 1  # 1=mono
FORMAT = pyaudio.paInt16
RATE = 88200  # Number of samples per second (44100 usualy)
RECORD_SECONDS = 5  # Duration of the audio record

def amplitude_to_db(amplitude):
    return 20 * math.log10(amplitude)


# Create a fold to save the images if doesn't exist already
output_dir = "output_images"
os.makedirs(output_dir, exist_ok=True)

# Variable to count the number of graphics
plot_count = 0


# This function detects the note the most present in N packets of frames
def note_detect(paquet_frame, nb_frame, f_s, plot_count):
    sound = np.zeros(nb_frame)  # blank array of nb_frame size

    for i in range(nb_frame):
        wdata = paquet_frame[i]  # get a frame
        data = struct.unpack("<h", wdata)  # decompress the audio part
        sound[i] = int(data[0])  # put the value of the audio frame into the array sound[]

    # plt.plot(sound)
    # plt.savefig(os.path.join(output_dir, f"sound_plot_{plot_count}.png"))

    sound = np.divide(sound, float(2 ** 15))  # scaling the value to 0 - 1
    # —————————————————————

    # plt.plot(sound)
    # plt.show()

    # fourier transformation from numpy module
    fourier = np.fft.fft(sound)  # get the frequencies thanks to the fft
    fourier = np.absolute(fourier)
    imax = np.argmax(fourier[0:int(nb_frame / 2)])  # index of the element with the biggest frequency

    # peak detection
    i_begin = -1
    threshold = 0.3 * fourier[imax]  # Determinate the min power from the maximum frequency observed
    for i in range(0, imax + 100):  # search for the biginning of the peak
        if fourier[i] >= threshold:
            if (i_begin == -1):
                i_begin = i
        if (i_begin != -1 and fourier[i] < threshold):
            break
    i_end = i
    imax = np.argmax(fourier[0:i_end + 100])  # find the higher frequency in the peak zone

    freq = (imax * f_s) / (nb_frame * CHANNELS)  # formula to convert index into sound frequency

    # frequency database
    note = 0
    name = np.array(
        ["C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0", "C1", "C#1", "D1", "D#1", "E1",
         "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1", "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G2#", "A2",
         "A2#", "B2", "C3", "C3#", "D3", "D3#", "E3", "F3", "F3#", "G3", "G3#", "A3", "A3#", "B3", "C4", "C4#", "D4",
         "D4#", "E4", "F4", "F4#", "G4", "G4#", "A4", "A4#", "B4", "C5", "C5#", "D5", "D5#", "E5", "F5", "F5#", "G5",
         "G5#", "A5", "A5#", "B5", "C6", "C6#", "D6", "D6#", "E6", "F6", "F6#", "G6", "G6#", "A6", "A6#", "B6", "C7",
         "C7#", "D7", "D7#", "E7", "F7", "F7#", "G7", "G7#", "A7", "A7#", "B7", "C8", "C8#", "D8", "D8#", "E8", "F8",
         "F8#", "G8", "G8#", "A8", "A8#", "B8", "Beyond B8"])
    frequencies = np.array(
        [16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89,
         41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00,
         103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00,
         233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88,
         523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, 1046.50,
         1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53, 2093.00,
         2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01,
         4434.92, 4698.64, 4978.03, 5274.04, 5587.65, 5919.91, 6271.93, 6644.88, 7040.00, 7458.62, 7902.13, 8000])

    # plt.plot(fourier)
    # plt.savefig(os.path.join(output_dir, f"fourier_plot_{plot_count}.png"))

    # searching for matched frequencies
    for i in range(0, frequencies.size - 1):
        if (freq < frequencies[0]):  # if the note heard is not a piano note (too low or too high)
            note = name[0]
            break
        if (freq > frequencies[-1]):
            note = name[-1]
            break
        if freq >= frequencies[i] and frequencies[i + 1] >= freq:
            # If the frequency heard is between 2 notes, calculate if it's closer to the note before or after
            if freq - frequencies[i] < (frequencies[i + 1] - frequencies[i]) / 2:
                note = name[i]
            else:
                note = name[i + 1]
            break

    # plot_count += 1
    amplitude = np.max(sound)  # Amplitude is the maximum value in the sound array
    return note, amplitude


p = pyaudio.PyAudio()

stream = p.open(  # audio stream opened with the format specified before
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAME_PACKET,
    input_device_index=0  # Use the index of the device you want to use
)
allframes = []
tmpframes = []
cpt = 0
print(f"* recording:{RECORD_SECONDS} s")
notes = []
notes_times = []  ## Liste pour stocker les temps des notes acceptées
former_amplitude = 0  # the amplitude of the note registered before
former_note = "H1"  # impossible note
former_note_amplitude = 1  # amplitude of the former note
frame_duration = 1.0 / RATE  ## Durée d'un cadre en secondes
for i in range(0, int(RATE * RECORD_SECONDS)):  # for each frame
    cpt = cpt + 1
    leframe = stream.read(1)
    allframes.append(leframe)
    tmpframes.append(leframe)
    if cpt == FRAME_PACKET:
        note, amplitude = note_detect(tmpframes, FRAME_PACKET, RATE, plot_count)
        print(f" note : {note} & amplitude : {amplitude}")

        ## Calculer le temps actuel
        current_time = i * frame_duration

        if amplitude >= 0.015 and (former_amplitude + 0.002) <= amplitude:  # Check the amplitude
            if note != former_note or (note == former_note and (former_note_amplitude + 0.02) < amplitude):
                print(f" Note Accepted : {note}")
                notes.append(note)
                notes_times.append([note, round(current_time, 2)])  # Ajouter la note et son temps à la liste
                former_note_amplitude = amplitude
                former_note = note
        former_amplitude = amplitude
        tmpframes = []
        cpt = 0

print("* done recording")
stream.stop_stream()
stream.close()
p.terminate()

plt.show()

print("* saving")
obj = wave.open("C:/Users/CYTech Student/OneDrive - eisti.eu/Corée/Speech recognition/project/MyVoicemono.Wav", "wb")
obj.setnchannels(CHANNELS)
obj.setsampwidth(p.get_sample_size(FORMAT))
obj.setframerate(RATE)
obj.writeframes(b"".join(allframes))
obj.close()
print("* done saving")

# Afficher les notes acceptées et leurs temps
for note, time in notes_times:
    print(f"Note {note} accepted at {time:.2f} seconds")

# Afficher le tableau des notes et leurs temps
print("Tableau des notes et leurs temps :")
print(notes_times)
