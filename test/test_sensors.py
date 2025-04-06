import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from sensors import SensorFilter, read_dht22

class MockDHTDevice:
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def exit(self):
        pass

@pytest.fixture
def sensor_filter():
    return SensorFilter()

def test_sensor_filter_initialization(sensor_filter):
    """Test that filter initializes correctly"""
    assert sensor_filter.temp_buffer.maxlen == 5
    assert sensor_filter.humidity_buffer.maxlen == 5
    assert len(sensor_filter.temp_buffer) == 0
    assert len(sensor_filter.humidity_buffer) == 0

def test_sensor_filter_add_reading(sensor_filter):
    """Test adding readings to the filter"""
    sensor_filter.add_reading(20.5, 55.0)
    assert len(sensor_filter.temp_buffer) == 1
    assert len(sensor_filter.humidity_buffer) == 1
    assert sensor_filter.temp_buffer[0] == 20.5
    assert sensor_filter.humidity_buffer[0] == 55.0

def test_sensor_filter_get_filtered_values(sensor_filter):
    """Test getting filtered values"""

    for i in range(5):
        sensor_filter.add_reading(20.0 + i, 50.0 + i)
    
    temp, humidity = sensor_filter.get_filtered_values()
    assert temp == 22  # avg of 20,21,22,23,24 rounded to integer
    assert humidity == 52  # avg of 50,51,52,53,54 rounded to integer

@patch('sensors.adafruit_dht.DHT22')
def test_read_dht22_success(mock_dht22):
    """Test successful DHT22 reading"""
    # Setup mock
    mock_device = MagicMock()
    mock_device.temperature = 20.5
    mock_device.humidity = 55.0
    mock_dht22.return_value = mock_device

    # Test
    temp, humidity = read_dht22()
    
    assert temp == 20.5
    assert humidity == 55.0
    mock_device.exit.assert_called_once()

@patch('sensors.adafruit_dht.DHT22')
def test_read_dht22_failure(mock_dht22):
    """Test DHT22 reading failure"""
    # Setup mock to raise an exception
    mock_device = MagicMock()
    type(mock_device).temperature = PropertyMock(side_effect=Exception("Sensor read error"))
    mock_device.humidity = 55.0
    mock_dht22.return_value = mock_device

    # Test
    temp, humidity = read_dht22()
    
    assert temp is None
    assert humidity is None
    mock_device.exit.assert_called_once()

def test_sensor_filter_handles_none_values(sensor_filter):
    """Test that the filter handles None values correctly"""
    # Add some valid readings
    sensor_filter.add_reading(20.0, 50.0)
    sensor_filter.add_reading(21.0, 51.0)
    sensor_filter.add_reading(None, None)
    sensor_filter.add_reading(22.0, 52.0)
    sensor_filter.add_reading(23.0, 53.0)
    temp, humidity = sensor_filter.get_filtered_values()
    assert temp is not None
    assert humidity is not None 