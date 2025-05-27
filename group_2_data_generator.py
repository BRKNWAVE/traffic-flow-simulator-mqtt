# group_2_data_generator.py

import random
import matplotlib.pyplot as plt

class TrafficFlowSensor:
    # Init function (added wild data generation from original lab & adjusted parameters for better simulation)
    def __init__(self, min_value=0.0, max_value=1.0, mean=0.5, std_dev=0.25, delta=0.15, frequency=0.4, wild_prob=0.005):
        self.min_value = min_value
        self.max_value = max_value
        self.mean = mean
        self.std_dev = std_dev
        self.base = 0.5
        self.delta = delta
        self.frequency = frequency
        self.wild_prob = wild_prob

    # Generate a random value
    def generate_random(self):
        return random.gauss(self.mean, self.std_dev)

    # Generate a pattern of values
    def generate_pattern(self):
        if self.base < self.min_value or self.base > self.max_value:
            self.delta *= -1
        self.base += self.delta
        return self.base

    # Generate a value that has a chance of being wild data
    def generate_value(self):
        if random.random() < self.wild_prob:
            return random.choice([-999, 999, 1.5, -0.5])
        elif random.random() < self.frequency:
            return self.generate_pattern()
        else:
            return self.generate_random()

# Original Test Code

sensor = TrafficFlowSensor(min_value=0.0, max_value=1.0, mean=0.5, std_dev=0.1, delta=0.05, frequency=0.1)

number_of_values = 500
data = [sensor.generate_value() for _ in range(number_of_values)]