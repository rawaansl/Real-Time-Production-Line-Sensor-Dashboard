import socket
import json
import time
import asyncio
import websockets
import simulator

from PyQt6.QtCore import QThread, pyqtSignal

class SensorWorker(QThread):
    
    # Signals maintaining thread safety with the main GUI thread
    data_received = pyqtSignal(list)
    alarm_triggered = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True # Flag to control the while loop
        self.client = None

    def run(self):
        self._run_flag = True
        host = simulator.load_config()['connection']['host']
        port = simulator.load_config()['connection']['tcp_port']
        
        self.log_message.emit("Attempting to connect to simulator...")  # Log connection attempt 
        # updated in UI through signal-slot mechanism --> log_message signal and update_log slot
        
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Create TCP socket client 
            
            # Set a timeout so recv() doesn't block forever when we try to stop
            # set a timeout so connection doesn't hang indefinitely
            self.client.settimeout(5.0) 
            
            # Connect to the simulator server on the specified host and port
            self.client.connect((host, port))   # Connect to simulator server 
            # connect method blocks until connection is established or fails like accept method in the server side 
            
            
            self.log_message.emit("Connected to simulator successfully.") 
            
            
            while self._run_flag:
                try:
                    # Wait for data from the simulator
                    raw_data = self.client.recv(4096).decode('utf-8')    # Blocking call with timeout 
                    
                    if not raw_data:
                        self.log_message.emit("Connection closed by simulator.")
                        break
                        
                    lines = raw_data.strip().split('\n')
                    for line in lines:
                        if line:
                            sensor_list = json.loads(line)
                            self.data_received.emit(sensor_list)
                            
                except socket.timeout:
                    # Timeout is normal, it just lets us check if _run_flag is still True
                    self.log_message.emit("Stream Heartbeat: No data received, continuing to listen...")
                    continue
                except Exception as e:
                    self.log_message.emit(f"Data Error: {str(e)}")
                    break

        except ConnectionRefusedError:
            self.log_message.emit("Error: Simulator not found. Is it running?")
            
        except Exception as e:
            self.log_message.emit(f"Connection Error: {str(e)}")
        finally:
            if self.client:
                self.client.close()
            self._run_flag = False
            self.log_message.emit("Disconnected from simulator successfully.")

    def stop(self):
        """Called by the UI to stop the connection"""
        self._run_flag = False



class WebSocketWorker(QThread):
    data_received = pyqtSignal(list)
    log_message = pyqtSignal(str)

    def __init__(self, url="ws://localhost:8080"):
        super().__init__()
        self.url = url
        self._run_flag = True

    def stop(self):
        self._run_flag = False

    def run(self):
        # We must create a new event loop for this specific thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.listen())

    async def listen(self):
        self.log_message.emit(f"Connecting to {self.url}...")
        try:
            async with websockets.connect(self.url) as websocket:
                self.log_message.emit("WebSocket Connected.")
                
                while self._run_flag:
                    try:
                        # This line blocks until a full message arrives
                        # No need to specify 4096; it handles any size automatically
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        
                        # WebSockets usually send JSON strings
                        data = json.loads(message)
                        
                        # Throw the data to the Main UI Thread
                        self.data_received.emit(data)
                        
                    except asyncio.TimeoutError:
                        self.log_message.emit("Stream Heartbeat: Waiting for data...")
                    except Exception as e:
                        self.log_message.emit(f"Stream Error: {e}")
                        break
        except Exception as e:
            self.log_message.emit(f"Could not connect: {e}")

        self.log_message.emit("WebSocket Disconnected.")


# offline data parser and replayer
# imports json and time already done above
class OfflineReplayWorker(QThread):
    data_received = pyqtSignal(list)
    alarm_triggered = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._run_flag = True

    def run(self):
        try:
            with open(self.file_path, 'r') as f:
                saved_data = json.load(f)
            
            self.log_message.emit(f"OFFLINE: Loaded {len(saved_data)} data points.")
            
            for entry in saved_data:
                if not self._run_flag: break
                
                # Emit the data just like the live sensor would
                self.data_received.emit(entry['sensors'])
                
                # Sleep to simulate required frequency 2Hz
                time.sleep(0.5) 
                
            self.log_message.emit("OFFLINE: Replay finished.")
        except Exception as e:
            self.log_message.emit(f"OFFLINE ERROR: {str(e)}")

    def stop(self):
        self._run_flag = False
