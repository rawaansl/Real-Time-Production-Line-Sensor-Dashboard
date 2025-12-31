
# Unit Tests for SensorWorker thread
# This file contains automated test cases to verify the functionality
# of the SensorWorker class in sensor_worker.py, ensuring proper
# initialization, signal emission, and clean shutdown behavior.



import unittest
from PyQt6.QtTest import QTest
from PyQt6.QtCore import QCoreApplication
from sensor_worker import SensorWorker
from simulator import load_config



class TestSensorWorker(unittest.TestCase):
    
    def setUp(self):
        self.app = QCoreApplication([])
        self.config = load_config()
    
    
    # --- 1. WORKER INITIALIZATION TESTS ---
    def test_worker_initialization(self):
        """Verify worker thread initializes correctly"""
        worker = SensorWorker()
        
        self.assertIsNotNone(worker)
        self.assertFalse(worker.isRunning())
        self.assertTrue(worker._run_flag)
    
    
    # --- 2. SIGNAL EMISSION TESTS ---
    def test_signal_emission(self):
        """Verify signals are emitted correctly"""
        worker = SensorWorker()
        received_data = []
        log_messages = []
        
        def capture_data(data):
            received_data.append(data)
        
        def capture_log(msg):
            log_messages.append(msg)
        
        worker.data_received.connect(capture_data)
        worker.log_message.connect(capture_log)
        worker.start()
        
        # Wait for connection attempt
        QTest.qWait(1000)  # 1 second
        
        worker.stop()
        worker.wait()
        
        # Should have attempted to connect
        self.assertIn("Attempting to connect to simulator...", log_messages)
        # If simulator is running, should receive data, but since it's not, just check attempt
    
    
    # --- 3. WORKER SHUTDOWN TESTS ---
    def test_shutdown(self):
        """Verify worker stops cleanly"""
        worker = SensorWorker()
        worker.start()
        
        self.assertTrue(worker.isRunning())
        
        worker.stop()
        worker.wait(5000)  # 5-second timeout
        
        self.assertFalse(worker.isRunning())


if __name__ == '__main__':
    unittest.main()
