# group_2_display_gauge.py

import tkinter as tk
from tkinter import Canvas, ttk
import math

class TrafficGaugeDisplay:
    # Init the GUI as a child of the subscriber so we can pack it with the rest of the GUI
    # Also removed all the old elements related to manual input and random values as we get those from MQTT.
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.value = 50
        
        self.inner_frame = tk.Frame(self.frame, bg="#333", bd=10, relief=tk.RIDGE)
        self.inner_frame.grid(row=0, column=0, sticky="nsew")
        
        self.canvas = Canvas(self.inner_frame, width=350, height=350, bg='#222', highlightthickness=0)
        self.canvas.grid(row=0, column=0, pady=20, sticky="nsew")
        
        self.label = tk.Label(self.inner_frame, 
                            text=f"Traffic Flow: {self.value}%", 
                            font=("Arial", 16, "bold"), 
                            bg="#333", 
                            fg="white")
        self.label.grid(row=1, column=0)
        
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.inner_frame.columnconfigure(0, weight=1)
        self.inner_frame.rowconfigure(0, weight=1)
        
        self.draw_gauge()
    
    def draw_gauge(self):
        self.canvas.delete("all")
        center_x, center_y, radius = 175, 175, 120
        start_angle = 130
        end_angle = 410
        
        self.canvas.create_rectangle(20, 20, 330, 330, outline="gray", width=4)
        
        for i in range(3):
            color = ["#4CAF50", "#FFC107", "#F44336"][i]
            self.canvas.create_arc(40, 40, 310, 310, 
                                  start=start_angle + i*90, 
                                  extent=90, 
                                  style=tk.ARC, 
                                  width=15, 
                                  outline=color)
        
        labels = [("Low", start_angle), ("Medium", start_angle + 90), ("High", start_angle + 180)]
        for text, angle in labels:
            rad = math.radians(angle + 45)
            x = center_x + (radius - 30) * math.cos(rad)
            y = center_y - (radius - 30) * math.sin(rad)
            self.canvas.create_text(x, y, 
                                  text=text, 
                                  font=("Arial", 12, "bold"), 
                                  fill="white")
        
        angle = start_angle + ((self.value / 100) * (end_angle - start_angle))
        rad = math.radians(angle)
        x = center_x + radius * math.cos(rad)
        y = center_y - radius * math.sin(rad)
        
        self.canvas.create_line(center_x, center_y, x, y, width=5, fill='black')
        self.canvas.create_oval(center_x-7, center_y-7, center_x+7, center_y+7, fill='black')

    def update_from_mqtt(self, value):
        self.value = value * 100
        self.label.config(text=f"Traffic Flow: {self.value:.1f}%")
        self.draw_gauge()