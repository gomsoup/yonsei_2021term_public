#include <Servo.h>
#include "HUSKYLENS.h"
#include "SoftwareSerial.h"

#define VibrationThreshold 775
#define RED   1
#define GREEN 2
#define BLUE  3
#define OPEN 90
#define CLOSE 1
#define URGENT 1
#define NORMAL 2
#define CMD_NORMAL 0
#define CMD_SWITCH_URGENT 1
#define CMD_SWITCH_NORMAL 2
#define CMD_SIGNAL_URGENT 3

HUSKYLENS huskylens;
SoftwareSerial mySerial(5, 6); // RX, TX
//HUSKYLENS green line >> Pin 5; blue line >> Pin 6

Servo myservo;
int pos = 0;

const int PinLED    = 2;
const int PinServo  = 3;
const int PinLEDVCC = 4;

const int PinCmd1   = 7;
const int PinCmd2   = 8;
const int PinRed    = 9;
const int PinBlue   = 10;
const int PinGreen  = 11;
const int PinButton = 12; 
const int PinUrgent = 13; 
const int PinVib    = A0; 

int currentMode = NORMAL;
int doorStatus  = OPEN;

int readCommand();
bool detectObject();
bool detectVibration();
void LightRGB(int color);
void LightLED(int op);
void doorOperation(int op);
void printResult(HUSKYLENSResult result);

void setup() 
{
  pinMode(PinLED, OUTPUT);
  pinMode(PinRed, OUTPUT);
  pinMode(PinBlue, OUTPUT);
  pinMode(PinGreen, OUTPUT);
  pinMode(PinLEDVCC, OUTPUT);
  pinMode(PinUrgent, OUTPUT);

  myservo.attach(PinServo);
  myservo.write(OPEN);
  
  Serial.begin(9600);
  mySerial.begin(9600);
  while (!huskylens.begin(mySerial))
  {
      Serial.println(F("Begin failed!"));
      Serial.println(F("1.Please recheck the \"Protocol Type\" in HUSKYLENS (General Settings>>Protocol Type>>Serial 9600)"));
      Serial.println(F("2.Please recheck the connection."));
      delay(100);
  }
}


void loop() 
{
  if (detectVibration()) {
    currentMode = URGENT;
    doorOperation(CLOSE);
    LightRGB(RED);
    digitalWrite(PinUrgent, HIGH);
  }

  if (digitalRead(PinButton) == LOW) {
    if (currentMode == NORMAL) {
      doorOperation(doorStatus==OPEN ? CLOSE : OPEN);
      LightRGB(doorStatus==OPEN ? BLUE : GREEN);
    }  
  }

  int cmd = readCommand();
  if (cmd != 0) {
    Serial.print("Receive Command ");
    Serial.println(cmd);
  }  

  switch(cmd) {
  case CMD_SWITCH_URGENT:
    currentMode = URGENT;
    doorOperation(CLOSE);
    LightRGB(RED);
    break;
  case CMD_SWITCH_NORMAL:
    currentMode = NORMAL;
    doorOperation(CLOSE);
    LightRGB(GREEN);
    break;
  case CMD_SIGNAL_URGENT:
    digitalWrite(PinUrgent, LOW);
    break;
  case 40:
    LightLED(HIGH);
    delay(100);
    if (detectObject())
      Serial.println("Object detected");
    else
      Serial.println("Object not detected");
    delay(100);
    LightLED(LOW);
    break;
  default:
    break;
  }
}


int readCommand()
{
  int cmd1 = digitalRead(PinCmd1);
  int cmd2 = digitalRead(PinCmd2);
  return (cmd1<<1) + cmd2;
}


bool detectObject()
{
  bool ret = false;
  if (!huskylens.request()) Serial.println(F("Fail to request data from HUSKYLENS, recheck the connection!"));
  else if(!huskylens.isLearned()) Serial.println(F("Nothing learned, press learn button on HUSKYLENS to learn one!"));
  else if(!huskylens.available()) Serial.println(F("No block or arrow appears on the screen!"));
  else
  {
      Serial.println(F("###########"));
      while (huskylens.available())
      {
          HUSKYLENSResult result = huskylens.read();
          ret = (result.xOrigin != -1);
      }    
  }
  
  return ret;
}

void doorOperation(int op)
{
  delay(100);
  if (op == OPEN) {
    myservo.write(OPEN);
  }
  else if (op == CLOSE) {
    myservo.write(CLOSE);
  }
  else {
    Serial.println("Invalid Door Operation!");
    delay(1000);
  }
  delay(100);
  doorStatus = op;
}

bool detectVibration()
{
  // sensor output range : 0~1023
  int sensorOut = analogRead(PinVib);
  
  if (sensorOut > VibrationThreshold) {
    Serial.println("Detect Vibration!");
    return true;
  }
  
  return false;
}

void LightRGB(int color)
{
  if (color == RED) {
    analogWrite(PinRed, 255);
    analogWrite(PinGreen, 0);
    analogWrite(PinBlue,  0);
  }
  else if (color == GREEN) {
    analogWrite(PinRed,  0);
    analogWrite(PinGreen,255);
    analogWrite(PinBlue, 0);
  }
  else if (color == BLUE) {
    analogWrite(PinRed,   0);
    analogWrite(PinGreen, 0);
    analogWrite(PinBlue,255);
  }
  else {
    Serial.println("Invalid RGB Color!");
    delay(1000);
  }
}


void LightLED(int op)
{
  digitalWrite(PinLED, op);
  digitalWrite(PinLEDVCC, op);
}


void printResult(HUSKYLENSResult result)
{
    if (result.command == COMMAND_RETURN_BLOCK){
        Serial.println(String()+F("Block:xCenter=")+result.xCenter+F(",yCenter=")+result.yCenter+F(",width=")+result.width+F(",height=")+result.height+F(",ID=")+result.ID);
    }
    else if (result.command == COMMAND_RETURN_ARROW){
        Serial.println(String()+F("Arrow:xOrigin=")+result.xOrigin+F(",yOrigin=")+result.yOrigin+F(",xTarget=")+result.xTarget+F(",yTarget=")+result.yTarget+F(",ID=")+result.ID);
    }
    else{
        Serial.println("Object unknown!");
    }
}
