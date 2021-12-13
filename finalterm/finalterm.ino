#include "httpConnection.h"
#define CMD_NORMAL 0
#define CMD_SWITCH_URGENT 1
#define CMD_SWITCH_NORMAL 2
#define CMD_SIGNAL_URGENT 3

const int PinCmd1 = D1;
const int PinCmd2 = D2;
const int PinUrgent  = D3;

int currentState = 0;
bool isArgent = false;

void writeCommand(int cmd);

void setup()
{
  pinMode(PinCmd1, OUTPUT);
  pinMode(PinCmd2, OUTPUT);   
  
  Serial.println("Initilization start...");
  Serial.begin(115200);
  delay(10);

  wifi_setup();

  while (!checkHttpServer())
  {
    delay(NETWORK_DELAY);
  }

  Serial.println("Initilization done!");
  delay(NETWORK_DELAY);
}

void loop()
{
  //Get Current State
  setCurrentState();
  
  if(isArgent){
    //긴급모드시 동작할 것들...
    //긴급모드는 앱에서밖에 해제 불가능..
    //setCurrentState()에서 자동으로 해제할것임
  }else{
    //일반모드시 동작할 것들...
    //...
    //만약 일반모드 동작하다가 긴급상황이 감지된다면 서버로 알림..
    if (digitalRead(PinUrgent) == HIGH) {
      while(!sendPostRequest(DEVICE_ALERT_ARGENT)){
        delay(NETWORK_DELAY);
      }
      writeCommand(CMD_SIGNAL_URGENT);
    }
  }

  //delay(1000);
}

void writeCommand(int cmd)
{
  digitalWrite(PinCmd1, cmd & 0b10);
  digitalWrite(PinCmd2, cmd & 0b01);
}

void setCurrentState()
{
  int ret = getCurrentState();

  if (ret == STATE_TIMOUT_NOT_REACHED)
  {
    //Serial.println("getCurrentState() timeout not reached");
  }
  else if (ret == STATE_CANNOT_CONNECT_SERVER)
  {
    Serial.println("getCurrentState() can't connect server");
  }
  else
  {
    if (isArgent)
    {
      if (ret == APP_SWITCH_NORMAL_MODE)
      {
        while (!sendPostRequest(DEVICE_SET_NORMAL)){
          delay(NETWORK_DELAY);
        }

        Serial.println("switch Normal mode");
        writeCommand(CMD_SWITCH_NORMAL);
        isArgent = false;
      }
      else
      {
        writeCommand(CMD_NORMAL);
      }
    }
    else
    {
      if (ret == APP_SWITCH_ARGENT_MODE || ret == NOTIFY_ARGENT)
      {
        isArgent = true;
        while (!sendPostRequest(DEVICE_SET_ARGENT))
        {
          delay(NETWORK_DELAY);
        }
        
        Serial.println("switch Argent mode");
        writeCommand(CMD_SWITCH_URGENT);
      }
      else
      {
        writeCommand(CMD_NORMAL);
      }
    }
  }
  delay(100);
  writeCommand(CMD_NORMAL);
}
