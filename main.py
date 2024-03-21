import serial
import pyodbc
from datetime import datetime

# Verbinding maken met de Microsoft Access-database
conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\KDG\sim4\Database11.accdb;'  # Vervang dit pad door het pad naar je eigen database
)

# Maak een cursor-object om queries uit te voeren
cursor = conn.cursor()

# Functie om gegevens naar de database te schrijven
def write_to_database(uid, uid_length, train_name, current_time):
    cursor.execute("INSERT INTO treininfo (uid, uid_length, train_name, current_time) VALUES (?, ?, ?, ?)",
                   (uid, uid_length, train_name, current_time))
    conn.commit()

# Definieer de COM-poort en baudrate
ser = serial.Serial('COM5', 115200)

# Definieer geaccepteerde UID's en bijbehorende treinmodellen
accepted_uids = [
    bytes([0x63, 0x6A, 0xD2, 0x1F]),
    bytes([0xB3, 0x55, 0xD2, 0x1F]),
    bytes([0x13, 0x84, 0x04, 0xBE]),
    bytes([0x83, 0xA7, 0xCE, 0x1F]),
    bytes([0xB3, 0x63, 0x00, 0xBE])
]

train_models = [
    "Trein model 1",
    "Trein model 2",
    "Trein model 3",
    "Trein model 4",
    "Trein model 5"
]

while True:
    # Lees een regel van de seriële poort
    line = ser.readline().decode().strip()

    # Controleer of de regel begint met "Found a card!"
    if line == "Found a card!":
        # Lees de volgende regel voor UID Lengte
        uid_length = ser.readline().decode().strip().split(": ")[1]
        print("UID Length:", uid_length)

        # Lees de volgende regel voor UID Value
        uid_value = ser.readline().decode().strip().split(": ")[1]
        print("UID Value:", uid_value)

        # Haal de lengte van de UID op
        uid_length = int(uid_length.split()[0])

        # Controleer of de UID geaccepteerd is
        if uid_length == 4:
            uid_bytes = bytes([int(x, 16) for x in uid_value.split()])
            if uid_bytes in accepted_uids:
                # Vind de index van de geaccepteerde UID in de lijst
                index = accepted_uids.index(uid_bytes)
                # Haal de treinnaam op
                train_name = train_models[index]
                # Haal het moment van detectie op
                current_time = datetime.now()
                # Print de geaccepteerde UID en het bijbehorende treinmodel
                print("Accepted UID! Dit is trein:", train_name)
                # Schrijf de gegevens naar de database
                write_to_database(uid_value, uid_length, train_name, current_time)
            else:
                print("Unauthorized card!")
        else:
            print("UID heeft een ongeldige lengte.")
