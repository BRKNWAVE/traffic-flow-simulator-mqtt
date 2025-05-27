import tkinter as tk
from tkinter import ttk, Canvas

class TrafficFlowDisplay:
    # Init the GUI as a child of the subscriber so we can pack it with the rest of the GUI
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.values = [0.0] * 10
        self.label = ttk.Label(self.frame, text="Traffic Flow Over Time", 
                             font=("Arial", 14))
        self.label.grid(row=0, column=0)
        
        self.canvas = Canvas(self.frame, width=450, height=300, bg='white')
        self.canvas.grid(row=1, column=0, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        self.draw_chart()

    # Get the color for the bar based on value.
    def get_color(self, value):
        if value <= 0.25:
            return "green"
        elif value <= 0.5:
            return "yellow"
        elif value <= 0.75:
            return "orange"
        else:
            return "red"

    # Draws the line chart.
    def draw_chart(self):
        self.canvas.delete("all")
        max_height = 100
        bar_width = 25

        for i, value in enumerate(self.values):
            value_scaled = max(0.0, min(1.0, value))
            height = int(value_scaled * max_height)

            x0 = 30 + i * (bar_width + 5)
            y0 = 200 - height
            x1 = x0 + bar_width
            y1 = 200

            color = self.get_color(value)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

            if i > 0:
                prev_x = 30 + (i - 1) * (bar_width + 5) + bar_width / 2
                prev_y = 200 - int(self.values[i - 1] * max_height)
                curr_x = x0 + bar_width / 2
                curr_y = y0
                self.canvas.create_line(prev_x, prev_y, curr_x, curr_y, fill="blue", width=2)

    # Added the update from MQTT method instead of random value
    def update_from_mqtt(self, value):
        self.values.append(value)
        self.values.pop(0)
        self.draw_chart()