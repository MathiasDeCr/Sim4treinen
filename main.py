import socket
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyodbc
import pandas as pd
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import threading
import time

motor_control_enabled = False
accepted_uid_detected = False
command_enabled_time = None

# IP adres arduino en poort waar alles wordt doorgestuurd
ARDUINO_IP = '10.6.121.159'
ARDUINO_PORT = 80

# Verbinding maken database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\KDG\sim4\Database11.accdb;'
)
cursor = conn.cursor()

# Initialiseer canvas variabele
canvas = None

# Haal info uit database om in grafiek te steken
def fetch_data():
    query = "SELECT train_name, current_time FROM treininfo"
    df = pd.read_sql(query, conn)
    return df

# Code voor grafiek te maken
def draw_graph():
    global canvas
    df = fetch_data()
    df['current_time'] = pd.to_datetime(df['current_time'])
    df['hour'] = df['current_time'].dt.hour

    # Groepeer per uur
    trains_per_hour = df.groupby('hour').size()

    figure = plt.Figure(figsize=(10, 6), dpi=100)
    ax = figure.add_subplot(111)
    trains_per_hour.plot(kind='line', ax=ax, marker='o')
    ax.set_title('Aantal treinen per uur')
    ax.set_xlabel('Uur')
    ax.set_ylabel('Aantal treinen')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    if canvas:
        canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(figure, frame_graph)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Update grafiek en treinlijst om de zoveel seconden
def update_data():
    global command_enabled_time
    draw_graph()
    update_train_list()

    # Controleer of de periode van 15 seconden voorbij is
    if accepted_uid_detected and time.time() > command_enabled_time:
        send_command('F')  # Stuur het "terug naar nul" commando naar de Arduino
        command_enabled_time = None  # Reset de command_enabled_time

    # Plan de volgende update
    root.after(30000, update_data)



# Maak de window aan voor de knoppen
root = tk.Tk()
root.title("Arduino Motor Control")

frame_btn = tk.Frame(root)
frame_btn.pack(pady=20)

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12))

# Functies voor motorbesturing
def button_right():
    if accepted_uid_detected and time.time() < command_enabled_time:
        send_command('R')

def button_left():
    if accepted_uid_detected and time.time() < command_enabled_time:
        send_command('L')

def button_full():
    if accepted_uid_detected and time.time() < command_enabled_time:
        send_command('F')

def button_180():
    if accepted_uid_detected and time.time() < command_enabled_time:
        send_command('A')

# Functies voor communicatie met de Arduino
def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ARDUINO_IP, ARDUINO_PORT))
        s.sendall(command.encode())

# Knoppen voor motorbesturing
btn_right = ttk.Button(frame_btn, text="Right", command=button_right)
btn_right.grid(row=0, column=0, padx=10)

btn_left = ttk.Button(frame_btn, text="Left", command=button_left)
btn_left.grid(row=0, column=1, padx=10)

btn_full = ttk.Button(frame_btn, text="terug naar nul", command=button_full)
btn_full.grid(row=0, column=2, padx=10)

btn_180 = ttk.Button(frame_btn, text="180", command=button_180)
btn_180.grid(row=0, column=3, padx=10)

# Frame voor grafiek en treinenlijst
frame_graph = tk.Frame(root)
frame_graph.pack(pady=20, fill=tk.BOTH, expand=True)

btn_draw_graph = ttk.Button(root, text="Toon Grafiek", command=draw_graph)
btn_draw_graph.pack(pady=20)

train_list = tk.Listbox(frame_graph, width=40, height=20)
train_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Haal treininfo uit database en update de lijstwidget
def update_train_list():
    train_list.delete(0, tk.END)
    df = fetch_data()
    for index, row in df.iterrows():
        train_list.insert(tk.END, f"{row['train_name']} - {row['current_time']}")

# Geaccepteerde UID's en treinen ophalen voor identificatie
def get_accepted_uids():
    cursor.execute("SELECT uid, train_model FROM accepted_uids")
    rows = cursor.fetchall()
    accepted_uids = {bytes.fromhex(row.uid): row.train_model for row in rows}
    return accepted_uids

accepted_uids = get_accepted_uids()

# Stuurt geaccepteerde data naar database
def write_to_database(uid, uid_length, train_name, current_time):
    cursor.execute("INSERT INTO treininfo (uid, uid_length, train_name, current_time) VALUES (?, ?, ?, ?)",
                   (uid, uid_length, train_name, current_time))
    conn.commit()

# Functie voor het afhandelen van clientverbindingen
def handle_client_connection(clientsocket, address):
    global accepted_uid_detected, command_enabled_time
    print(f"Connection from {address} has been established.")

    uid_string = clientsocket.recv(1024).strip().decode('utf-8')
    uid_value = bytes.fromhex(uid_string)
    uid_length = len(uid_value)

    if uid_length == 4 and uid_value in accepted_uids:
        train_name = accepted_uids[uid_value]
        current_time = datetime.now()
        print("Accepted UID! This is train:", train_name)
        write_to_database(uid_value.hex().upper(), uid_length, train_name, current_time)
        accepted_uid_detected = True
        command_enabled_time = time.time() + 10  # 30-seconden periode
    else:
        print("Unauthorized card or UID has invalid length.")

    clientsocket.close()

# Functie voor het accepteren van verbindingen
def accept_connections():
    while True:
        clientsocket, address = s.accept()
        handle_client_connection(clientsocket, address)

# Maak een socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind de socket aan het juiste IP-adres en poort
s.bind(('0.0.0.0', 80))
# Luister naar verbindingen
s.listen(5)

# Start een thread om verbindingen te accepteren
threading.Thread(target=accept_connections, daemon=True).start()
# Start een thread om de GUI bij te werken
threading.Thread(target=update_data, daemon=True).start()

root.mainloop()
