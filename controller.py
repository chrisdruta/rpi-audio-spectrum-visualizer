# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
from threading import Lock

#import RPi.GPIO as GPIO

from enum import Enum

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

class StateMachine:
    def __init__(self, buffer: list, lock: Lock, wait: int = 0.1):
        self.buffer = buffer
        self.lock = lock
        self.wait = wait

        # Configure the count of pixels:
        PIXEL_COUNT = 32

        # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
        SPI_PORT   = 0
        SPI_DEVICE = 0

        #self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

    def start_loop(self):
        while True:
            with self.lock:
                current_state = self.buffer.pop(0)
                current_state(self.lock, self.buffer)
            time.sleep(self.wait)

    def set_state(self, state: str) -> bool:
        with self.lock:
            self.buffer.clear()
            self.buffer.append(States.__dict__[state])


class States(Enum):
    def _names():
        return [state for state in States.__dict__.keys() if not state.startswith("_")]

    def idle(lock, buffer: list):
        pass
        buffer.append(States.idle)

    def new(lock, buffer: list):
        pass
        buffer.append(States.new)
