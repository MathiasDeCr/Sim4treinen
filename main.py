import socket
import pyodbc
from datetime import datetime

# Verbinding maken met de Microsoft Access-database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\KDG\sim4\Database11.accdb;'
)
print('Verbonden met database')

# Maak een cursor-object om queries uit te voeren
cursor = conn.cursor()

# Functie om geaccepteerde UID's en bijbehorende treinmodellen op te halen
def get_accepted_uids():
    cursor.execute("SELECT uid, train_model FROM accepted_uids")
    rows = cursor.fetchall()
    accepted_uids = {bytes.fromhex(row.uid): row.train_model for row in rows}
    return accepted_uids

accepted_uids = get_accepted_uids()

# Functie om gegevens naar de database te schrijven
def write_to_database(uid, uid_length, train_name, current_time):
    cursor.execute("INSERT INTO treininfo (uid, uid_length, train_name, current_time) VALUES (?, ?, ?, ?)",
                   (uid, uid_length, train_name, current_time))
    conn.commit()

# Maak een socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind de socket aan het juiste IP-adres en poort
s.bind(('0.0.0.0', 80))
# Luister naar verbindingen
s.listen(5)

while True:
    # Accepteer verbindingen van buitenaf
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")

    # Ontvang gegevens van de Arduino
    uid_string = clientsocket.recv(1024).strip().decode('utf-8')
    print("UID Value:", uid_string)

    # Converteer hex string naar bytes
    uid_value = bytes.fromhex(uid_string)
    uid_length = len(uid_value)

    # Controleer of de UID geaccepteerd is
    if uid_length == 4 and uid_value in accepted_uids:
        train_name = accepted_uids[uid_value]
        current_time = datetime.now()
        print("Accepted UID! Dit is trein:", train_name)
        write_to_database(uid_value.hex().upper(), uid_length, train_name, current_time)
    else:
        print("Unauthorized card or UID has invalid length.")

    # Sluit de clientsocket verbinding
    clientsocket.close()
