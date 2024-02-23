#include <Arduino.h>

// #
// # Editor     : Youyou from DFRobot
// # Date       : 04.06.2014
// # E-Mail : youyou.yu@dfrobot.com

// # Product name: PIR (Motion) Sensor
// # Product SKU : SEN0171
// # Version     : 1.0

// # Description:
// # The sketch for using the PIR Motion sensor with Arduino/Raspberry Pi controller to achieve the human detection feature.

// # Hardware Connection:
// #        PIR Sensor    -> Digital pin 2
// #        Indicator LED -> Digital pin 13
// #

byte sensorPin1 = D2;
byte sensorPin2 = D3;
byte sensorPin3 = D4;

void setup()
{
  pinMode(sensorPin1,INPUT);
  pinMode(sensorPin2,INPUT);
  pinMode(sensorPin3,INPUT);

  Serial.begin(9600);
}

void loop()
{
  byte state1 = digitalRead(sensorPin1);
  if(state1 == 1)Serial.println("Somebody is in this area of the first sensor!");
  else if(state1 == 0)Serial.println("No one at first sensor!");
  delay(500);
  byte state2 = digitalRead(sensorPin2);
  if(state2 == 1)Serial.println("Somebody is in this area of the second sensor!");
  else if(state2 == 0)Serial.println("No one at second sensor!");
  delay(500);
  byte state3 = digitalRead(sensorPin3);
  if(state3 == 1)Serial.println("Somebody is in this area of the third sensor!");
  else if(state3 == 0)Serial.println("No one at third sensor!");
  delay(500);
}
