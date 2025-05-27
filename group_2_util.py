# group_2_util.py

import random
import time

start_id = 111
YELLOW_DURATION = 4 # Use a constant to comply with Canadian traffic light standards

# Return a string based on the flow rate
def get_traffic_level(flow_rate):
    if flow_rate <= 0.25:
        return "Low"
    elif flow_rate <= 0.5:
        return "Moderate"
    elif flow_rate <= 0.75:
        return "Heavy"
    else:
        return "Severe"

# Calculate light timings based on the value from the flow rate
def calculate_light_timings(traffic_level):
    if traffic_level == "Low":
        return {
            'red': random.randint(10, 20),
            'green': random.randint(30, 45),
            'yellow': YELLOW_DURATION
        }
    elif traffic_level == "Moderate":
        return {
            'red': random.randint(20, 30),
            'green': random.randint(20, 30),
            'yellow': YELLOW_DURATION
        }
    elif traffic_level == "Heavy":
        return {
            'red': random.randint(30, 45),
            'green': random.randint(15, 25),
            'yellow': YELLOW_DURATION
        }
    else:
        return {
            'red': random.randint(45, 60),
            'green': random.randint(10, 20),
            'yellow': YELLOW_DURATION
        }

# Create JSON data for the publisher based on the flow rate from the data generator
def create_data(flow_rate=None):
    global start_id
    
    if flow_rate is None:
        flow_rate = random.random()
    
    traffic_level = get_traffic_level(flow_rate)
    light_timings = calculate_light_timings(traffic_level)
    
    data = {
        'id': start_id,
        'timestamp': time.asctime(),
        'intersection': f"Intersection-{random.randint(1, 10)}",
        'vehicle_count': random.randint(5, 50),
        'avg_speed': round(random.uniform(20, 60), 1),
        'congestion_level': traffic_level,
        'traffic_lights': light_timings,
        'flow_rate': flow_rate
    }
    start_id += 1
    return data

# Print the data in a readable format for the publisher GUI
def print_data(data):
    print(f"\nTraffic Data ID: {data['id']}")
    print(f"Time: {data['timestamp']}")
    print(f"Intersection: {data['intersection']}")
    print(f"Vehicles Counted: {data['vehicle_count']}")
    print(f"Average Speed: {data['avg_speed']} km/h")
    print(f"Congestion: {data['congestion_level']}")
    print(f"Traffic Light Timings - Red: {data['traffic_lights']['red']}s, "
          f"Green: {data['traffic_lights']['green']}s, "
          f"Yellow: {YELLOW_DURATION}s")
    print('-' * 40)