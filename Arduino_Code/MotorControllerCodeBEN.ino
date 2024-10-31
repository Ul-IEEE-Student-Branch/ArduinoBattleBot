// Author: Ben and Chatgpt https://suno.com/song/71361c22-18f9-4d45-a371-dc579e969a36

// OI README
// This code uses the 2 and only 2 avaialble interupt pins on your dog Arudino Nano. 
// We should use the ESP32, maybe this one is overkill but makes the point https://www.electronicwings.com/esp32/gpio-interrupt-of-esp32 64 interupts. 
// Ideally as we have 8 channels on the reciever or more? we need preferably need an interupt pin for each. 
// 1 untested change has been made, in setmotorspeeds pwmLeft has been inverted 2000, 1000. Check this
// Sound

#include <Arduino.h>
#include <Servo.h>

const int pinLeftStick = 2;       // Transmitter Left Stick (INT0)
const int pinRightStick = 3;      // Transmitter Right Stick (INT1)
const int pinWeaponSwitch = 5;    // Turn on and off only (PCINT21)
const int pinAddOnSwitch = 6;     // Forward / Off / Reverse (PCINT22)

#define pinMotorFrontLeft 12
#define pinMotorRearLeft 11
#define pinMotorFrontRight 9
#define pinMotorRearRight 10
#define pinMotorWeapon A2
#define pinAddOn A3

#define sparkMaxMax 2000
#define sparkMaxMin 1000
#define sparkMiniMax 2500
#define sparkMiniMin 500

Servo servoFrontLeft, servoRearLeft, servoFrontRight, servoRearRight, servoWeapon, servoAddOn;

// Pulse widths for each control
volatile unsigned long LeftPulseWidth = 1500;
volatile unsigned long RightPulseWidth = 1500;
volatile unsigned long WeaponPulseWidth = 1500;
volatile unsigned long AddOnPulseWidth = 1500;

void setup() {
  Serial.begin(9600); // Start serial communication

  // Attach each motor to its respective pin
  servoFrontLeft.attach(pinMotorFrontLeft);
  servoRearLeft.attach(pinMotorRearLeft);
  servoFrontRight.attach(pinMotorFrontRight);
  servoRearRight.attach(pinMotorRearRight);
  servoWeapon.attach(pinMotorWeapon);
  servoAddOn.attach(pinAddOn);

  // Set up interrupts for left and right sticks
  attachInterrupt(digitalPinToInterrupt(pinLeftStick), LeftStickISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(pinRightStick), RightStickISR, CHANGE);
}

void LeftStickISR() {
  static unsigned long startTime = 0;
  if (digitalRead(pinLeftStick) == HIGH) {
    startTime = micros();
  } else {
    LeftPulseWidth = micros() - startTime;
  }
}

void RightStickISR() {
  static unsigned long startTime = 0;
  if (digitalRead(pinRightStick) == HIGH) {
    startTime = micros();
  } else {
    RightPulseWidth = micros() - startTime;
  }
}

void setMotorSpeeds() {
  int pwmLeft = map(LeftPulseWidth, 2000, 1000, sparkMaxMin, sparkMaxMax);  // I flipped the bish because i want up on both joysticks to be forward
  int pwmRight = map(RightPulseWidth, 1000, 2000, sparkMaxMin, sparkMaxMax);
  
  // Print statements for debugging
  Serial.print("Left Stick Pulse Width: ");
  Serial.print(LeftPulseWidth);
  Serial.print(" -> Mapped PWM Left: ");
  Serial.println(pwmLeft);
  
  Serial.print("Right Stick Pulse Width: ");
  Serial.print(RightPulseWidth);
  Serial.print(" -> Mapped PWM Right: ");
  Serial.println(pwmRight);
  
  servoFrontLeft.writeMicroseconds(pwmLeft);
  servoRearLeft.writeMicroseconds(pwmLeft);
  servoFrontRight.writeMicroseconds(pwmRight);
  servoRearRight.writeMicroseconds(pwmRight);
}




void loop() {
  setMotorSpeeds();   // Update motor speeds based on left and right stick positions

  
  // Print a separator for each loop iteration

  
  delay(20);          // Short delay to improve loop efficiency
}
