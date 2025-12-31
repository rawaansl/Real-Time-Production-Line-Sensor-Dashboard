

# Unit Tests for Industrial Sensor Simulator

# This file contains the automated test cases for verifying
# the core logic of the `simulator.py` module.
# It ensures that the configuration loader, payload generator, data parsing and alarm logic function reliably under both
# success and failure conditions.


import unittest
import json
from simulator import load_config, generate_payload
from unittest.mock import patch, mock_open



class TestSimulator(unittest.TestCase):
    
    
    def setUp(self):
        try:
            self.config = load_config()
            self.sensors = self.config['sensors']
        except:
            self.config = None
            self.sensors = None
    
    
    # --- 1. CONFIG LOADER TESTS ---
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_config_success(self, mock_file):
        result = load_config()
        self.assertEqual(result, {"test": "data"})
        mock_file.assert_called_with('config/sensors_config.json', 'r')
        
        
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_file):
        with self.assertRaises(SystemExit) as cm:
            load_config()
        self.assertEqual(cm.exception.code, 1)
        mock_file.assert_called_with('config/sensors_config.json', 'r')
        
        
        
        
        
        
    # --- 2. PAYLOAD GENERATION TESTS ---
    def test_payload_structure(self):
        """Verify generated payload format"""
        payload = generate_payload(self.sensors)
        
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 6)
        
        for sensor_data in payload:
            self.assertIn('name', sensor_data)
            self.assertIn('value', sensor_data)
            self.assertIn('timestamp', sensor_data)
            self.assertIn('status', sensor_data)
    
    # --- 3. ALARM LOGIC TESTS ---
    def test_alarm_logic(self):
        """Verify alarm status determination"""
        payload = generate_payload(self.sensors)
        
        for sensor_data in payload:
            value = sensor_data['value']
            status = sensor_data['status']
            
            # Find corresponding config
            sensor_config = self.sensors[sensor_data['name']]
            
            # Verify alarm logic
            if value < sensor_config['low']:
                self.assertEqual(status, "LOW ALARM")
            elif value > sensor_config['high']:
                self.assertEqual(status, "HIGH ALARM")
            else:
                self.assertEqual(status, "OK")
    
    # --- 4. VALUE RANGE TESTS ---
    def test_value_ranges(self):
        """Verify generated values are within expected ranges"""
        for _ in range(100):  # Test 100 samples
            payload = generate_payload(self.sensors)
            
            for sensor_data in payload:
                sensor_config = self.sensors[sensor_data['name']]
                
                # Value should be within low-variation to high+variation
                min_val = sensor_config['low'] - sensor_config.get('variation', 5.0)
                max_val = sensor_config['high'] + sensor_config.get('variation', 5.0)
                
                self.assertGreaterEqual(sensor_data['value'], min_val - 0.01)
                self.assertLessEqual(sensor_data['value'], max_val + 0.01)
    
    


    # --- 1. SENSOR PARSING ---
    def test_sensor_parsing(self):
        
        # Test that JSON sensor data is parsed correctly into expected structure --> list of dicts

        raw_json = '[{"name": "Temp", "value": 55.0, "status": "OK"}]'
        parsed_data = json.loads(raw_json)
        
        self.assertEqual(len(parsed_data), 1)
        self.assertEqual(parsed_data[0]['name'], "Temp")
        self.assertIsInstance(parsed_data[0]['value'], float)

# --- 5. API OUTPUT TESTS ---
    def test_api_output_compliance(self):
    
        # 1. Setup sample config
        config = {"Temp": {"low": 20, "high": 30}, "Press": {"low": 50, "high": 100}}
        
        # 2. Generate the "API Output"
        payload = generate_payload(config)
        api_string = json.dumps(payload) + "\n"
        
        # 3. Assertions (The "Tests")
        self.assertTrue(api_string.endswith("\n"), "API Output must use newline termination.")
        
        decoded_payload = json.loads(api_string.strip())
        self.assertEqual(len(decoded_payload), 2, "API Output count must match config count.")
        self.assertEqual(decoded_payload[0]['name'], "Temp")


if __name__ == '__main__':
    unittest.main()
