#include <WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include "rfid_firebeetle_config.h" 
//pins voor ded rfid board
#define PN532_SCK  D2
#define PN532_MOSI D3
#define PN532_SS   D4
#define PN532_MISO D5

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

void setup() {
  Serial.begin(115200);
  Serial.print("Hallo");

  // Verbinden met WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Verbinden met WiFi..");
  }
  Serial.println("Verbonden met WiFi");

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.print("Geen PN53x bord gevonden");
    while (1); 
  }
  Serial.print("Chip gevonden PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware versie. "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  nfc.setPassiveActivationRetries(0xFF);
  Serial.println("Wachten op een ISO14443A kaart");
}

void loop() {
  uint8_t success;
  uint8_t uid[7] = { 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Kaart gevonden!");
    Serial.print("UID Lengte: "); Serial.print(uidLength, DEC); Serial.println(" bytes");
    Serial.print("UID Waarde: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(" 0x"); Serial.print(uid[i], HEX);
    }
    Serial.println("");

    if (uidLength == 4) {
      // Stuur de UID naar de server
      Serial.println("Verzenden van UID via WiFi...");
      WiFiClient client;
      if (client.connect(server_ip, server_port)) {
        // Converteer UID array naar hexadecimale string
        String uidString = "";
        for (uint8_t i = 0; i < uidLength; i++) {
          if (uid[i] < 0x10) {
            uidString += "0";
          }
          uidString += String(uid[i], HEX);
        }
        uidString.toUpperCase();

        // Print de UID 
        client.println(uidString);
        client.println("E"); 
        client.flush();

        // Wacht op  server
        while (client.connected()) {
          if (client.available()) {
            String response = client.readStringUntil('\n');
            response.trim();
            Serial.println("Server respons: " + response);
            if (response == "AUTHORIZED") {
              Serial.println("Kaart is geautoriseerd, versturen rotatie commando...");
              // stuur command naar server dat het mag rotaten
              WiFiClient motorClient;
              if (motorClient.connect(server_ip, server_port)) {
                motorClient.println("ROTATE");
                motorClient.stop();
              }
            } else {
              Serial.println("Kaart is niet geautoriseerd.");
            }
            break;
          }
        }

        client.stop();
      } else {
        Serial.println("Verbinding met server mislukt!");
      }
    } else {
      Serial.println("Ongeautoriseerde kaart!");
    }
    
    delay(1000);
  } else {
    Serial.println("Time-out wachten op een kaart");
  }
}
