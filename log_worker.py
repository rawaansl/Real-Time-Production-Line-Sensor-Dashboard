import socket
import json
import time
import os




from PyQt6.QtCore import QThread, pyqtSignal




# LogWorker handles logging in a separate thread to keep the UI responsive

class LogWorker(QThread):
    # This is the signal that the UI will connect to
    log_message = pyqtSignal(str) 

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # We start the event loop for this thread
        # This allows the thread to stay alive and handle signals
        self.exec() 


    def stop(self):
        self.quit() # Tells the thread's event loop to stop
        self.wait() # Waits for it to actually finish
