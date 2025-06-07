#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>

const char WIFI_SSID[] = "NICOLE_E_MARCOS";
const char WIFI_PASSWORD[] = "Dv010400";

String HOST_NAME   = "http://192.168.1.8:3000";
String PATH_NAME   = "/m_dht_report/";

DHT dht(15, DHT22);

void setup() {
  Serial.begin(9600);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  dht.begin();
}

void loop() {

  delay(10000);

  if(WiFi.status() != WL_CONNECTED) {

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while(WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
  }

  int h = int(round(dht.readHumidity()));
  int t = int(round(dht.readTemperature()));

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    h = 0;
    t = 0;
  }

  HTTPClient http;
  String query = HOST_NAME + PATH_NAME + String(t) + "/" + String(h);
  
  http.begin(query); //HTTP
  
  int httpCode = http.GET();

  // httpCode will be negative on error
  if (httpCode > 0) {
    // file found at server
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println(payload);
    } else {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);
    }
  } else {
    Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}
