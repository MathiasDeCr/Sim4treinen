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

byte sensorPin = 2;
byte indicator = 13;

void setup()
{
  pinMode(sensorPin,INPUT);
  pinMode(indicator,OUTPUT);
  Serial.begin(9600);
}

void loop()
{
  byte state = digitalRead(sensorPin);
  digitalWrite(indicator,state);
  if(state == 1)Serial.println("Somebody is in this area!");
  else if(state == 0)Serial.println("No one!");
  delay(500);
}