#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_SCK  (2)
#define PN532_MOSI (3)
#define PN532_SS   (4)
#define PN532_MISO (5)

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

#define PN532_IRQ   (2)
#define PN532_RESET (3)

#define NUM_ACCEPTED_UIDS 5

const uint8_t acceptedUIDs[NUM_ACCEPTED_UIDS][4] = {
  {0x63, 0x6A, 0xD2, 0x1F},
  {0xB3, 0x55, 0xD2, 0x1F},
  {0x13, 0x84, 0x4, 0xBE},
  {0x83, 0xA7, 0xCE, 0x1F},
  {0xB3, 0x63, 0x0, 0xBE}
};

const char* trainModels[NUM_ACCEPTED_UIDS] = {
  "Trein model 1",
  "Trein model 2",
  "Trein model 3",
  "Trein model 4",
  "Trein model 5"
};

void setup(void) {
  Serial.begin(115200);
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

void loop(void) {
  uint8_t success;
  uint8_t uid[7] = { 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Found a card!");
    Serial.print("UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("UID Value: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(" 0x");Serial.print(uid[i], HEX);
    }
    Serial.println("");

    bool isAccepted = false;
    int acceptedIndex;
    for (int i = 0; i < NUM_ACCEPTED_UIDS; i++) {
      if (memcmp(uid, acceptedUIDs[i], uidLength) == 0) {
        isAccepted = true;
        acceptedIndex = i;
        break;
      }
    }

    if (isAccepted) {
      Serial.print("Accepted UID! Dit is trein: ");
      Serial.println(trainModels[acceptedIndex]);
    } else {
      Serial.println("Unauthorized card!");
    }
    
    delay(1000);
  }
  else {
    Serial.println("Timed out waiting for a card");
  }
}
