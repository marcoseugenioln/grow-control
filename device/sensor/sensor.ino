#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>

const char WIFI_SSID[] = "NICOLE_E_MARCOS";
const char WIFI_PASSWORD[] = "Dv010400";

const String humidity_sensor_id = "2";
const String temp_sensor_id = "1";

String HUM_URL   = "http://grow-control.kinghost.net/grow/sensor/data/" + humidity_sensor_id + "/";

String TEMP_URL   = "http://grow-control.kinghost.net/grow/sensor/data/" + temp_sensor_id + "/";

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;
// Timer set to 10 minutes (600000)
//unsigned long timerDelay = 600000;
// Set timer to 5 seconds (5000)
unsigned long timerDelay = 1000;

DHT dht(15, DHT22);

void setup() {
  Serial.begin(9600);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

  dht.begin();
}

void loop() {
  // Send an HTTP POST request depending on timerDelay
  if ((millis() - lastTime) > timerDelay) {

    int h = int(round(dht.readHumidity()));
    int t = int(round(dht.readTemperature()));

    // Check if any reads failed and exit early (to try again).
    if (isnan(h) || isnan(t)) {
      h = 0;
      t = 0;
    }

    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      HTTPClient http;
      String client_hum = HUM_URL + String(h);
      String client_temp = TEMP_URL + String(t);
      
      http.begin(client_hum); //HTTP

      // Send HTTP GET request
      int httpResponseCode = http.GET();
      
      // httpCode will be negative on error
      if (httpResponseCode > 0) {
        // file found at server
        if (httpResponseCode == HTTP_CODE_OK) {
          String payload = http.getString();
          Serial.println(payload);
        } else {
          // HTTP header has been send and Server response header has been handled
          Serial.printf("[HTTP] GET... code: %d\n", httpResponseCode);
        }
      } else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      // Free resources
      http.end();

      http.begin(client_temp); //HTTP

      // Send HTTP GET request
      httpResponseCode = http.GET();
      
      // httpCode will be negative on error
      if (httpResponseCode > 0) {
        // file found at server
        if (httpResponseCode == HTTP_CODE_OK) {
          String payload = http.getString();
          Serial.println(payload);
        } else {
          // HTTP header has been send and Server response header has been handled
          Serial.printf("[HTTP] GET... code: %d\n", httpResponseCode);
        }
      } else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}
