from __future__ import annotations
from threading import Thread
from queue import SimpleQueue

import os
import struct
import subprocess
import time
import tempfile

from enum import Enum

import sounddevice as sd
import numpy as np

import board
import adafruit_ws2801

class StateMachine:
    def __init__(self, initial_state: State, wait: int = 0.1):
        self.command_queue = SimpleQueue()
        self.loop_thread: Thread = Thread(target=self.loop)
        self.state_function_thread: Thread = Thread()

        self.state_function_thread.start()  # start with no target so first join doesn't fail
        self.command_queue.put(initial_state)
        self.current_state = None
        self.wait = wait


        self.pixels = adafruit_ws2801.WS2801(board.SCLK, board.MOSI, 64, auto_write=False)
        self.pixels.fill((255, 0, 0))
        self.pixels.show()


    def start_loop(self):
        self.loop_thread.start()

    def loop(self):
        while True:
            if not self.command_queue.empty():
                new_state = self.command_queue.get()
                if new_state != self.current_state:
                    # Update current state to signify state function thread to join
                    self.current_state = new_state
                    self.state_function_thread.join()
                    # Start new state function thread
                    self.state_function_thread = Thread(target=self.current_state, args=(self,))
                    self.state_function_thread.start()

            time.sleep(self.wait)


class States(Enum):
    def _names() -> List[str]:
        return [state for state in States.__dict__.keys() if not state.startswith("_")]

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

        while state_machine.current_state == States.idle:
            first = state_machine.pixels[0]
            for i in range(len(state_machine.pixels) - 1):
                state_machine[i] = state_machine[i + 1]
            state_machine.pixels[len(state_machine.pixels) - 1] = first
            state_machine.pixels.show()
            time.sleep(0.2)
        return

    def pink(state_machine: StateMachine):
        while state_machine.current_state == States.pink:
            for i in range(100):  # 100 breath levels
                temp = i / 100
                state_machine.pixels.fill((min(255,int(2*255*temp)), min(255,int(2*255*(1-temp))), 0))
                state_machine.pixels.show()
                time.sleep(0.5)
        return

    def custom_fft(state_machine: StateMachine):
        CHUNK = 2048
        with sd.InputStream(channels=1, samplerate=44100, blocksize=CHUNK) as stream:
            while state_machine.current_state == States.custom_fft:
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

        BARS_NUMBER = 32
        OUTPUT_BIT_FORMAT = '8bit'
        #OUTPUT_BIT_FORMAT = '16bit'
        # RAW_TARGET = "/tmp/cava.fifo"
        RAW_TARGET = '/dev/stdout'

        conpat = """
        [general]
        bars = %d
        autosens = 0
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
        """

        config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
        bytetype, bytesize, bytenorm = ('H', 2, 65535) if OUTPUT_BIT_FORMAT == '16bit' else ('B', 1, 255)

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

            while state_machine.current_state == States.cava:
                data = source.read(chunk)
                if len(data) < chunk:
                    break
                # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
                sample = [i / bytenorm for i in struct.unpack(fmt, data)]
                for i, bin in enumerate(sample):
                    val = int(bin * 255)
                    state_machine.pixels[i] = (val, val, val)
                    state_machine.pixels[63-i] = (val, val, val)
                state_machine.pixels.show()

        process.terminate()
        return

if __name__ == '__main__':
    state_machine = StateMachine(initial_state=States.custom_fft)
    state_machine.start_loop()