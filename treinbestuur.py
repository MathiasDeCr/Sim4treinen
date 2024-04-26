import serial
import tkinter as tk
from tkinter import ttk

# Verander de poort naar de poort waarop je Arduino is aangesloten
SERIAL_PORT = 'COM4'  # Bijvoorbeeld '/dev/ttyUSB0' op Linux of 'COM3' op Windows
BAUD_RATE = 9600

# Maak een seriële verbinding met de Arduino
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Functies om de verschillende knoppen te behandelen
def send_command(command):
    ser.write(command.encode())

def button_right():
    send_command('R')

def button_left():
    send_command('L')

def button_full():
    send_command('F')

def button_180():
    send_command('A')

# GUI-venster
root = tk.Tk()
root.title("Arduino Motor Control")

# Stijl voor de knoppen
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12))

# Frames voor het centreren van knoppen
frame_btn = tk.Frame(root)
frame_btn.pack(pady=20)

# Knoppen
btn_right = ttk.Button(frame_btn, text="Right", command=button_right)
btn_right.grid(row=0, column=0, padx=10)

btn_left = ttk.Button(frame_btn, text="Left", command=button_left)
btn_left.grid(row=0, column=1, padx=10)

btn_full = ttk.Button(frame_btn, text="terug naar nul", command=button_full)
btn_full.grid(row=0, column=2, padx=10)

btn_180 = ttk.Button(frame_btn, text="180", command=button_180)
btn_180.grid(row=0, column=3, padx=10)

# Start GUI-loop
root.mainloop()
