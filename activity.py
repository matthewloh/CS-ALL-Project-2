import tkinter as tk
import random

class HardwareOfTheDay:
    def __init__(self, root):
        self.root = root
        self.hardware_list = [
            "CPU",
            "GPU",
            "RAM",
            "SSD",
            "Motherboard",
            "Power Supply",
            "Monitor",
            "Keyboard",
            "Mouse",
            "Headphones"
        ]

        self.hardware_label = tk.Label(self.root, text="Hardware of the Day", font=("Helvetica", 24))
        self.hardware_label.pack(pady=20)

        self.random_hardware()

        self.change_button = tk.Button(self.root, text="Next", command=self.random_hardware)
        self.change_button.pack(pady=10)

    def random_hardware(self):
        random_hardware = random.choice(self.hardware_list)
        self.hardware_label.config(text=random_hardware)

# Create the main window
root = tk.Tk()
root.title("Hardware of the Day")

# Create an instance of the HardwareOfTheDay class
activity = HardwareOfTheDay(root)

# Start the Tkinter event loop
root.mainloop()