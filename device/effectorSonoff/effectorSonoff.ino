#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>

// Default values
#define DEFAULT_EFFECTOR_ID ""
#define DEFAULT_WIFI_SSID ""
#define DEFAULT_WIFI_PASSWORD ""
#define DEFAULT_SERVER_URL ""

// Configuration structure
struct Config {
  char effector_id[10];
  char wifi_ssid[32];
  char wifi_password[64];
  char server_url[100];
  bool configured;
  int connection_failures;
  uint8_t mac_address[6];
};

Config config;
unsigned long lastTime = 0;
unsigned long timerDelay = 15000;

// Sonoff Basic R2 pins
const byte relay_pin = 12;
const byte led_pin = 13;

ESP8266WebServer server(80);
String URL;
String uniqueAPName;

// Retry control variables
int retryCount = 0;
const int maxRetries = 3;
const unsigned long retryDelay = 5000;

// Web server always available
bool webServerEnabled = true;

void setup() {
  Serial.begin(115200);
  
  pinMode(relay_pin, OUTPUT);
  pinMode(led_pin, OUTPUT);
  
  EEPROM.begin(512);
  
  WiFi.macAddress(config.mac_address);
  char macSuffix[7];
  snprintf(macSuffix, sizeof(macSuffix), "%02X%02X%02X", 
           config.mac_address[3], config.mac_address[4], config.mac_address[5]);
  uniqueAPName = "Sonoff_" + String(macSuffix);
  
  // Visual feedback
  for (int i = 0; i < 3; i++) {
    digitalWrite(led_pin, HIGH);
    delay(200);
    digitalWrite(led_pin, LOW);
    delay(200);
  }
  
  loadConfig();
  
  Serial.println("\n=== Sonoff Basic R2 Effector ===");
  Serial.print("Device MAC: ");
  Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X\n", 
                config.mac_address[0], config.mac_address[1], config.mac_address[2],
                config.mac_address[3], config.mac_address[4], config.mac_address[5]);
  
  // Start AP mode ALWAYS
  startAPMode();
  
  // Try to connect to WiFi in background
  connectToWiFiBackground();
  
  setupWebServer();
  
  Serial.println("Web interface always available at: http://192.168.4.1");
  digitalWrite(led_pin, HIGH);
}

void startAPMode() {
  WiFi.softAP(uniqueAPName.c_str(), "");
  Serial.print("AP Mode: ");
  Serial.println(uniqueAPName);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());
}

bool connectToWiFiBackground() {
  if (strlen(config.wifi_ssid) == 0) {
    Serial.println("No WiFi config found");
    return false;
  }
  
  Serial.print("Connecting to WiFi: ");
  Serial.println(config.wifi_ssid);
  
  // Non-blocking connection attempt
  WiFi.begin(config.wifi_ssid, config.wifi_password);
  
  return true;
}

void checkWiFiConnection() {
  static unsigned long lastCheck = 0;
  
  if (millis() - lastCheck > 5000) {  // Check every 5 seconds
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi not connected - still trying...");
      // LED blink slowly when not connected
      digitalWrite(led_pin, !digitalRead(led_pin));
    } else {
      // LED solid when connected
      digitalWrite(led_pin, HIGH);
    }
    lastCheck = millis();
  }
}

void loadConfig() {
  EEPROM.get(0, config);
  
  if (!config.configured || config.mac_address[0] == 0 || strlen(config.effector_id) == 0) {
    Serial.println("Loading default values...");
    strcpy(config.effector_id, DEFAULT_EFFECTOR_ID);
    strcpy(config.wifi_ssid, DEFAULT_WIFI_SSID);
    strcpy(config.wifi_password, DEFAULT_WIFI_PASSWORD);
    strcpy(config.server_url, DEFAULT_SERVER_URL);
    WiFi.macAddress(config.mac_address);
    config.configured = true;
    config.connection_failures = 0;
    saveConfig();
  }
  
  URL = String(config.server_url) + String(config.effector_id);
  Serial.print("Effector ID: ");
  Serial.println(config.effector_id);
  Serial.print("Server URL: ");
  Serial.println(URL);
}

void saveConfig() {
  EEPROM.put(0, config);
  EEPROM.commit();
  Serial.println("Configuration saved");
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    String wifiStatus = (WiFi.status() == WL_CONNECTED) ? 
      "Connected to " + String(config.wifi_ssid) + " - IP: " + WiFi.localIP().toString() : 
      "Not connected - trying to connect to: " + String(config.wifi_ssid);
    
    String html = "<html><head><meta charset='UTF-8'><title>Sonoff Control</title>"
                  "<style>body{font-family:Arial,sans-serif;margin:20px;}</style></head><body>"
                  "<h1>🔌 Sonoff Control Panel</h1>"
                  
                  "<div style='background:#f0f0f0;padding:15px;border-radius:5px;margin:10px 0;'>"
                  "<strong>Device:</strong> " + uniqueAPName + "<br>"
                  "<strong>MAC:</strong> " + String(config.mac_address[0], HEX) + ":" + 
                  String(config.mac_address[1], HEX) + ":" + String(config.mac_address[2], HEX) + ":" + 
                  String(config.mac_address[3], HEX) + ":" + String(config.mac_address[4], HEX) + ":" + 
                  String(config.mac_address[5], HEX) + "<br>"
                  "<strong>WiFi Status:</strong> " + wifiStatus + "<br>"
                  "<strong>AP Access:</strong> http://192.168.4.1<br>"
                  "</div>"
                  
                  "<h3>⚙️ Configuration</h3>"
                  "<form method='post' action='/save'>"
                  "WiFi SSID: <input type='text' name='ssid' value='" + String(config.wifi_ssid) + "'><br>"
                  "Password: <input type='password' name='password' value='" + String(config.wifi_password) + "'><br>"
                  "Effector ID: <input type='text' name='effector_id' value='" + String(config.effector_id) + "'><br>"
                  "Server URL: <input type='text' name='server_url' value='" + String(config.server_url) + "'><br>"
                  "<input type='submit' value='💾 Save'>"
                  "</form>"
                  
                  "<h3>🔧 Actions</h3>"
                  "<form method='post' action='/restart'><input type='submit' value='🔄 Restart'></form>"
                  "<form method='post' action='/reset'><input type='submit' value='⚡ Reset to Default'></form>"
                  
                  "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.on("/save", HTTP_POST, []() {
    server.arg("ssid").toCharArray(config.wifi_ssid, 32);
    server.arg("password").toCharArray(config.wifi_password, 64);
    server.arg("effector_id").toCharArray(config.effector_id, 10);
    server.arg("server_url").toCharArray(config.server_url, 100);
    
    saveConfig();
    URL = String(config.server_url) + String(config.effector_id);
    
    // Reconnect to WiFi with new credentials
    WiFi.disconnect();
    connectToWiFiBackground();
    
    String html = "<html><head><meta charset='UTF-8'><title>Settings Saved</title></head><body>"
                  "<h1>✅ Settings Saved!</h1>"
                  "<p>Reconnecting to WiFi...</p>"
                  "<p><a href='/'>Back to control panel</a></p>"
                  "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.on("/restart", HTTP_POST, []() {
    server.send(200, "text/html", "<html><body><h1>🔄 Restarting...</h1></body></html>");
    delay(1000);
    ESP.restart();
  });
  
  server.on("/reset", HTTP_POST, []() {
    strcpy(config.effector_id, DEFAULT_EFFECTOR_ID);
    strcpy(config.wifi_ssid, DEFAULT_WIFI_SSID);
    strcpy(config.wifi_password, DEFAULT_WIFI_PASSWORD);
    strcpy(config.server_url, DEFAULT_SERVER_URL);
    config.configured = true;
    
    saveConfig();
    URL = String(config.server_url) + String(config.effector_id);
    
    WiFi.disconnect();
    connectToWiFiBackground();
    
    server.send(200, "text/html", "<html><body><h1>⚡ Reset to Default!</h1><p>Restarting...</p></body></html>");
    delay(1000);
    ESP.restart();
  });
  
  server.begin();
  Serial.println("Web server started");
}

bool makeHttpRequest() {
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  WiFiClient client;
  HTTPClient http;
  bool success = false;

  if (http.begin(client, URL)) {
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String payload = http.getString();
      bool turn_device_on = payload.toInt() == 1;
      digitalWrite(relay_pin, turn_device_on ? HIGH : LOW);
      success = true;
      retryCount = 0;
    }
    http.end();
  }

  return success;
}

void loop() {
  server.handleClient();  // Always handle web requests
  
  checkWiFiConnection();  // Check WiFi status periodically
  
  // Normal operation
  if ((millis() - lastTime) > timerDelay && WiFi.status() == WL_CONNECTED) {
    bool requestSuccess = makeHttpRequest();
    
    if (!requestSuccess) {
      retryCount++;
      if (retryCount >= maxRetries) {
        retryCount = 0;
      } else {
        delay(retryDelay);
        return;
      }
    } else {
      retryCount = 0;
    }

    lastTime = millis();
  }

  delay(10);
}
