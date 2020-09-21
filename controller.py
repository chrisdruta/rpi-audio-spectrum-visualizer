from __future__ import annotations
from threading import Thread
from queue import SimpleQueue

import os
import struct
import subprocess
import time
import tempfile
from enum import Enum

#import RPi.GPIO as GPIO

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

class StateMachine:
    def __init__(self, initial_state: State, wait: int = 0.1):
        self.command_queue = SimpleQueue()
        self.loop_thread: Thread = Thread(target=self.loop)
        self.state_function_thread: Thread = Thread()

        self.state_function_thread.start()  # start with no target so first join doesn't fail
        self.command_queue.put(initial_state)
        self.current_state = None
        self.wait = wait

        # Configure the count of pixels:
        PIXEL_COUNT = 32

        # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
        SPI_PORT   = 0
        SPI_DEVICE = 0

        #self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

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
        while state_machine.current_state == States.idle:
            print("idling...")
            time.sleep(1)
        return

    def new(state_machine: StateMachine):
        while state_machine.current_state == States.new:
            print("doing the thing")
            time.sleep(1)
        return

    def cava(state_machine: StateMachine):

        BARS_NUMBER = 32
        # OUTPUT_BIT_FORMAT = "8bit"
        OUTPUT_BIT_FORMAT = "16bit"
        # RAW_TARGET = "/tmp/cava.fifo"
        RAW_TARGET = "/dev/stdout"

        conpat = """
        [general]
        bars = %d
        [input]
        method = pulse
        source = echoCancel_source
        [output]
        channels = mono
        method = raw
        raw_target = %s
        bit_format = %s
        """

        config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
        bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)

         with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()

        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER

        if RAW_TARGET != "/dev/stdout":
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, "rb")
        else:
            source = process.stdout

        while state_machine.current_state == States.cava:
            data = source.read(chunk)
            if len(data) < chunk:
                break
            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            print(sample)

        return
