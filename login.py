import tkinter as tk
from tkinter import ttk
import pyodbc
import bcrypt
from datetime import datetime

# Verbinding maken met de database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\KDG\sim4\Database11.accdb;'
)
cursor = conn.cursor()

def get_user_by_username(username):
    cursor.execute("SELECT username, password_hash, name FROM users WHERE username = ?", username)
    return cursor.fetchone()

def add_user(username, password, name):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)",
                   (username, password_hash, name))
    conn.commit()

def get_user_id(username):
    cursor.execute("SELECT id FROM users WHERE username = ?", username)
    result = cursor.fetchone()
    return result[0] if result else None

def log_user_login(username):
    try:
        user_id = get_user_id(username)
        if user_id is None:
            print(f"User ID not found for username: {username}")
            return

        current_time = datetime.now()
        print(f"Logging login for user_id: {user_id} at {current_time}")
        cursor.execute("INSERT INTO login_history (user_id, login_time) VALUES (?, ?)", (user_id, current_time))
        conn.commit()
    except Exception as e:
        print(f"Error logging login: {e}")


def login(root, on_success):
    login_frame = ttk.Frame(root, padding="10")
    login_frame.pack(pady=20)

    def show_login_screen():
        clear_frame(login_frame)
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, pady=10)
        entry_username = ttk.Entry(login_frame)
        entry_username.grid(row=0, column=1, pady=10)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, pady=10)
        entry_password = ttk.Entry(login_frame, show='*')
        entry_password.grid(row=1, column=1, pady=10)

        lbl_login_status = ttk.Label(login_frame, text="")
        lbl_login_status.grid(row=3, column=0, columnspan=2)

        def check_login():
            username = entry_username.get()
            password = entry_password.get()

            user = get_user_by_username(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                login_frame.pack_forget()
                log_user_login(username)  # Log de inlogtijd
                user_id = get_user_id(username)  # Haal de user_id op
                on_success(username, user_id)  # Geef username en user_id door
            else:
                lbl_login_status.config(text="Invalid username or password", foreground="red")

        btn_login = ttk.Button(login_frame, text="Login", command=check_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(login_frame, text="Register", command=show_registration_screen).grid(row=4, column=0, columnspan=2, pady=10)

    def show_registration_screen():
        clear_frame(login_frame)
        ttk.Label(login_frame, text="New Username:").grid(row=0, column=0, pady=10)
        entry_username = ttk.Entry(login_frame)
        entry_username.grid(row=0, column=1, pady=10)

        ttk.Label(login_frame, text="New Password:").grid(row=1, column=0, pady=10)
        entry_password = ttk.Entry(login_frame, show='*')
        entry_password.grid(row=1, column=1, pady=10)

        ttk.Label(login_frame, text="Name:").grid(row=2, column=0, pady=10)
        entry_name = ttk.Entry(login_frame)
        entry_name.grid(row=2, column=1, pady=10)

        lbl_registration_status = ttk.Label(login_frame, text="")
        lbl_registration_status.grid(row=4, column=0, columnspan=2)

        def register_user():
            username = entry_username.get()
            password = entry_password.get()
            name = entry_name.get()

            if not username or not password or not name:
                lbl_registration_status.config(text="All fields are required", foreground="red")
                return

            if get_user_by_username(username):
                lbl_registration_status.config(text="Username already exists", foreground="red")
                return

            add_user(username, password, name)
            lbl_registration_status.config(text="Registration successful", foreground="green")
            user_id = get_user_id(username)  # Retrieve the new user's ID
            login_frame.pack_forget()
            on_success(username, user_id)  # Pass both username and user_id

        btn_register = ttk.Button(login_frame, text="Register", command=register_user)
        btn_register.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(login_frame, text="Back to Login", command=show_login_screen).grid(row=5, column=0, columnspan=2, pady=10)

    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    show_login_screen()
