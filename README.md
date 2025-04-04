# DHT22 Room Monitor

A Python application for monitoring room temperature and humidity using a DHT22 sensor and publishing the data via MQTT. The application implements a moving average filter to provide stable, accurate readings optimized for indoor environments.

## Features

- DHT22 sensor reading with error handling
- Moving average filter for stable measurements
- Integer-rounded temperature and humidity values for practical home monitoring
- MQTT publishing of temperature and humidity data
- Optimized 30-second sampling interval for room monitoring
- Clean shutdown handling
- Automatic startup on Raspberry Pi boot

## Hardware Requirements

- Raspberry Pi (any model)
- DHT22 temperature and humidity sensor
- The DHT22 sensor should be connected to GPIO4 (Pin 7)

## Prerequisites

- Docker and Docker Compose installed and running
- MQTT broker running in Docker (as defined in docker-compose.yaml)
- `netcat` package for service health check:
  ```bash
  sudo apt-get install netcat
  ```

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install pip-tools:
```bash
pip install pip-tools
```

3. Generate and install requirements:
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
5. Round values to whole numbers for practical use
6. Publish filtered data to MQTT topics:
   - `sensor/dht/temperature`
   - `sensor/dht/humidity`

## MQTT Topics

The following topics provide integer-rounded values suitable for home automation:
- Temperature: `sensor/dht/temperature` (°C, whole numbers)
- Humidity: `sensor/dht/humidity` (%, whole numbers)

## Data Quality

- Sampling Interval: 30 seconds (optimized for room monitoring)
- Filter Window: 5 samples
- Initial Stabilization Time: 2.5 minutes
- Temperature Resolution: 1°C (rounded for practical use)
- Humidity Resolution: 1%
- Value Smoothing: Moving average over 2.5 minutes
- Noise Reduction: Integer rounding removes minor fluctuations

The combination of moving average filter and integer rounding provides:
- Stable readings without unnecessary decimal precision
- Elimination of sensor noise and minor fluctuations
- Values that are practical for home automation and display
- Reduced MQTT message size

## Troubleshooting

1. If the service fails to start:
   ```bash
   journalctl -u dht22-monitor -n 50
   ```

2. Common issues:
   - Check if Docker is running: `sudo systemctl status docker`
   - Verify MQTT container is running: `docker ps | grep mosquitto`
   - Test MQTT port: `nc -zv localhost 1883`
   - Check GPIO permissions
   - Ensure virtual environment paths are correct
   - Check sensor connections

3. To restart after configuration changes:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart dht22-monitor
   ```

4. Docker-specific issues:
   - If the service starts before MQTT is ready, it will retry automatically
   - Check Docker logs: `docker logs <mosquitto_container_id>`
   - Verify Docker compose status: `docker-compose ps`

## License

MIT License 