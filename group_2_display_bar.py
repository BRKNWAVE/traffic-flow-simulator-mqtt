# group_2_display_bar.py

import tkinter as tk
from tkinter import ttk, Canvas

class TrafficBarDisplay:
    # Init the GUI as a child of the subscriber so we can pack it with the rest of the GUI
    # Also removed all the old elements related to manual input and random values as we get those from MQTT.
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.value = 0.5
        self.target_value = self.value

        self.canvas = Canvas(self.frame, width=360, height=100, bg="#23272a", 
                           bd=2, relief="ridge", highlightbackground="#99aab5")
        self.canvas.grid(row=0, column=0, pady=15, sticky="nsew")
        
        self.label = ttk.Label(self.frame, text=f"Traffic Flow: {self.value:.2f}")
        self.label.grid(row=1, column=0)
        
        self.traffic_label = ttk.Label(self.frame, 
                                     text=self.get_traffic_label(self.value), 
                                     font=("Arial", 12, "bold"))
        self.traffic_label.grid(row=2, column=0)
        
        # Configure grid weights for grid packing
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        self.draw_bar()

    # Get the traffic label based on the value (unchanged)
    def get_traffic_label(self, value):
        if value <= 0.25:
            return "Low Traffic"
        elif value <= 0.5:
            return "Moderate Traffic"
        elif value <= 0.75:
            return "Heavy Traffic"
        else:
            return "Severe Traffic"

    # Get the color based on the value (unchanged)
    def get_bar_color(self, value):
        if value <= 0.25:
            return "green"
        elif value <= 0.5:
            return "yellow"
        elif value <= 0.75:
            return "orange"
        else:
            return "red"
    
    # Draw the bar with the current value.
    def draw_bar(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(10, 35, 350, 75, fill="#3a3e42", outline="black", width=2)
        bar_width = int(self.value * 340)
        bar_color = self.get_bar_color(self.value)
        self.canvas.create_rectangle(10, 35, 10 + bar_width, 75, fill=bar_color, outline="")
        self.canvas.create_text(175, 20, text="Live Traffic Flow", font=("Arial", 10), fill="#99aab5")

    # Update the bar from MQTT (not a random value anymore)
    def update_from_mqtt(self, value):
        self.target_value = value
        self.animate_bar()

    # Animate bar to the target value
    def animate_bar(self):
        step = (self.target_value - self.value) / 10
        if abs(self.value - self.target_value) > 0.00:
            self.value += step
            self.label.config(text=f"Traffic Flow: {self.value:.2f}")
            self.traffic_label.config(text=self.get_traffic_label(self.value))
            self.draw_bar()
            self.frame.after(50, self.animate_bar)
        else:
            self.value = self.target_value
            self.draw_bar()