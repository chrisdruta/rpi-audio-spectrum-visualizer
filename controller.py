import time
from threading import Thread
from queue import SimpleQueue

import board
from adafruit_ws2801 import WS2801

class StateMachine:
    def __init__(self, initial_state, wait: float = 0.1):
        self.command_queue: SimpleQueue = SimpleQueue()
        self.loop_thread: Thread = Thread(target=self.loop)
        self.state_function_thread: Thread = Thread()

        self.state_function_thread.start()  # start with no target so first join doesn't fail
        self.command_queue.put(initial_state)
        self.current_state = None
        self.wait = wait

        self.num_pixels = 50
        self.pixels = WS2801(board.SCLK, board.MOSI, self.num_pixels, auto_write=False, baudrate=1000000)
        self.pixels.fill((255, 0, 0))
        self.pixels.show()

        self.cava_mode = "between-hues"


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
