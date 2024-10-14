#include <Arduino.h>
#include <Servo.h>

#define pinL1 9
const int LeftpwmPin = 3; // Pin 3 where PWM signal is connected
const int RightpwmPin = 5; // Pin 5 where PWM signal is connected

#define sparkMax 1000 // Default full-reverse input pulse
#define sparkMin 2000 // Default full-forward input pulse

Servo leftOne, rightOne;
int Routput = 1500, Loutput = 1500, inputValue = 0;

void setup() {
  Serial.begin(9600); // Start serial communication at 9600 baud
  pinMode(LeftpwmPin, INPUT); // Set pin as input
  leftOne.attach(pinL1);
  //rightOne.attach(pinL1);
}

void setWheelVelocity(int left, int right) {
 Loutput = map(left, -100, 100, sparkMin, sparkMax);
 // Serial.print("output: ");
 //Serial.println(output);
 leftOne.writeMicroseconds(Loutput);

Routput = map(right, -100, 100, sparkMin, sparkMax);
 // Serial.print("output: ");
 //Serial.println(output);
 rightOne.writeMicroseconds(Routput);

}

int ReadLeftStick()
{
  unsigned long LefthighTime = pulseIn(LeftpwmPin, HIGH); // Time the signal is high
  return map((float)LefthighTime, 977, 1987, -100, 100);
}

int ReadRightStick()
{
  unsigned long RighthighTime = pulseIn(RightpwmPin, HIGH); // Time the signal is high
  return map((float)RighthighTime, 974, 2008, -100, 100);
}

void loop() {
  int LeftmappedValue = ReadLeftStick();
  int RightmappedValue = ReadRightStick();

  // get mappedvalue and send to motor
if(abs(LeftmappedValue) > 5){
  setWheelVelocity(LeftmappedValue,0);
    
}
else{
  setWheelVelocity(0,0);
}
  //

  delay(50); // Delay before the next reading
}
