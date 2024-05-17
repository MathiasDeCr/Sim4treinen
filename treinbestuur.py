import socket

# IP-adres en poort van de Arduino Uno R4 WiFi
ARDUINO_IP = '192.168.1.35'  # Vervang dit met het IP-adres van je Arduino
ARDUINO_PORT = 80

# Functie om commando's naar de Arduino te sturen via het netwerk
def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ARDUINO_IP, ARDUINO_PORT))
        s.sendall(command.encode())

# Functies voor het sturen van specifieke commando's
def button_right():
    send_command('R')

def button_left():
    send_command('L')

def button_full():
    send_command('F')

def button_180():
    send_command('A')

# Je kunt hier de rest van je GUI-code plaatsen

# Voorbeeld van GUI-code
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Arduino Motor Control")

frame_btn = tk.Frame(root)
frame_btn.pack(pady=20)

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12))

btn_right = ttk.Button(frame_btn, text="Right", command=button_right)
btn_right.grid(row=0, column=0, padx=10)

btn_left = ttk.Button(frame_btn, text="Left", command=button_left)
btn_left.grid(row=0, column=1, padx=10)

btn_full = ttk.Button(frame_btn, text="terug naar nul", command=button_full)
btn_full.grid(row=0, column=2, padx=10)

btn_180 = ttk.Button(frame_btn, text="180", command=button_180)
btn_180.grid(row=0, column=3, padx=10)

root.mainloop()
