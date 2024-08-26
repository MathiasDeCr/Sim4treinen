import socket
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyodbc
import pandas as pd
from matplotlib.ticker import MaxNLocator
from datetime import datetime, timedelta
import threading
import time
from login import login

motor_control_enabled = False
accepted_uid_detected = False
command_enabled_time = None
last_chosen_direction = None  # Bewaar de laatst gekozen richting

# Configurations
config = {
    'ARDUINO_IP': 'arduinip',
    'ARDUINO_PORT': 80,
    'auto_mode': True,
    'graph_update_interval': 30000,
    'database_path': r'C:\KDG\sim4\Database11.accdb'
}

# Verbinding maken met de database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + config['database_path'] + ';'
)
cursor = conn.cursor()

# Initialiseer canvas variabele
canvas = None

# Haal info uit de database om in de grafiek te zetten
def fetch_data():
    query = "SELECT train_name, current_time, direction FROM treininfo"
    df = pd.read_sql(query, conn)
    df['current_time'] = pd.to_datetime(df['current_time'])
    last_24_hours = datetime.now() - timedelta(hours=24)
    df = df[df['current_time'] >= last_24_hours]
    return df

def main_app(username, user_id):
    global frame_graph, tree, lbl_status, auto_mode_toggle, lbl_auto_mode_status

    root.title("Arduino Motor Control")
    root.attributes('-fullscreen', True)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('TLabel', font=('Helvetica', 12))

    frame_btn = ttk.Frame(root, padding="10")
    frame_btn.pack(pady=20, fill=tk.X)

    def show_welcome_message():
        lbl_welcome = ttk.Label(root, text=f"Welkom, {username}!", font=("Helvetica", 16))
        lbl_welcome.pack(pady=10)
        root.after(3000, lbl_welcome.destroy)  # Verwijder het bericht na 3 seconden

    show_welcome_message()

    # Commando's voor de motor
    def button_right():
        if accepted_uid_detected and time.time() < command_enabled_time:
            print("Button Right Pressed")
            set_button_state(btn_right, "busy")
            send_command('R')
            lbl_status.config(text="Beweging: Rechts")
            root.after(3000, lambda: set_button_state(btn_right, "normal"))
            global last_chosen_direction
            last_chosen_direction = "Rechts"

    def button_left():
        if accepted_uid_detected and time.time() < command_enabled_time:
            print("Button Left Pressed")
            set_button_state(btn_left, "busy")
            send_command('L')
            lbl_status.config(text="Beweging: Links")
            root.after(3000, lambda: set_button_state(btn_left, "normal"))
            global last_chosen_direction
            last_chosen_direction = "Links"

    def button_full():
        if accepted_uid_detected and time.time() < command_enabled_time:
            print("Button Full Pressed")
            set_button_state(btn_full, "busy")
            send_command('F')
            lbl_status.config(text="Beweging: Terug naar nul")
            root.after(3000, lambda: set_button_state(btn_full, "normal"))
            global last_chosen_direction
            last_chosen_direction = "Terug naar nul"

    def button_180():
        if accepted_uid_detected and time.time() < command_enabled_time:
            print("Button 180 Pressed")
            set_button_state(btn_180, "busy")
            send_command('A')
            lbl_status.config(text="Beweging: 180 graden")
            root.after(3000, lambda: set_button_state(btn_180, "normal"))
            global last_chosen_direction
            last_chosen_direction = "180 graden"

    # Praten met de Arduino
    def send_command(command):
        print(f"Sending command to Arduino: {command}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((config['ARDUINO_IP'], config['ARDUINO_PORT']))
            s.sendall(command.encode())

    # Knoppen voor de motor
    global btn_right, btn_left, btn_full, btn_180

    btn_right = ttk.Button(frame_btn, text="Rechts", command=button_right)
    btn_right.grid(row=0, column=0, padx=10)

    btn_left = ttk.Button(frame_btn, text="Links", command=button_left)
    btn_left.grid(row=0, column=1, padx=10)

    btn_full = ttk.Button(frame_btn, text="Terug naar nul", command=button_full)
    btn_full.grid(row=0, column=2, padx=10)

    btn_180 = ttk.Button(frame_btn, text="180 graden", command=button_180)
    btn_180.grid(row=0, column=3, padx=10)

    # Grafiek en treinlijst
    frame_graph = ttk.Frame(root, padding="10")
    frame_graph.pack(pady=20, fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame_graph, columns=("Train Name", "Current Time", "Direction"), show='headings')
    tree.heading("Train Name", text="Train Name")
    tree.heading("Current Time", text="Current Time")
    tree.heading("Direction", text="Direction")
    tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    lbl_status = ttk.Label(root, text="Status: Wachtend op commando's")
    lbl_status.pack(pady=20)

    lbl_auto_mode_status = ttk.Label(root, text="Automatische modus is Aan" if config['auto_mode'] else "Automatische modus is Uit")
    lbl_auto_mode_status.pack(pady=10)

    def update_auto_mode_status(status):
        lbl_auto_mode_status.config(text="Automatische modus is Aan" if status else "Automatische modus is Uit")
        config['auto_mode'] = status

    def update_train_list():
        print("Updating train list")
        for row in tree.get_children():
            tree.delete(row)
        df = fetch_data()
        for index, row in df.iterrows():
            tree.insert("", tk.END, values=(row['train_name'], row['current_time'], row['direction']))

    def draw_graph():
        global canvas
        print("Drawing graph")
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

    def update_data():
        global command_enabled_time
        print("Updating data")
        draw_graph()
        update_train_list()

        print(f"accepted_uid_detected: {accepted_uid_detected}")
        print(f"current_time: {time.time()}, command_enabled_time: {command_enabled_time}")
        print(f"last_chosen_direction: {last_chosen_direction}")
        print(f"auto_mode_toggle: {config['auto_mode']}")

        # Controleer of de periode van 15 seconden voorbij is en command_enabled_time niet None is
        if accepted_uid_detected and command_enabled_time is not None and time.time() > command_enabled_time:
            if last_chosen_direction not in ["Terug naar nul", None, "vooruit", "rechtdoor"]:
                print("15 seconds period is over. Sending 'F' command.")
                send_command('F')
                lbl_status.config(text="Gaat naar originele positie")
                root.after(5000, reset_status_message)
            else:
                print(
                    "Skipping 'F' command due to last chosen direction being 'Terug naar nul', None, 'vooruit', or 'rechtdoor'.")
                lbl_status.config(text="Status: Wachtend op commando's")
            command_enabled_time = None  # Reset de command_enabled_time
        else:
            print("Condition not met: Either accepted_uid_detected is False or the time period is not over.")

        root.after(config['graph_update_interval'], update_data)

    def reset_status_message():
        print("Resetting status message")
        lbl_status.config(text="Status: Wachtend op commando's")

    def get_accepted_uids():
        print("Fetching accepted UIDs from database")
        cursor.execute("SELECT uid, train_model, direction FROM accepted_uids")
        rows = cursor.fetchall()
        accepted_uids = {bytes.fromhex(row.uid): (row.train_model, row.direction) for row in rows}
        return accepted_uids

    accepted_uids = get_accepted_uids()

    def write_to_database(uid, uid_length, train_name, current_time, direction, user_id):
        global last_chosen_direction
        print("Writing data to database")

        # Zoek het id van de bijbehorende accepted_uid
        cursor.execute("SELECT id FROM accepted_uids WHERE uid = ?", uid.upper())
        accepted_uid_row = cursor.fetchone()

        if accepted_uid_row:
            accepted_uid_id = accepted_uid_row.id

            if direction == "vooruit":
                direction = "No direction set"

            print(
                f"Writing to database: UID={uid}, UID Length={uid_length}, Train Name={train_name}, Current Time={current_time}, Direction={direction}, User ID={user_id}, Accepted UID ID={accepted_uid_id}")

            cursor.execute(
                "INSERT INTO treininfo (uid, uid_length, train_name, current_time, direction, user_id, accepted_uid_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                uid.upper(), uid_length, train_name, current_time, direction, user_id, accepted_uid_id
            )
            conn.commit()
            update_data()  # Update data na schrijven naar database
            last_chosen_direction = None  # Reset last_chosen_direction naar None
        else:
            print(f"Error: UID {uid.upper()} not found in accepted_uids table.")

    def handle_client_connection(clientsocket, address, user_id):
        global accepted_uid_detected, command_enabled_time, last_chosen_direction
        print(f"Connection from {address} has been established.")

        uid_string = clientsocket.recv(1024).strip().decode('utf-8')
        uid_value = bytes.fromhex(uid_string)
        uid_length = len(uid_value)

        if uid_length == 4 and uid_value in accepted_uids:
            train_name, direction = accepted_uids[uid_value]
            current_time = datetime.now()
            print("Accepted UID! This is train:", train_name)
            accepted_uid_detected = True
            print({accepted_uid_detected})
            command_enabled_time = time.time() + 15  # 15-seconden periode
            lbl_status.config(text=f"Geaccepteerde trein: {train_name}")

            if config['auto_mode']:
                def send_auto_command():
                    time.sleep(5)
                    if direction == "links":
                        button_left()
                    elif direction == "rechts":
                        button_right()
                    elif direction == "180":
                        button_180()
                    elif direction == "vooruit":
                        button_full()

                threading.Thread(target=send_auto_command, daemon=True).start()

            # Wacht 15 seconden voordat we naar de database schrijven
                def delayed_database_write():
                    global accepted_uid_detected, last_chosen_direction
                    time.sleep(15)
                    # Als last_chosen_direction nog steeds None is, zet deze dan op "rechtdoor"
                    if last_chosen_direction is None:
                        last_chosen_direction = "rechtdoor"
                    write_to_database(uid_value.hex().upper(), uid_length, train_name, current_time,
                                      last_chosen_direction, user_id)
                    accepted_uid_detected = False  # Reset de accepted_uid_detected

                # Plan de vertraagde database schrijfoperatie om ervoor te zorgen dat update_data eerst wordt uitgevoerd
                root.after(100, lambda: threading.Thread(target=delayed_database_write, daemon=True).start())

            else:
                print("Unauthorized card or UID has invalid length.")
                lbl_status.config(text="Ongeldige UID")

            clientsocket.close()

    def accept_connections(user_id):
        while True:
            clientsocket, address = s.accept()
            handle_client_connection(clientsocket, address, user_id)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 80))

    s.listen(5)

    threading.Thread(target=accept_connections, args=(user_id,), daemon=True).start()
    threading.Thread(target=update_data, daemon=True).start()

    def set_button_state(button, state):
        if state == "busy":
            button.config(state=tk.DISABLED, style='Busy.TButton')
        else:
            button.config(state=tk.NORMAL, style='TButton')

    style.configure('TButton', background='lightblue', foreground='black')
    style.map('TButton', background=[('active', 'blue'), ('disabled', 'grey')])
    style.configure('Busy.TButton', background='orange', foreground='white')

    # programma sluiten
    def close_program():
        root.destroy()

    btn_close = ttk.Button(frame_btn, text="Afsluiten", command=close_program)
    btn_close.grid(row=0, column=5, padx=650)

    # Settings pagina openen
    def open_settings():
        settings_window = tk.Toplevel(root)
        settings_window.title("Instellingen")
        settings_window.geometry("400x600")

        ttk.Label(settings_window, text="Arduino IP:").pack(pady=10)
        ip_entry = ttk.Entry(settings_window)
        ip_entry.pack(pady=10)
        ip_entry.insert(0, config['ARDUINO_IP'])

        ttk.Label(settings_window, text="Grafiek Update Interval (ms):").pack(pady=10)
        interval_entry = ttk.Entry(settings_window)
        interval_entry.pack(pady=10)
        interval_entry.insert(0, config['graph_update_interval'])

        ttk.Label(settings_window, text="Database Pad:").pack(pady=10)
        db_path_entry = ttk.Entry(settings_window)
        db_path_entry.pack(pady=10)
        db_path_entry.insert(0, config['database_path'])

        auto_mode_var = tk.BooleanVar(value=config['auto_mode'])
        ttk.Checkbutton(settings_window, text="Automatische modus", variable=auto_mode_var).pack(pady=10)

        def save_settings():
            config['ARDUINO_IP'] = ip_entry.get()
            config['graph_update_interval'] = int(interval_entry.get())
            config['database_path'] = db_path_entry.get()

            update_auto_mode_status(auto_mode_var.get())

            # Sluit de bestaande databaseverbinding en maak een nieuwe verbinding
            global conn, cursor
            conn.close()
            conn = pyodbc.connect(
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ=' + config['database_path'] + ';'
            )
            cursor = conn.cursor()

            settings_window.destroy()

        ttk.Button(settings_window, text="Opslaan", command=save_settings).pack(pady=20)
        ttk.Button(settings_window, text="Annuleren", command=settings_window.destroy).pack(pady=10)

    btn_settings = ttk.Button(frame_btn, text="Instellingen", command=open_settings)
    btn_settings.grid(row=0, column=4, padx=10)

root = tk.Tk()
login(root, lambda username, user_id: main_app(username, user_id))
root.mainloop()
