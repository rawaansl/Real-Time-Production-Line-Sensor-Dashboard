import socket
import json
import time
import asyncio
import websockets
import simulator

from PyQt6.QtCore import QThread, pyqtSignal


# Worker thread class to handle data reception from the simulator over TCP 
class SensorWorker(QThread):
    
    # Signals maintaining thread safety with the main GUI thread
    data_received = pyqtSignal(list)
    alarm_triggered = pyqtSignal(dict)
    log_message = pyqtSignal(str)  
    
    
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.client = None

    def run(self):
        self._run_flag = True
        host = simulator.load_config()['connection']['host']
        port = simulator.load_config()['connection']['tcp_port']
        
        self.log_message.emit("Attempting to connect to simulator...")
        
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP socket 
            self.client.settimeout(5.0)  # timeout for connection attempts and recv
            self.client.connect((host, port))

            self.log_message.emit("Connected to simulator successfully.") 
            
            
            while self._run_flag:
                try:
                    raw_data = self.client.recv(4096).decode('utf-8') # Receive data from simulator
                    
                    if not raw_data:
                        self.log_message.emit("Connection closed by simulator.")
                        break
                        
                    lines = raw_data.strip().split('\n')   # Handle multiple JSON objects if sent together
                    
                    for line in lines:
                        if line:
                            sensor_list = json.loads(line)
                            self.data_received.emit(sensor_list)
                            
                except socket.timeout:
                    self.log_message.emit("Stream Heartbeat: No data received, continuing to listen...")
                    continue
                except Exception as e:
                    self.log_message.emit(f"Data Error: {str(e)}")
                    break
                
                
        # Handle connection errors
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


# Worker thread class to handle data reception from the simulator over WebSocket
class WebSocketWorker(QThread):
    data_received = pyqtSignal(list)
    log_message = pyqtSignal(str)
    alarm_triggered = pyqtSignal(dict)
    
    # Initialize with the WebSocket URL
    def __init__(self, url="ws://localhost:8080"):
        super().__init__()
        self.url = url
        self._run_flag = True

    def stop(self):
        self._run_flag = False
        
        
    # Run the event loop for WebSocket connection
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.listen())
        
    # listen for incoming WebSocket messages
    async def listen(self):
        self.log_message.emit(f"Connecting to {self.url}...")
        try:
            async with websockets.connect(self.url) as websocket:
                self.log_message.emit("WebSocket Connected.")
                
                while self._run_flag:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)   # 5-second timeout
                        data = json.loads(message) # message is a JSON array of sensor data
                        self.data_received.emit(data) # Emit received data to main thread 
                        
                    except asyncio.TimeoutError:
                        self.log_message.emit("Stream Heartbeat: Waiting for data...")
                    except Exception as e:
                        self.log_message.emit(f"Stream Error: {e}")
                        break

        except Exception as e:
            self.log_message.emit(f"Could not connect: {e}")
        self.log_message.emit("WebSocket Disconnected.")



# Worker thread class to replay saved sensor data from a file 
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
                if not self._run_flag: 
                    break
                
                # Emit the sensor data list
                self.data_received.emit(entry['sensors'])
                time.sleep(0.5)  # Simulate real-time delay (2Hz)
                
            self.log_message.emit("OFFLINE: Replay finished.")
        except Exception as e:
            self.log_message.emit(f"OFFLINE ERROR: {str(e)}")

    def stop(self):
        self._run_flag = False
