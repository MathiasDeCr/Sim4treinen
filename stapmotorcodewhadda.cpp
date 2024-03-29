#include "Stepper.h"

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
  // Step one revolution in one direction:
  if (digitalRead(buttonRightPin) == HIGH && !isRotatingRight && currentPosition != 1025) {
    rechts();
  } else if (digitalRead(buttonLeftPin) == HIGH && !isRotatingLeft && currentPosition != 1025) {
    links();
  } else if (digitalRead(buttonFullPin) == HIGH && currentPosition != 0) {
    full();
  } else if (digitalRead(button180Pin) == HIGH && currentPosition == 0) { // Check if button is pressed and current position is 0
    rotate180(); // Only call rotate180() if the button is pressed and current position is 0
  }
}


void rechts() {
  if (!isRotatingLeft) {
    myStepper.step(90);
    currentPosition += 90; // Update position
    isRotatingRight = true;
  } else {
    myStepper.step(180); // Dubbel zoveel stappen als links
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
    myStepper.step(-180); // Dubbel zoveel stappen als rechts
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

