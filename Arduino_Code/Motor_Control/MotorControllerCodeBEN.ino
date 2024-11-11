// Author: Ben and Chatgpt https://suno.com/song/71361c22-18f9-4d45-a371-dc579e969a36

// OI README
// This code uses the 2 and only 2 avaialble interupt pins on your dog Arudino Nano. 
// We should use the ESP32, maybe this one is overkill but makes the point https://www.electronicwings.com/esp32/gpio-interrupt-of-esp32 64 interupts. 
// Ideally as we have 8 channels on the reciever or more? we need preferably need an interupt pin for each. 
// Channel fli[ is tested and wokring
// Sound



#include <Servo.h>

const int pinLeftStick = 2;       // Transmitter Left Stick (INT0)
const int pinRightStick = 3;      // Transmitter Right Stick (INT1)
const int pinServoSwitch = 5;     // Input from receiver channel 4
const int pinServoOut = 6;        // Output PWM based on switch position

#define pinMotorFrontLeft 12
#define pinMotorRearLeft 11
#define pinMotorFrontRight 9
#define pinMotorRearRight 10

#define sparkMaxMax 2000
#define sparkMaxMin 1000

Servo servoFrontLeft, servoRearLeft, servoFrontRight, servoRearRight;
Servo servoOut; // Servo object for outputting the pulse width on pin 6

// Pulse widths for each control
volatile unsigned long LeftPulseWidth = 1500;
volatile unsigned long RightPulseWidth = 1500;
unsigned long ServoSwitchPulseWidth = 0;

void setup() {
  delay(5000); // Wait 5 seconds to ensure stable startup

  // Attach each motor to its respective pin
  servoFrontLeft.attach(pinMotorFrontLeft);
  servoRearLeft.attach(pinMotorRearLeft);
  servoFrontRight.attach(pinMotorFrontRight);
  servoRearRight.attach(pinMotorRearRight);
  servoOut.attach(pinServoOut); // Attach pin 6 to output the calculated pulse width

  // Set up interrupts for left and right sticks
  attachInterrupt(digitalPinToInterrupt(pinLeftStick), LeftStickISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(pinRightStick), RightStickISR, CHANGE);

  pinMode(pinServoSwitch, INPUT); // Set up pinServoSwitch as input
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

void readServoSwitchPulse() {
  // Measure the length of the HIGH pulse on pin 5
  ServoSwitchPulseWidth = pulseIn(pinServoSwitch, HIGH);
}

void checkAndSetServoOut() {
  if (ServoSwitchPulseWidth >= 970 && ServoSwitchPulseWidth <= 990) {
    // Full reverse position
    servoOut.writeMicroseconds(499);
  } else if (ServoSwitchPulseWidth >= 1474 && ServoSwitchPulseWidth <= 1494) {
    // Neutral position
    servoOut.writeMicroseconds(1500);
  } else if (ServoSwitchPulseWidth >= 1986 && ServoSwitchPulseWidth <= 2006) {
    // Full forward position
    servoOut.writeMicroseconds(2501);
  }
}

void setMotorSpeeds() {
  int pwmLeft = map(LeftPulseWidth, 2000, 1000, sparkMaxMin, sparkMaxMax); // Up on both joysticks is forward
  int pwmRight = map(RightPulseWidth, 1000, 2000, sparkMaxMin, sparkMaxMax);

  servoFrontLeft.writeMicroseconds(pwmLeft);
  servoRearLeft.writeMicroseconds(pwmLeft);
  servoFrontRight.writeMicroseconds(pwmRight);
  servoRearRight.writeMicroseconds(pwmRight);
}

void loop() {
  setMotorSpeeds();       // Update motor speeds based on left and right stick positions
  readServoSwitchPulse(); // Read the pulse width from pin 5
  checkAndSetServoOut();  // Set the output pulse width on pin 6 based on the switch position

  delay(20);              // Short delay to improve loop efficiency
}
