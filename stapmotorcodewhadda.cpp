#include <Arduino.h>

int motorPin1 = D3; // Blue - 28BYJ48 pin 1
int motorPin2 = D5; // Pink - 28BYJ48 pin 2
int motorPin3 = D6; // Yellow - 28BYJ48 pin 3
int motorPin4 = D7; // Orange - 28BYJ48 pin 4

int motorSpeed = 1200;
int count = 0;
int countsperrev = 512;
int maxSteps = 130; // Maximum number of steps allowed in each direction
int lookup[8] = {B01000, B01100, B00100, B00110, B00010, B00011, B00001, B01001};

int buttonRightPin = D10;
int buttonLeftPin = D11;

void setOutput(int out) {
  digitalWrite(motorPin1, bitRead(lookup[out], 0));
  digitalWrite(motorPin2, bitRead(lookup[out], 1));
  digitalWrite(motorPin3, bitRead(lookup[out], 2));
  digitalWrite(motorPin4, bitRead(lookup[out], 3));
}

void anticlockwise() {
  if (count < maxSteps) { // Check if within maximum steps limit
    for (int i = 0; i < 8; i++) {
      setOutput(i);
      delayMicroseconds(motorSpeed);
    }
    count++;
  }
}

void clockwise() {
  if (count > -maxSteps) { // Check if within maximum steps limit
    for (int i = 7; i >= 0; i--) {
      setOutput(i);
      delayMicroseconds(motorSpeed);
    }
    count--;
  }
}

void setup() {
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);

  pinMode(buttonRightPin, INPUT_PULLUP);
  pinMode(buttonLeftPin, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() {
  if (digitalRead(buttonRightPin) == LOW) {
    clockwise();
  }

  if (digitalRead(buttonLeftPin) == LOW) {
    anticlockwise();
  }
}

