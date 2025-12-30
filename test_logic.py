from operator import contains
import unittest
import json
from unittest.mock import patch, mock_open
import simulator


# Unit Test Suite for Industrial Sensor Simulator

# This file contains the automated test cases for verifying
# the core logic of the `simulator.py` module.
# It ensures that the configuration loader, payload generator, and alarm logic function reliably under both
# success and failure conditions.



class TestSensorDashboard(unittest.TestCase):


    # --- Tests for load_config ---
    
    
    # NB --> the code will attempt to open 'sensors_config.json' in the current directory 
    # use @patch to mock open function calls within load_config
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_config_success(self, mock_file):
        
        # Test that config loads correctly when file exists
        
        result = simulator.load_config()
        self.assertEqual(result, {"test": "data"})
        mock_file.assert_called_with('sensors_config.json', 'r')


    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_file):
        
        # Test that SystemExit is raised when file is not found
    
        with self.assertRaises(SystemExit) as cm:
            simulator.load_config()
        self.assertEqual(cm.exception.code, 1)

    # --- Tests for generate_payload ---

    def setUp(self):
        # Common sensor settings for payload tests
        self.sensor_settings = {
            "Temp": {"low": 20.0, "high": 30.0, "variation": 5.0}
        }

    def test_payload_structure(self):
        
        # Ensure generated payload has correct structure
        
        payload = simulator.generate_payload(self.sensor_settings)
        self.assertEqual(len(payload), 1)
        item = payload[0]
        self.assertIn("name", item)
        self.assertIn("value", item)
        self.assertIn("status", item)
        self.assertIn("timestamp", item)


    def test_alarm_logic_ok(self):

        # We mock random.uniform to return a safe value: 25.0
        with patch("random.uniform", return_value=25.0):
            payload = simulator.generate_payload(self.sensor_settings)
            self.assertEqual(payload[0]["status"], "OK")

    def test_alarm_logic_high(self):

        with patch("random.uniform", return_value=35.0):
            payload = simulator.generate_payload(self.sensor_settings)
            self.assertEqual(payload[0]["status"], "HIGH ALARM")

    def test_alarm_logic_low(self):

        with patch("random.uniform", return_value=15.0):
            payload = simulator.generate_payload(self.sensor_settings)
            self.assertEqual(payload[0]["status"], "LOW ALARM")
            
            
            
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
        payload = simulator.generate_payload(config)
        api_string = json.dumps(payload) + "\n"
        
        # 3. Assertions (The "Tests")
        self.assertTrue(api_string.endswith("\n"), "API Output must use newline termination.")
        
        decoded_payload = json.loads(api_string.strip())
        self.assertEqual(len(decoded_payload), 2, "API Output count must match config count.")
        self.assertEqual(decoded_payload[0]['name'], "Temp")


if __name__ == '__main__':
    unittest.main()
