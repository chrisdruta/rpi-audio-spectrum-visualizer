import os
import struct
import subprocess
import time
import tempfile

import colorsys

import sounddevice as sd
import numpy as np

from controller import StateMachine

def idle(state_machine: StateMachine):

    def wheel(pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    for i in range(len(state_machine.pixels)):
        state_machine.pixels[i] = wheel(((i * 256 // len(state_machine.pixels))) % 256)
    state_machine.pixels.show()

    while state_machine.current_state == idle:
        first = state_machine.pixels[0]
        for i in range(len(state_machine.pixels) - 1):
            state_machine.pixels[i] = state_machine.pixels[i + 1]
        state_machine.pixels[len(state_machine.pixels) - 1] = first

        state_machine.pixels.show()
        time.sleep(0.2)
    return


def pink(state_machine: StateMachine):
    hue, sat, lum = (328/360, 100/100, 11/100)
    while state_machine.current_state == pink:
        for i in range(100):
            lum -= 0.001
            r, g, b = colorsys.hls_to_rgb(hue, lum, sat)
            val = (int(r * 255), int(g * 255), int(b * 255))

            state_machine.pixels.fill(val)
            state_machine.pixels.show()

        time.sleep(1)
        for i in range(100):
            lum += 0.001
            r, g, b = colorsys.hls_to_rgb(hue, lum, sat)
            val = (int(r * 255), int(g * 255), int(b * 255))

            state_machine.pixels.fill(val)
            state_machine.pixels.show()
    return

def custom_fft(state_machine: StateMachine):
    CHUNK = 2048
    with sd.InputStream(channels=1, samplerate=44100, blocksize=CHUNK) as stream:
        while state_machine.current_state == custom_fft:
            data = stream.read(CHUNK)[0]
            fft_size = 64

            magnitude = np.abs(np.fft.rfft(data.transpose(), n=fft_size)[0 : data.size // 2]).transpose()
            magnitude *= 2550 / fft_size
            #magnitude /= np.max(magnitude)

            for i, mag in enumerate(magnitude):
                val = int(mag)
                state_machine.pixels[i] = (val, val, val)
                state_machine.pixels[63-i] = (val, val, val)
            state_machine.pixels.show()

def cava(state_machine: StateMachine):

    BARS_NUMBER = int(state_machine.num_pixels / 2)
    OUTPUT_BIT_FORMAT = '8bit'
    #OUTPUT_BIT_FORMAT = '16bit'
    # RAW_TARGET = "/tmp/cava.fifo"
    RAW_TARGET = '/dev/stdout'

    conpat = """
    [general]
    bars = %d
    autosens = 0
    ; higher_cutoff_freq = 10000
    higher_cutoff_freq = 7000
    [input]
    method = pulse
    source = echoCancel_source
    ;source = alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono
    [output]
    channels = mono
    method = raw
    raw_target = %s
    bit_format = %s
    [smoothing]
    gravity = 100
    [eq]
    1=2
    2=1
    3=1
    4=1
    5=1
    """
    config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
    bytetype, bytesize, bytenorm = ('H', 2, 65535) if OUTPUT_BIT_FORMAT == '16bit' else ('B', 1, 255)

    def hue_range(i, level, val=1.0, sat=100, start=0, end=360):
        hue, sat, val = (start/360, sat/100, val)
        val *= level

        hue_delta = end - start
        if hue_delta < 0:
            hue_delta += 360

        hue += i / BARS_NUMBER * hue_delta / 360
        hue -= int(hue)

        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return ((int(r * 255), int(g * 255), int(b * 255)))

    def sat_range(i, level, val=1.0, hue=0, start=100, end=90):
        hue, sat, val = (hue/360, start/100, val)
        val *= level

        sat_delta = end - start
        sat += i / BARS_NUMBER * sat_delta / 100
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return ((int(r * 255), int(g * 255), int(b * 255)))

    if state_machine.cava_mode == "between-hues":
        get_bar_color = hue_range

    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()

        process = subprocess.Popen(['cava', '-p', config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER

        if RAW_TARGET != '/dev/stdout':
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, 'rb')
        else:
            source = process.stdout

        while state_machine.current_state == cava:
            data = source.read(chunk)
            if len(data) < chunk:
                break
            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            for i, level in enumerate(sample):
                #val = get_bar_color(i, level, val=1.0, start_hue=0, end_hue=360)
                val = sat_range(i, level, val=0.5, hue=0, start=100, end=90)
                state_machine.pixels[i] = val
                state_machine.pixels[state_machine.num_pixels - 1 - i] = val
            state_machine.pixels.show()

    process.terminate()
    return