#include <WiFi.h>
#include "Stepper.h"

#define PIR_PIN 2 // Pin voor PIR-sensor

char ssid[] = "IoT";     // naam van je WiFi-netwerk
char pass[] = "KdGIoT70!"; // wachtwoord van je WiFi-netwerk

WiFiServer server(80);

// Define number of steps per revolution:
const int stepsPerRevolution = 300;

// Give the motor control pins names:
#define pwmA 3
#define pwmB 11
#define brakeA 9
#define brakeB 8
#define dirA 12
#define dirB 13

// Buttons
int buttonRightPin = 5;
int buttonLeftPin = 6;
int buttonFullPin = 7; // New button pin for 180-degree rotation
int button180Pin = 4;

// Initialize the stepper library on the motor shield:
Stepper myStepper = Stepper(stepsPerRevolution, dirA, dirB);

bool isRotatingRight = false; // Track if the motor is currently rotating right
bool isRotatingLeft = false;  // Track if the motor is currently rotating left

int currentPosition = 0; // Variable to track current position

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait until serial port is opened
  }

  pinMode(PIR_PIN, INPUT); // Configure PIR pin as input

  // Connect to WiFi network
  Serial.println();
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());



  server.begin();

  // Set the PWM and brake pins so that the direction pins can be used to control the motor:
  pinMode(pwmA, OUTPUT);
  pinMode(pwmB, OUTPUT);
  pinMode(brakeA, OUTPUT);
  pinMode(brakeB, OUTPUT);

  pinMode(buttonRightPin, INPUT_PULLUP);
  pinMode(buttonLeftPin, INPUT_PULLUP);
  pinMode(buttonFullPin, INPUT_PULLUP);
  pinMode(button180Pin, INPUT_PULLUP); // Set the new button pin as input with pull-up resistor

  digitalWrite(pwmA, HIGH);
  digitalWrite(pwmB, HIGH);
  digitalWrite(brakeA, LOW);
  digitalWrite(brakeB, LOW);

  // Set the motor speed (RPMs):
  myStepper.setSpeed(60);

  // Set the initial position to 0
  myStepper.step(-currentPosition);
}

void loop() {
  // Check PIR sensor for motion
  if (digitalRead(PIR_PIN) == HIGH) {
    // Beweging gedetecteerd, breng de motor naar de nulpositie als de motor niet al op nul staat
    if (currentPosition != 0) {
      moveToZero();
      Serial.println("Motion detected! Moving motor to zero position.");
    }
  }

  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  while (!client.available()) {
    delay(1);
  }

  // Read the command from the client
  String command = client.readStringUntil('\r');
  client.flush();

  // Execute the received command
  if (command == "R") {
    if (!isRotatingRight && currentPosition != 1025) {
      rechts();
      
    }
  } else if (command == "L") {
    if (!isRotatingLeft && currentPosition != 1025) {
      links();
      Serial.print("ok");
    }
  } else if (command == "F") {
    if (currentPosition != 0) {
      full();
      Serial.print("ok");
    }
  } else if (command == "A") {
    if (currentPosition == 0) {
      rotate180();
      Serial.print("ok");
    }
  }
  
  // Check physical buttons
  if (digitalRead(buttonRightPin) == HIGH && !isRotatingRight && currentPosition != 1025) {
    rechts();
    Serial.print("ok");
  } else if (digitalRead(buttonLeftPin) == HIGH && !isRotatingLeft && currentPosition != 1025) {
    links();
    Serial.print("ok");
  } else if (digitalRead(buttonFullPin) == HIGH && currentPosition != 0) {
    full();
    Serial.print("ok");
  } else if (digitalRead(button180Pin) == HIGH && currentPosition == 0) {
    rotate180();
    Serial.print("ok");
  }
}

void rechts() {
  if (!isRotatingLeft) {
    myStepper.step(90);
    currentPosition += 90; // Update position
    isRotatingRight = true;
  } else {
    myStepper.step(180); // Double the steps compared to left
    currentPosition += 180; // Update position
    isRotatingRight = true;
    isRotatingLeft = false;
  }
}

void links() {
  if (!isRotatingRight) {
    myStepper.step(-90);
    currentPosition -= 90; // Update position
    isRotatingLeft = true;
  } else {
    myStepper.step(-180); // Double the steps compared to right
    currentPosition -= 180; // Update position
    isRotatingLeft = true;
    isRotatingRight = false;
  }
}

void full() {
  int stepsToHome = -currentPosition; // Steps needed to return to start position
  myStepper.step(stepsToHome);
  currentPosition = 0; // Reset position to 0
  isRotatingRight = false; // Reset rotation flags
  isRotatingLeft = false;
}

void rotate180() {
  if (currentPosition == 0) { // Check if current position is 0
    myStepper.step(1025); // Rotate 180 degrees (1025 steps)
    currentPosition = 1025; // Update position to 1025
  }
}

void moveToZero() {
  // Beweeg alleen naar nulpositie als de huidige positie niet al nul is
  if (currentPosition != 0) {
    int stepsToZero = -currentPosition; // Steps needed to return to zero position
    myStepper.step(stepsToZero);
    currentPosition = 0; // Reset position to 0
    isRotatingRight = false; // Reset rotation flags
    isRotatingLeft = false;
  }
}
