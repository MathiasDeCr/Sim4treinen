import socket
import tkinter as tk
from tkinter import ttk, messagebox
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
ARDUINO_IP = '192.168.129.27'
ARDUINO_PORT = 80

# Verbinding maken database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=F:\Database11.accdb;'  # Gebruik het netwerkpad naar de gedeelde database
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
        lbl_status.config(text="Gaat naar originele positie")
        root.after(5000, reset_status_message)  # Reset de status na 5 seconden
        command_enabled_time = None  # Reset de command_enabled_time

    # Plan de volgende update
    root.after(30000, update_data)

# Helper functie om de status terug te zetten
def reset_status_message():
    lbl_status.config(text="Status: Wachtend op commando's")

# Maak de window aan voor de knoppen
root = tk.Tk()
root.title("Arduino Motor Control")

# Zet het venster in fullscreen modus
root.attributes('-fullscreen', True)

style = ttk.Style()
style.theme_use('clam')  # Gebruik een modern thema
style.configure('TButton', font=('Helvetica', 12), padding=10)
style.configure('TLabel', font=('Helvetica', 12))

frame_btn = ttk.Frame(root, padding="10")
frame_btn.pack(pady=20, fill=tk.X)

# Functies voor motorbesturing
def button_right():
    if accepted_uid_detected and time.time() < command_enabled_time:
        set_button_state(btn_right, "busy")
        send_command('R')
        lbl_status.config(text="Beweging: Rechts")
        root.after(3000, lambda: set_button_state(btn_right, "normal"))

def button_left():
    if accepted_uid_detected and time.time() < command_enabled_time:
        set_button_state(btn_left, "busy")
        send_command('L')
        lbl_status.config(text="Beweging: Links")
        root.after(3000, lambda: set_button_state(btn_left, "normal"))

def button_full():
    if accepted_uid_detected and time.time() < command_enabled_time:
        set_button_state(btn_full, "busy")
        send_command('F')
        lbl_status.config(text="Beweging: Terug naar nul")
        root.after(3000, lambda: set_button_state(btn_full, "normal"))

def button_180():
    if accepted_uid_detected and time.time() < command_enabled_time:
        set_button_state(btn_180, "busy")
        send_command('A')
        lbl_status.config(text="Beweging: 180 graden")
        root.after(3000, lambda: set_button_state(btn_180, "normal"))

# Functies voor communicatie met de Arduino
def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ARDUINO_IP, ARDUINO_PORT))
        s.sendall(command.encode())

# Knoppen voor motorbesturing
btn_right = ttk.Button(frame_btn, text="Rechts", command=button_right)
btn_right.grid(row=0, column=0, padx=10)

btn_left = ttk.Button(frame_btn, text="Links", command=button_left)
btn_left.grid(row=0, column=1, padx=10)

btn_full = ttk.Button(frame_btn, text="Terug naar nul", command=button_full)
btn_full.grid(row=0, column=2, padx=10)

btn_180 = ttk.Button(frame_btn, text="180 graden", command=button_180)
btn_180.grid(row=0, column=3, padx=10)

# Frame voor grafiek en treinenlijst
frame_graph = ttk.Frame(root, padding="10")
frame_graph.pack(pady=20, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_graph, columns=("Train Name", "Current Time"), show='headings')
tree.heading("Train Name", text="Train Name")
tree.heading("Current Time", text="Current Time")
tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Status label
lbl_status = ttk.Label(root, text="Status: Wachtend op commando's")
lbl_status.pack(pady=20)

# Haal treininfo uit database en update de lijstwidget
def update_train_list():
    for row in tree.get_children():
        tree.delete(row)
    df = fetch_data()
    for index, row in df.iterrows():
        tree.insert("", tk.END, values=(row['train_name'], row['current_time']))

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
        command_enabled_time = time.time() + 5  # 15-seconden periode
        lbl_status.config(text=f"Geaccepteerde trein: {train_name}")
    else:
        print("Unauthorized card or UID has invalid length.")
        lbl_status.config(text="Ongeldige UID")

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

# Helper functie om de knopstatus te wijzigen
def set_button_state(button, state):
    if state == "busy":
        button.config(state=tk.DISABLED, style='Busy.TButton')
    else:
        button.config(state=tk.NORMAL, style='TButton')

# Configureren van stijlen voor de knoppen
style.configure('TButton', background='lightblue', foreground='black')
style.map('TButton', background=[('active', 'blue'), ('disabled', 'grey')])
style.configure('Busy.TButton', background='orange', foreground='white')

# Functie om het programma te sluiten
def close_program():
    root.destroy()

# Knop om het programma te sluiten
btn_close = ttk.Button(frame_btn, text="Afsluiten", command=close_program)
btn_close.grid(row=0, column=4, padx=800)

root.mainloop()
