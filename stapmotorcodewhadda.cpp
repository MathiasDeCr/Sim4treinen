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
int buttonFullPin = 7;
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

  digitalWrite(pwmA, HIGH);
  digitalWrite(pwmB, HIGH);
  digitalWrite(brakeA, LOW);
  digitalWrite(brakeB, LOW);

  // Set the motor speed (RPMs):
  myStepper.setSpeed(60);
}

void loop() {
  // Step one revolution in one direction:
  if (digitalRead(buttonRightPin) == HIGH && !isRotatingRight) {
    rechts();
  } else if (digitalRead(buttonLeftPin) == HIGH && !isRotatingLeft) {
    links();
  } else if (digitalRead(buttonFullPin) == HIGH){
    full();
  }
}

void rechts() {
  if (!isRotatingLeft) {
    myStepper.step(85.416);
    currentPosition += 85.416; // Update position
    isRotatingRight = true;
  } else {
    myStepper.step(170.832); // Dubbel zoveel stappen als links
    currentPosition += 170.832; // Update position
    isRotatingRight = true;
    isRotatingLeft = false;
  }
}

void links() {
  if (!isRotatingRight) {
    myStepper.step(-85.416);
    currentPosition -= 85.416; // Update position
    isRotatingLeft = true;
  } else {
    myStepper.step(-170.832); // Dubbel zoveel stappen als rechts
    currentPosition -= 170.832; // Update position
    isRotatingLeft = true;
    isRotatingRight = false;
  }
}

void full(){
  int stepsToHome = -currentPosition; // Steps needed to return to start position
  myStepper.step(stepsToHome);
  currentPosition = 0; // Reset position to 0
  isRotatingRight = false; // Reset rotation flags
  isRotatingLeft = false;
}

void oneeighty(){

  
}
