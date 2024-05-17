#include <WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_PN532.h>

#define PN532_SCK  D2
#define PN532_MOSI D3
#define PN532_SS   D4
#define PN532_MISO D5

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

const char* ssid     = "appelenpeer";
const char* password = "6281appel";
const char* server_ip = "192.168.36.150"; // Vervang door het IP-adres van je computer
const int server_port = 80;

void setup() {
  Serial.begin(115200);
  Serial.print("Hallo");

  // Connecteer met WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi");

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); 
  }
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  nfc.setPassiveActivationRetries(0xFF);
  Serial.println("Waiting for an ISO14443A card");
}

void loop() {
  uint8_t success;
  uint8_t uid[7] = { 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Found a card!");
    Serial.print("UID Length: "); Serial.print(uidLength, DEC); Serial.println(" bytes");
    Serial.print("UID Value: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(" 0x"); Serial.print(uid[i], HEX);
    }
    Serial.println("");

    if (uidLength == 4) {
      // Stuur de UID via WiFi
      Serial.println("Sending UID over WiFi...");
      WiFiClient client;
      if (client.connect(server_ip, server_port)) {
        // Convert UID array to hexadecimal string
        String uidString = "";
        for (uint8_t i = 0; i < uidLength; i++) {
          if (uid[i] < 0x10) {
            uidString += "0";
          }
          uidString += String(uid[i], HEX);
        }
        uidString.toUpperCase(); // Optioneel converteren naar hoofdletters

        // Print de UID string over WiFi
        client.print(uidString);
        client.stop();
      } else {
        Serial.println("Connection to server failed!");
      }
    } else {
      Serial.println("Unauthorized card!");
    }
    
    delay(1000);
  } else {
    Serial.println("Timed out waiting for a card");
  }
}
