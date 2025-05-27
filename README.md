# Traffic Flow Simulator with MQTT  

A real-time traffic flow monitoring system using simulated data publishers and subscribers via MQTT.  

## Features  
- **Publisher**: Generates synthetic traffic data with configurable intervals, wild data, and packet loss.  
- **Subscriber**: Visualizes traffic flow via dynamic charts (gauge, bar, line) and detects congestion/missing packets.  
- **MQTT**: Decentralized communication between publishers and subscribers.  

## Usage  
1. Run publishers: `python group_2_publisher.py [ID]`  
2. Run subscribers: `python group_2_subscriber.py [ID]`  
3. Adjust parameters via GUI sliders.  

## Dependencies  
- Python 3.x  
- `paho-mqtt`, `tkinter`, `matplotlib`  
