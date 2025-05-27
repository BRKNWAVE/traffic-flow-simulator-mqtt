# group_2_dynamic_chart.py

import tkinter as tk
from tkinter import Canvas
import math

class DynamicLineChart:
    # Init the GUI as a child of the subscriber so we can pack it with the rest of the GUI
    # Also removed all the old elements related to manual input and random values as we get those from MQTT.
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        
        self.values = [0.5] * 20
        
        self.canvas = Canvas(self.frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.label = tk.Label(self.frame, text="Traffic Flow Over Time", font=("Arial", 14))
        self.label.pack()
        
        self.draw_chart()

    # Draw the line chart dynamically    
    def draw_chart(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if len(self.values) < 2 or width <= 1 or height <= 1:
            return
        
        max_value = max(self.values) if max(self.values) != min(self.values) else 1
        min_value = min(self.values)
        
        # Normalize values to stay within canvas
        normalized_values = []
        for val in self.values:
            if max_value == min_value:
                normalized = 0.5
            else:
                normalized = (val - min_value) / (max_value - min_value)
            normalized_values.append(height - (normalized * (height - 10)))
        
        step = width / (len(self.values) - 1)
        
        # Draw grid lines
        for i in range(0, width, 50):
            self.canvas.create_line(i, 0, i, height, fill='#f0f0f0')
        for i in range(0, height, 50):
            self.canvas.create_line(0, i, width, i, fill='#f0f0f0')
        
        # Draw the line
        for i in range(len(normalized_values) - 1):
            x1, y1 = i * step, normalized_values[i]
            x2, y2 = (i + 1) * step, normalized_values[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill='blue', width=2)
        
        # Draw min/max labels
        self.canvas.create_text(5, 10, text=f"{max_value:.2f}", anchor=tk.W, fill='red')
        self.canvas.create_text(5, height-10, text=f"{min_value:.2f}", anchor=tk.W, fill='green')
    
    # Update the chart using MQTT values
    def update_from_mqtt(self, value):
        self.values.pop(0)
        self.values.append(value)
        self.draw_chart()
    
    def on_close(self):
        self.frame.destroy()