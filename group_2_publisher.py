# group_2_publisher.py

import json
import time
import paho.mqtt.client as mqtt
from group_2_util import create_data
from group_2_data_generator import TrafficFlowSensor
import random
import tkinter as tk
from tkinter import ttk
import threading

class TrafficPublisher:
    # Init publisher with default values
    def __init__(self, publisher_id=1):
        self.publisher_id = publisher_id
        self.client = mqtt.Client()
        self.sensor = TrafficFlowSensor()
        self.running = True
        self.block_skip_active = False
        self.block_skip_remaining = 0
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title(f"Traffic Publisher {self.publisher_id} Control")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Init default values for sliders
        self.publish_interval = tk.DoubleVar(value=2.0)
        self.skip_prob = tk.DoubleVar(value=1.0)
        self.wild_prob = tk.DoubleVar(value=0.5)
        self.block_skip_prob = tk.DoubleVar(value=0.2)
        self.block_skip_duration = tk.IntVar(value=5)
        
        self.setup_gui()
        self.connect()
        
        # Start the publishing thread 
        self.publish_thread = threading.Thread(target=self.publish_data, daemon=True)
        self.publish_thread.start()

    def setup_gui(self):
        # Parameter Control Frame
        control_frame = ttk.LabelFrame(self.root, text=f"Publisher {self.publisher_id} Controls", padding=10)
        control_frame.pack(padx=10, pady=10, fill=tk.X)

        # Interval Control
        ttk.Label(control_frame, text="Publish Interval (0.5-10s):").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=0.5, to=10, variable=self.publish_interval,
                 command=lambda v: self.interval_label.config(text=f"{float(v):.1f}s")).grid(row=0, column=1, sticky=tk.EW)
        self.interval_label = ttk.Label(control_frame, text=f"{self.publish_interval.get():.1f}s")
        self.interval_label.grid(row=0, column=2)

        # Skip Probability
        ttk.Label(control_frame, text="Skip Probability (0-5%):").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=0, to=5, variable=self.skip_prob,
                 command=lambda v: self.skip_label.config(text=f"{float(v):.1f}%")).grid(row=1, column=1, sticky=tk.EW)
        self.skip_label = ttk.Label(control_frame, text=f"{self.skip_prob.get():.1f}%")
        self.skip_label.grid(row=1, column=2)

        # Wild Data Probability
        ttk.Label(control_frame, text="Wild Data Probability (0-2%):").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=0, to=2, variable=self.wild_prob,
                 command=lambda v: self.wild_label.config(text=f"{float(v):.2f}%")).grid(row=2, column=1, sticky=tk.EW)
        self.wild_label = ttk.Label(control_frame, text=f"{self.wild_prob.get():.2f}%")
        self.wild_label.grid(row=2, column=2)

        # Block Skip Probability
        ttk.Label(control_frame, text="Block Skip Probability (0-1%):").grid(row=3, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=0, to=1, variable=self.block_skip_prob,
                 command=lambda v: self.block_skip_label.config(text=f"{float(v):.2f}%")).grid(row=3, column=1, sticky=tk.EW)
        self.block_skip_label = ttk.Label(control_frame, text=f"{self.block_skip_prob.get():.2f}%")
        self.block_skip_label.grid(row=3, column=2)

        # Block Skip Duration
        ttk.Label(control_frame, text="Block Skip Duration (1-10):").grid(row=4, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=1, to=10, variable=self.block_skip_duration,
                 command=lambda v: self.block_duration_label.config(text=f"{int(float(v))}")).grid(row=4, column=1, sticky=tk.EW)
        self.block_duration_label = ttk.Label(control_frame, text=f"{self.block_skip_duration.get()}")
        self.block_duration_label.grid(row=4, column=2)

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Publication Status", padding=10)
        status_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=10, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)

    # Connect to MQTT broker
    def connect(self):
        self.client.connect("localhost", 1883, 60)
        self.log_status("Connected to MQTT broker")

    # Send status messages to the GUI
    def log_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    # Publish data to the MQTT broker
    # Runs in a separate thread to avoid blocking the GUI
    def publish_data(self):
        try:
            while self.running:
                # Get current values from sliders
                current_interval = self.publish_interval.get()
                current_skip_prob = self.skip_prob.get() / 100
                current_wild_prob = self.wild_prob.get() / 100
                current_block_skip_prob = self.block_skip_prob.get() / 100
                current_block_duration = self.block_skip_duration.get()
                
                # Update data generator parameters 
                self.sensor.wild_prob = current_wild_prob

                # Handle block skipping
                if self.block_skip_active:
                    self.block_skip_remaining -= 1
                    if self.block_skip_remaining <= 0:
                        self.block_skip_active = False
                    self.log_status(f"BLOCK SKIP ACTIVE ({self.block_skip_remaining} remaining)")
                    time.sleep(current_interval)
                    continue
                # Check if we should start a block skip
                elif random.random() < current_block_skip_prob:
                    self.block_skip_active = True
                    self.block_skip_remaining = current_block_duration
                    self.log_status(f"BLOCK SKIP TRIGGERED! Skipping next {current_block_duration} transmissions")
                    continue
                # Check if we should skip this transmission
                if random.random() < current_skip_prob:
                    self.log_status(f"SKIPPED transmission ({current_skip_prob*100:.1f}% chance)")
                else:
                    flow_value = self.sensor.generate_value()
                    payload = create_data(flow_value)
                    
                    if not (0 <= flow_value <= 1):
                        self.log_status(f"WILD DATA GENERATED: {flow_value:.2f}")
                    
                    # Send relevant data to MQTT broker for subscribers
                    payload['flow_rate'] = flow_value
                    payload['publisher_id'] = self.publisher_id
                    json_data = json.dumps(payload)
                    
                    # Publish to unique topic for this publisher and a common topic for all publishers
                    self.client.publish(f"traffic/flow/group2/publisher{self.publisher_id}", json_data)
                    self.client.publish("traffic/flow/group2/all", json_data)
                    self.log_status(f"Published: {json_data}")
                
                time.sleep(current_interval)
        except Exception as e:
            self.log_status(f"Error in publish thread: {str(e)}")
        finally:
            self.client.disconnect()
            self.log_status("Disconnected from broker")

    # Close the GUI and stop the publisher
    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    import sys
    publisher_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    publisher = TrafficPublisher(publisher_id)
    publisher.root.mainloop()