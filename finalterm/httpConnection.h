#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include "wifi.h"
#include "enums.h"

class httpReturn{
public:
    int code;
    String payload;
};

httpReturn httpGETRequest(const char* servername);
httpReturn httpPOSTRequest(const char* servername);

bool checkHttpServer();
bool sendPostRequest(int msg);
int getCurrentState();