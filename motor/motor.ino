#include <WiFiS3.h>
#include <ArduinoJson.h>
#include "Stepper.h"
#include "arduino_motor_config.h"

WiFiServer server(server_port);  // Gebruik de variabele uit config.h

// Define number of steps per revolution:
const int stepsPerRevolution = 300;

// Geef de motoraansturingspinnen namen:
#define pwmA 3
#define pwmB 11
#define brakeA 9
#define brakeB 8
#define dirA 12
#define dirB 13

// Knoppen
int buttonRightPin = 5;
int buttonLeftPin = 6;
int buttonFullPin = 7; // Nieuwe knop pin voor 180 graden rotatie
int button180Pin = 4;

// Telegram bot gegevens


// Initialiseer de stepper bibliotheek op het motor schild:
Stepper myStepper = Stepper(stepsPerRevolution, dirA, dirB);

bool isRotatingRight = false; // Bijhouden of de motor momenteel naar rechts draait
bool isRotatingLeft = false;  // Bijhouden of de motor momenteel naar links draait

int currentPosition = 0; // Variabele om huidige positie bij te houden

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wacht tot de seriële poort is geopend
  }

  // Verbinden met WiFi-netwerk
  Serial.println();
  Serial.println("Verbinden met WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi verbonden");
  Serial.println("IP-adres: ");
  Serial.println(WiFi.localIP());

  server.begin();

  // Stel de PWM- en rempinnen in zodat de richtingspinnen kunnen worden gebruikt om de motor aan te sturen:
  pinMode(pwmA, OUTPUT);
  pinMode(pwmB, OUTPUT);
  pinMode(brakeA, OUTPUT);
  pinMode(brakeB, OUTPUT);

  pinMode(buttonRightPin, INPUT_PULLUP);
  pinMode(buttonLeftPin, INPUT_PULLUP);
  pinMode(buttonFullPin, INPUT_PULLUP);
  pinMode(button180Pin, INPUT_PULLUP); // Stel de nieuwe knop pin in als invoer met pull-up weerstand

  digitalWrite(pwmA, HIGH);
  digitalWrite(pwmB, HIGH);
  digitalWrite(brakeA, LOW);
  digitalWrite(brakeB, LOW);

  // Stel de motorsnelheid in (RPM's):
  myStepper.setSpeed(60);

  // Stel de beginpositie in op 0
  myStepper.step(-currentPosition);
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    while (!client.available()) {
      delay(1);
    }

    // Lees het commando van de client
    String command = client.readStringUntil('\r');
    client.flush();

    // Voer het ontvangen commando uit
    if (command == "R") {
      if (!isRotatingRight && currentPosition != 1025) {
        rechts();
        sendMessageToTelegram("Motor draait naar rechts.");
      }
    } else if (command == "L") {
      if (!isRotatingLeft && currentPosition != 1025) {
        links();
        sendMessageToTelegram("Motor draait naar links.");
      }
    } else if (command == "F") {
      if (currentPosition != 0) {
        moveToZero();
        sendMessageToTelegram("Motor draait terug naar 0.");
      }
    } else if (command == "A") {
      if (currentPosition == 0) {
        rotate180();
        sendMessageToTelegram("Motor draait 180 graden.");
      }
    }
  }

  // Controleer fysieke knoppen
  if (digitalRead(buttonRightPin) == HIGH && !isRotatingRight && currentPosition != 1025) {
    rechts();
    sendMessageToTelegram("Motor draait naar rechts (knop ingedrukt).");
  } else if (digitalRead(buttonLeftPin) == HIGH && !isRotatingLeft && currentPosition != 1025) {
    links();
    sendMessageToTelegram("Motor draait naar links (knop ingedrukt).");
  } else if (digitalRead(buttonFullPin) == HIGH && currentPosition != 0) {
    moveToZero();
    sendMessageToTelegram("Motor draait terug naar 0 (knop ingedrukt).");
  } else if (digitalRead(button180Pin) == HIGH && currentPosition == 0) {
    rotate180();
    sendMessageToTelegram("Motor draait 180 graden (knop ingedrukt).");
  }
}

void rechts() {
  if (!isRotatingLeft) {
    myStepper.step(90);
    currentPosition += 90; // Update positie
    isRotatingRight = true;
  } else {
    myStepper.step(180); // Verdubbel de stappen in vergelijking met links
    currentPosition += 180; // Update positie
    isRotatingRight = true;
    isRotatingLeft = false;
  }
}

void links() {
  if (!isRotatingRight) {
    myStepper.step(-90);
    currentPosition -= 90; // Update positie
    isRotatingLeft = true;
  } else {
    myStepper.step(-180); // Verdubbel de stappen in vergelijking met rechts
    currentPosition -= 180; // Update positie
    isRotatingLeft = true;
    isRotatingRight = false;
  }
}

void rotate180() {
  if (currentPosition == 0) { // Controleer of huidige positie 0 is
    myStepper.step(1025); // Draai 180 graden (1025 stappen)
    currentPosition = 1025; // Update positie naar 1025
  }
}

void moveToZero() {
  // Beweeg alleen naar nulpositie als de huidige positie niet al nul is
  if (currentPosition != 0) {
    int stepsToZero = -currentPosition; // Stappen nodig om terug te keren naar de nulpositie
    myStepper.step(stepsToZero);
    currentPosition = 0; // Reset positie naar 0
    isRotatingRight = false; // Reset rotatie vlaggen
    isRotatingLeft = false;
  }
}

void sendMessageToTelegram(String message) {
  WiFiSSLClient client;
  
  if (client.connect("api.telegram.org", 443)) {  // Verbinden met de Telegram server
    String url = "/bot" + String(botToken) + "/sendMessage?chat_id=" + String(chatId) + "&text=" + message;
    
    // Maak HTTP verzoek
    client.println("GET " + url + " HTTP/1.1");
    client.println("Host: api.telegram.org");
    client.println("Connection: close");
    client.println();
    
    // Debug: Toon het verzonden bericht
    Serial.println("Verzonden naar Telegram: " + message);
    
    // Debug: Toon de server response
    while (client.connected()) {
      String line = client.readStringUntil('\n');
      if (line == "\r") {
        break;
      }
      Serial.println(line);
    }
  } else {
    Serial.println("Verbinding met Telegram mislukt!");
  }
  client.stop();
}
