# group_2_subscriber.py

import json
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
from group_2_display_gauge import TrafficGaugeDisplay
from group_2_display_bar import TrafficBarDisplay
from group_2_display_chart import TrafficFlowDisplay
from group_2_dynamic_chart import DynamicLineChart

BROKER = "localhost"
BASE_TOPIC = "traffic/flow/group2"

class TrafficSubscriber:
    def __init__(self, root, subscriber_id=1):
        self.root = root
        self.subscriber_id = subscriber_id
        self.current_publisher = "all"
        self.scale_factor = 0.9
        self.root.tk.call('tk', 'scaling', self.scale_factor * self.root.tk.call('tk', 'scaling'))
        
        # Initialize MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.last_ids = {}
        self.missing_packets = 0
        self.active_publishers = set()
        self.first_message_received = False
        self.last_processed_id = None
        
        # Configure root grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        
        # Initialize displays
        self.initialize_displays()
        
        # Publisher selection frame
        self.pub_select_frame = ttk.Frame(root)
        self.pub_select_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(self.pub_select_frame, text="Select Publisher:").pack(side=tk.LEFT)
        
        # Publisher selection radio buttons
        self.pub_var = tk.StringVar(value="all")
        self.pub_options = ["all", "publisher1", "publisher2", "publisher3"]
        
        for option in self.pub_options:
            ttk.Radiobutton(
                self.pub_select_frame,
                text=option.capitalize(),
                variable=self.pub_var,
                value=option,
                command=self.change_publisher
            ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.congestion_label = ttk.Label(
            root,
            text="Current Congestion: Unknown",
            font=("Arial", int(12 * self.scale_factor), "bold")
        )
        self.congestion_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Make the window resizable
        root.minsize(int(900 * self.scale_factor), int(900 * self.scale_factor))
        root.geometry(f"{int(900 * self.scale_factor)}x{int(900 * self.scale_factor)}")
        root.title(f"Traffic Subscriber {self.subscriber_id}")

    # Function to clear GUIs when switching publishers    
    def initialize_displays(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) < 2:
                widget.grid_forget()
        
        # Top-left: Gauge
        self.gauge = TrafficGaugeDisplay(self.root)
        self.gauge.frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Top-right: Bar
        self.bar = TrafficBarDisplay(self.root)
        self.bar.frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Bottom-left: Display Chart
        self.chart = TrafficFlowDisplay(self.root)
        self.chart.frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Bottom-right: Dynamic Chart
        self.dynamic_chart = DynamicLineChart(self.root)
        self.dynamic_chart.frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    
    # Handle publisher selection from UI
    def change_publisher(self):
        new_publisher = self.pub_var.get()
        
        if new_publisher != self.current_publisher:
            self.current_publisher = new_publisher
            print(f"Subscriber {self.subscriber_id} switched to {self.current_publisher}")
            self.initialize_displays()
            
            # Update active publishers based on selection
            if self.current_publisher == "all":
                self.active_publishers = {"publisher1", "publisher2", "publisher3"}
            else:
                self.active_publishers = {self.current_publisher}
            
            # Reset last IDs and missing packets (else errors DO occur)
            self.last_ids = {int(pub[-1]): None for pub in self.active_publishers}
            self.first_message_received = False
            self.last_processed_id = None
            
            # Reset congestion label
            self.congestion_label.config(text="Current Congestion: Unknown", foreground="black")

    # MQTT connection and message handling
    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Subscriber {self.subscriber_id} connected with result code {reason_code}")
        # Subscribe to all topics
        client.subscribe(f"{BASE_TOPIC}/all")
        client.subscribe(f"{BASE_TOPIC}/publisher1")
        client.subscribe(f"{BASE_TOPIC}/publisher2")
        client.subscribe(f"{BASE_TOPIC}/publisher3")

    # Handle incoming messages
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            publisher_id = data.get('publisher_id', 0)
            topic_publisher = msg.topic.split('/')[-1]
            
            # Skip duplicate messages (same ID from same publisher)
            if self.last_processed_id == data['id'] and publisher_id in self.last_ids:
                return
                
            # Determine if this message should be processed based on current selection
            should_process = (
                (self.current_publisher == "all" and topic_publisher == "all") or
                (self.current_publisher != "all" and f"publisher{publisher_id}" == self.current_publisher)
            )
            # Skip messages not from the selected publisher
            if not should_process:
                return
                
            # Initialize last_id tracking for this publisher so we can track missing packets now that we have switched
            if publisher_id not in self.last_ids:
                self.last_ids[publisher_id] = data['id']
                self.last_processed_id = data['id']
                return
            
            # Only check for missing packets after first message
            if self.first_message_received:
                expected_id = self.last_ids[publisher_id] + 1
                if data['id'] > expected_id:
                    missing = data['id'] - expected_id
                    self.missing_packets += missing
                    print(f"Subscriber {self.subscriber_id}: Missing {missing} packets from publisher {publisher_id}! Last: {self.last_ids[publisher_id]}, Current: {data['id']}")
                    # Update the label to show missing packets on the UI
                    self.congestion_label.config(
                        text=f"Missing {missing} packets from publisher {publisher_id}!",
                        foreground="orange"
                    )
                    self.root.after(2000, self.reset_congestion_label)
            # Update the last ID for this publisher
            self.last_ids[publisher_id] = data['id']
            self.last_processed_id = data['id']
            self.first_message_received = True
            # If the publisher ID is not in the active publishers, skip processing
            if not self.validate_data(data):
                return
            # Else we can process the data    
            congestion_level = data['congestion_level']
            flow = data['flow_rate']
            
            # And update the UI with the new data
            color = self.get_congestion_color(congestion_level)
            self.congestion_label.config(
                text=f"Current Congestion: {congestion_level} (Publisher {publisher_id})",
                foreground=color
            )
            self.gauge.update_from_mqtt(flow)
            self.chart.update_from_mqtt(flow)
            self.bar.update_from_mqtt(flow)
            self.dynamic_chart.update_from_mqtt(flow)
            
        except Exception as e:
            print(f"Subscriber {self.subscriber_id} error processing message: {str(e)}")

    # Validate data to check for wild values
    def validate_data(self, data):
        flow_rate = data.get('flow_rate', 0)
        if not 0 <= flow_rate <= 1:
            print(f"Subscriber {self.subscriber_id}: Wild data detected: {flow_rate}")
            self.congestion_label.config(
                text=f"Wild Data Detected. Please wait for next update.",
                foreground="red"
            )
            self.root.after(1500, self.clear_warning)
            return False
        return True

    # Clear warning messages after a delay
    def clear_warning(self):
        self.congestion_label.config(
            text="Current Congestion: Unknown",
            foreground="black"
        )

    # Reset congestion label after a delay
    def reset_congestion_label(self):
        if self.congestion_label['foreground'] == "orange":
            self.congestion_label.config(
                text="Current Congestion: Unknown",
                foreground="black"
            )
    # Get color based on congestion level
    def get_congestion_color(self, level):
        colors = {
            "Low": "green",
            "Moderate": "yellow",
            "Heavy": "orange",
            "Severe": "red"
        }
        return colors.get(level, "black")
        
    # Start the MQTT client
    def start(self):
        self.client.connect(BROKER, 1883, 60)
        print(f"Subscriber {self.subscriber_id} connecting to broker...")
        self.client.loop_start()

if __name__ == "__main__":
    import sys
    subscriber_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    root = tk.Tk()
    subscriber = TrafficSubscriber(root, subscriber_id)
    subscriber.start()
    
    root.mainloop()