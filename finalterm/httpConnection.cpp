#include "httpConnection.h"

WiFiClient client;
HTTPClient http;

const char *arduinoHost = "";
const char *serverOnlineURL = "";
const int httpPort = 9949;

const int HTTP_SUCCESS = 200;
const int HTTP_USER_ERROR = 400;
const int HTTP_SERVER_ERROR = 500;

static unsigned long lastTime = 60001;
unsigned long timeDelay = CHECK_STATE_DELAY;

// GET request 처리
httpReturn httpGETRequest(const char *serverName)
{
    httpReturn ret;

    http.begin(client, serverName);
    ret.code = http.GET();

    if (ret.code > 0)
    {
        Serial.print("HTTP Response code: ");
        Serial.println(ret.code);
        ret.payload = http.getString();
    }
    else
    {
        Serial.print("Error code: ");
        Serial.print(ret.code);
        Serial.printf(", %s\n", http.errorToString(ret.code).c_str());
    }

    http.end();
    return ret;
}

// POST request 처리
// header와 body 추가
httpReturn httpPOSTRequest(const char *serverName, String msg)
{
    httpReturn ret;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    ret.code = http.POST(msg);

    if (ret.code > 0)
    {
        Serial.print("HTTP Response code: ");
        Serial.println(ret.code);
        ret.payload = http.getString();
    }
    else
    {
        Serial.print("Error code: ");
        Serial.print(ret.code);
        Serial.printf(", %s\n", http.errorToString(ret.code).c_str());
    }

    http.end();
    return ret;
}

// Server가 살아있는지 체크
bool checkHttpServer()
{
    Serial.print("(GET) connecting to ");
    Serial.println(serverOnlineURL);

    if (isWiFiConnected())
    {
        httpReturn ret = httpGETRequest(serverOnlineURL);

        if (ret.code != HTTP_SUCCESS && ret.code != HTTP_USER_ERROR && ret.code != HTTP_SERVER_ERROR)
        {
            Serial.println("Unknown error code");
            return false;
        }

        StaticJsonDocument<200> json;
        deserializeJson(json, ret.payload);
        String pay = json["ret"];

        Serial.println("ret code: " + String(ret.code));
        Serial.println("ret: " + pay);

        if (ret.code == HTTP_SUCCESS)
        {
            return true;
        }
    }

    return false;
}

// POST 처리와 리턴값 처리
// 200이 아닐 경우 에러 핸들링
bool sendPostRequest(int msg)
{
    String body = "message=" + String(msg);

    Serial.print("(POST) connecting to ");
    Serial.println(arduinoHost);
    Serial.println("(POST) body: " + body);

    if (isWiFiConnected())
    {
        httpReturn ret = httpPOSTRequest(arduinoHost, body);

        if (ret.code != HTTP_SUCCESS && ret.code != HTTP_USER_ERROR && ret.code != HTTP_SERVER_ERROR)
        {
            Serial.println("Unknown error code");
            return false;
        }

        StaticJsonDocument<200> json;
        deserializeJson(json, ret.payload);
        String pay = json["ret"];

        Serial.println("ret code: " + String(ret.code));
        Serial.println("ret: " + pay);

        if (ret.code == HTTP_SUCCESS)
        {
            return true;
        }
    }

    return false;
}

// 서버로부터 current state 체크
// loop 안에서 실행되므로 delay 
int getCurrentState()
{
    int ret_val = -1;

    if ((millis() - lastTime) > timeDelay)
    {
        Serial.print("(GET) connecting to ");
        Serial.println(arduinoHost);

        if (isWiFiConnected())
        {
            httpReturn ret = httpGETRequest(arduinoHost);

            if (ret.code != HTTP_SUCCESS && ret.code != HTTP_USER_ERROR && ret.code != HTTP_SERVER_ERROR)
            {
                Serial.println("Unknown error code");
                
                lastTime = millis();
                return STATE_UNKNOWN_RESPONSE;
            }

            StaticJsonDocument<200> json;
            deserializeJson(json, ret.payload);

            String ret_code = json["ret"];

            Serial.println("ret code: " + String(ret.code));
            Serial.println("ret: " + ret_code);

            String currentStatus = json["currentState"];
            int pay = currentStatus.toInt();
            Serial.printf("serverState: %d\n", pay);

            if (ret.code == HTTP_SUCCESS)
            {
                
                lastTime = millis();
                return pay;
            }
            else if (ret.code != HTTP_USER_ERROR || ret.code != HTTP_SERVER_ERROR)
            {
                Serial.println("Unknown error code");
            }
        }
        
        lastTime = millis();
        return STATE_CANNOT_CONNECT_SERVER;
    }

    return STATE_TIMOUT_NOT_REACHED;
}