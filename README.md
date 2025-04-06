# DHT22 Room Monitor

A Python program for monitoring room temperature and humidity using a DHT22 sensor and publishing via MQTT. The program implements a moving average filter to provide readings
for indoor environments.

## Features

- DHT22 sensor reading with error handling
- Moving average filter
- Integer-rounded temperature and humidity values
- MQTT publishing of temperature and humidity data
- Optimized 30-second sampling interval
- Clean shutdown handling
- Automatic startup on Raspberry Pi boot

## Hardware Requirements

- Raspberry Pi (any model)
- DHT22 temperature and humidity sensor on GPIOs
- The DHT22 sensor should be connected to GPIO4 (Pin 7)

## Prerequisites

- Python 3.10
- Docker and Docker Compose installed and running
- MQTT broker running on port 1883

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install pip-tools:
```bash
pip install pip-tools
```

3. Generate and install requirements with pip-compile:
```bash
pip-compile requirements.in
pip install -r requirements.txt
```

## Startup Configuration

To make the script run automatically at boot:

1. Install netcat for Docker container health check:
```bash
sudo apt-get install netcat
```

2. Edit the systemd service file:
```bash
sudo nano /etc/systemd/system/dht22-monitor.service
```

3. Copy the contents of `dht22-monitor.service` into this file

4. Make sure the paths in the service file match your installation:
   - Update `User=` to your username
   - Update `WorkingDirectory=` to your installation path
   - Update `ExecStart=` to point to your virtual environment and script

5. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dht22-monitor
sudo systemctl start dht22-monitor
```

6. Check the service status:
```bash
sudo systemctl status dht22-monitor
```

7. View the logs:
```bash
journalctl -u dht22-monitor -f
```

## Configuration

The following settings can be modified in `sensors.py`:

- `MQTT_BROKER`: MQTT broker address (default: "localhost")
- `MQTT_PORT`: MQTT broker port (default: 1883)
- `MQTT_TOPIC`: Base topic for MQTT messages (default: "sensor/dht")

## Usage

The script will start automatically at boot, after Docker and the MQTT container are running. For manual control:

```bash
# Start the service
sudo systemctl start dht22-monitor

# Stop the service
sudo systemctl stop dht22-monitor

# Restart the service
sudo systemctl restart dht22-monitor
```

The script will:
1. Wait for the Docker MQTT container to be available
2. Initialize the DHT22 sensor
3. Start collecting readings every 30 seconds
4. Apply a moving average filter over 5 readings
6. Publish filtered data to MQTT topics:
   - `sensor/dht/temperature`
   - `sensor/dht/humidity`

## MQTT Topics

The following topics provide integer-rounded values:
- Temperature: `sensor/dht/temperature` (°C, whole numbers)
- Humidity: `sensor/dht/humidity` (%, whole numbers)

## Data Quality

- Sampling Interval: 30 seconds
- Filter Window: 5 samples
- Initial Stabilization Time: 2.5 minutes


## Troubleshooting

1. If the service fails to start:
```bash
journalctl -u dht22-monitor -n 50
```

2. Common issues:
   - Test MQTT port: `nc -zv localhost 1883`
   - Check GPIO permissions
   - Ensure virtual environment paths are correct
   - Check sensor connections

3. To restart after configuration changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart dht22-monitor
```
