import socket
import json
import time
import random
import asyncio    
import websockets
import sys



def load_config():
    """Load configuration from external JSON file."""
    try:
        with open('config/sensors_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: sensors_config.json not found. Please create it first.")
        sys.exit(1)

def generate_payload(sensor_settings):
    
    """Helper to generate sensor data based on config ranges."""
    payload = []
    for name, limits in sensor_settings.items():
        # Generate value with potential for out-of-bounds (Alarms)
        var = limits.get('variation', 5.0)
        val = round(random.uniform(limits['low'] - var, limits['high'] + var), 2)
        
        if val < limits['low']:
            status = "LOW ALARM"
        elif val > limits['high']:
            status = "HIGH ALARM"
        else:
            status = "OK"
        
        payload.append({
            "name": name,
            "value": val,
            "timestamp": time.strftime("%H:%M:%S"),
            "status": status
        })
    return payload



def run_tcp_simulator():
    
    config = load_config()
    host = config['connection']['host']
    port = config['connection']['tcp_port']
    interval = config['connection']['update_interval'] 
    SENSOR_CONFIG = config['sensors']
            
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"Industrial TCP Simulator Online at {host}:{port}...")
    
    while True:
        try:
            conn, addr = server_socket.accept()    # Wait for a client to connect
            # accept method blocks until a connection is established
            # conn is a new socket object usable to send and receive data on the connection
            # addr is the address bound to the socket on the other end of the connection USED FOR LOGGING
            
            print(f"Dashboard Connected: {addr}")
            
            while True:
                payload = generate_payload(SENSOR_CONFIG)
                json_data = json.dumps(payload) + "\n"
                conn.sendall(json_data.encode('utf-8'))
                
                time.sleep(interval) # required frequency
                
                
        except (ConnectionResetError, BrokenPipeError):
            print("Dashboard disconnected. Waiting...")
        except Exception as e:
            print(f"Simulator Error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()


def run_websocket_simulator():
    
    config = load_config()
    SENSOR_CONFIG = config['sensors']
    interval = config['connection']['update_interval']

    
    # The 'Handler' function called for every new connection
    async def sensor_data(websocket):
        print(f"Dashboard Connected: {websocket.remote_address}")
        try:
            while True:
                payload = generate_payload(SENSOR_CONFIG)
                json_data = json.dumps(payload)  # no manual delimiter needed for WebSocket
                await websocket.send(json_data)
                await asyncio.sleep(interval) # 2Hz Update Frequency
                
                                
        except websockets.exceptions.ConnectionClosed:
            print(f"Dashboard Disconnected: {websocket.remote_address}")
            

    async def main():
        # Using 'async with' ensures the server stops cleanly
        async with websockets.serve(sensor_data, "localhost", config['connection']['ws_port']):
            print("Industrial WebSocket Simulator Online at ws://localhost:8080...")
            await asyncio.Future()  # Run forever
            
            

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulator shut down by user.")


if __name__ == "__main__":
    # You can choose which one to run by uncommenting:
    
    # OPTION A: Run TCP (Default for the current dashboard)
    # try:
    #     run_tcp_simulator()
    # except KeyboardInterrupt:
    #     print("\nTCP Simulator shut down.")

    # OPTION B: Run WebSocket (NOTE ---> update your dashboard worker WebSocketWorker accordingly)
    try:
        asyncio.run(run_websocket_simulator())
    except KeyboardInterrupt:
        print("\nWS Simulator shut down.")
