# dht22_module.py
import time
import signal
import sys
import board
import adafruit_dht
import schedule
import paho.mqtt.publish as publish
from collections import deque
from typing import Optional, Tuple

# MQTT broker settings
MQTT_BROKER = "localhost"  # Change to the IP address or hostname of your MQTT broker
MQTT_PORT = 1883          # Default MQTT port
MQTT_TOPIC = "sensor/dht"

class SensorFilter:
    """Implements a moving average filter for sensor readings."""
    
    def __init__(self, window_size: int = 5):
        """Initialize filter with given window size."""
        self.window_size = window_size
        self.temp_buffer = deque(maxlen=window_size)
        self.humidity_buffer = deque(maxlen=window_size)
        
    def add_reading(self, temperature: float, humidity: float) -> None:
        """Add a new reading to the filter buffers."""
        if temperature is not None and humidity is not None:
            self.temp_buffer.append(temperature)
            self.humidity_buffer.append(humidity)
    
    def get_filtered_values(self) -> Tuple[Optional[float], Optional[float]]:
        """Get filtered temperature and humidity values.
        
        Returns:
            tuple: (temperature, humidity)
                - temperature: rounded to nearest whole number (°C)
                - humidity: rounded to nearest whole number (%)
        """
        if not self.temp_buffer or not self.humidity_buffer:
            return None, None
            
        avg_temp = sum(self.temp_buffer) / len(self.temp_buffer)
        avg_humidity = sum(self.humidity_buffer) / len(self.humidity_buffer)
        return round(avg_temp), round(avg_humidity)
    
    def is_stable(self) -> bool:
        """Check if enough readings have been collected for stable output."""
        return len(self.temp_buffer) == self.window_size

# Initialize the sensor filter
sensor_filter = SensorFilter(window_size=5)

def on_shutdown(signal, frame):
    print("Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, on_shutdown)
    
def read_dht22():
    # VE    - DHT version, e.g. 11 or 22
    # PIN   - GPIO Pin the board is connected to, e.g. D4 = GPIO Pin 4
    """Read temperature and humidity from DHT22 sensor."""
    dht_device = adafruit_dht.DHT22(board.D4)
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        dht_device.exit()
        return temperature_c, humidity
    except Exception as e:
        print(f"Error reading sensor: {e}")
        dht_device.exit()
        return None, None
        
def publish_sensor_data():
    """Read sensor data, apply filtering, and publish to MQTT."""
    # Read raw values
    raw_temp, raw_humidity = read_dht22()
    
    if raw_temp is not None and raw_humidity is not None:
        # Add to filter
        sensor_filter.add_reading(raw_temp, raw_humidity)
        
        # Get filtered values
        temp, humidity = sensor_filter.get_filtered_values()
        
        if temp is not None and humidity is not None and sensor_filter.is_stable():
            print(f"Filtered - Temp: {temp}°C    Humidity: {humidity}%")
            
            # Publish messages to MQTT broker
            msgs = [
                (f"{MQTT_TOPIC}/temperature", str(temp)),
                (f"{MQTT_TOPIC}/humidity", str(humidity))
            ]
            publish.multiple(msgs, hostname=MQTT_BROKER, port=MQTT_PORT, client_id="serverS")
        else:
            print("Collecting initial readings for stable filter output...")

def start_sensor_monitoring():
    """Start periodic sensor monitoring and MQTT publishing.
    
    Uses a 30-second interval optimized for room environment monitoring:
    - Provides stable readings for typical indoor changes
    - Reduces system resource usage
    - Accounts for DHT22 sensor characteristics
    - Maintains good battery life for battery-powered setups
    """
    print("Starting DHT22 room monitoring")
    print("Initializing filter with window size of 5 readings...")
    
    # 30 seconds is optimal for room monitoring:
    # - Temperature changes in rooms are typically gradual
    # - Humidity changes are also relatively slow in indoor environments
    # - Reduces unnecessary readings while maintaining accuracy
    schedule.every(30).seconds.do(publish_sensor_data)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_sensor_monitoring()
