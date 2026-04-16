// Include Servo library to control servo motors
#include <Servo.h>

// SERVO OBJECT DECLARATION

Servo baseServo; // Controls horizontal movement (left/right)
Servo armServo;  // Controls vertical movement (up/down)

// POSITION VARIABLES

// Current position of servos (initially set to center position = 90°)
int baseCurrent = 90;
int armCurrent = 90;

// Target position received from Python (desired angle)
int baseTarget = 90;
int armTarget = 90;

// CONTROL PARAMETERS

// Smoothing factor controls how fast the servo moves toward target
// Smaller value = smoother but slower motion
float smoothFactor = 0.1;

// HARDWARE COMPONENT

// LED pin used for system status indication
int ledPin = 13;

// SETUP FUNCTION (RUNS ONCE)

void setup()
{
  // Initialize serial communication at 9600 baud rate
  // Enables communication between Arduino and Python program
  Serial.begin(9600);

  // Attach servos to Arduino pins
  baseServo.attach(9); // Base servo → pin 9
  armServo.attach(10); // Arm servo → pin 10

  // Set LED pin as output
  pinMode(ledPin, OUTPUT);
}

// MAIN LOOP (RUNS CONTINUOUSLY)

void loop()
{
  // Check if data is available from Python via serial communication
  if (Serial.available())
  {
    // Read incoming data until newline character '\n'
    // Possible inputs:
    // "angle1,angle2" → move servos
    // "STOP" → stop movement
    // "HOME" → reset to center
    String data = Serial.readStringUntil('\n');

    // STOP COMMAND

    if (data == "STOP")
    {
      // Turn OFF LED to indicate system is inactive
      digitalWrite(ledPin, LOW);

      // Exit loop early → keeps servo at current position
      return;
    }

    // HOME COMMAND (RESET POSITION)

    if (data == "HOME")
    {
      // Reset both servos to center position (90°)
      baseTarget = 90;
      armTarget = 90;

      // Turn ON LED to indicate system is active
      digitalWrite(ledPin, HIGH);
    }

    // ANGLE DATA PROCESSING

    // Find position of comma in received string
    int commaIndex = data.indexOf(',');

    // If valid format exists, extract both angles
    if (commaIndex > 0)
    {
      // Extract base servo angle (before comma)
      baseTarget = data.substring(0, commaIndex).toInt();

      // Extract arm servo angle (after comma)
      armTarget = data.substring(commaIndex + 1).toInt();

      // Turn ON LED → system is active
      digitalWrite(ledPin, HIGH);
    }
  }

  // SMOOTH MOVEMENT ALGORITHM

  // Gradually move base servo toward target angle
  baseCurrent = baseCurrent + (baseTarget - baseCurrent) * smoothFactor;

  // Gradually move arm servo toward target angle
  armCurrent = armCurrent + (armTarget - armCurrent) * smoothFactor;

  // APPLY MOVEMENT TO SERVOS

  baseServo.write(baseCurrent);
  armServo.write(armCurrent);

  // SMALL DELAY FOR STABILITY

  delay(20);
}