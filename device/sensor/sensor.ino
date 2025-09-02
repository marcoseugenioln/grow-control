#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <EEPROM.h>

// Default values
#define DEFAULT_HUMIDITY_ID ""
#define DEFAULT_TEMPERATURE_ID ""
#define DEFAULT_WIFI_SSID ""
#define DEFAULT_WIFI_PASSWORD ""
#define DEFAULT_SERVER_URL ""

// Configuration structure
struct SensorConfig {
  char humidity_id[10];
  char temperature_id[10];
  char wifi_ssid[32];
  char wifi_password[64];
  char server_url[100];
  bool configured;
  int connection_failures;
  uint8_t mac_address[6];
};

SensorConfig config;
DHT dht(15, DHT22);
unsigned long lastTime = 0;
unsigned long timerDelay = 15000;
WebServer server(80);
bool webServerEnabled = true;
String HUM_URL;
String TEMP_URL;
String uniqueAPName;

// Retry control variables
int retryCount = 0;
const int maxRetries = 3;
const unsigned long retryDelay = 5000;

// EEPROM configuration for ESP32
#define EEPROM_SIZE 512

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  // Initialize EEPROM
  EEPROM.begin(EEPROM_SIZE);
  
  // Get MAC address for unique identification
  WiFi.macAddress(config.mac_address);
  
  // Generate unique AP name using last 3 bytes of MAC
  char macSuffix[7];
  snprintf(macSuffix, sizeof(macSuffix), "%02X%02X%02X", 
           config.mac_address[3], config.mac_address[4], config.mac_address[5]);
  uniqueAPName = "DHT_Sensor_" + String(macSuffix);
  
  loadConfig();
  
  Serial.println("\n=== DHT22 Sensor ===");
  Serial.print("Device MAC: ");
  Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X\n", 
                config.mac_address[0], config.mac_address[1], config.mac_address[2],
                config.mac_address[3], config.mac_address[4], config.mac_address[5]);
  Serial.print("Unique AP Name: ");
  Serial.println(uniqueAPName);
  
  // Start AP mode ALWAYS
  startAPMode();
  
  // Try to connect to WiFi in background
  connectToWiFiBackground();
  
  setupWebServer();
  
  Serial.println("Web interface always available");
  Serial.print("Access at: http://");
  Serial.println(WiFi.softAPIP());
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
  
  if (millis() - lastCheck > 5000) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi not connected - still trying...");
    }
    lastCheck = millis();
  }
}

void loadConfig() {
  EEPROM.get(0, config);
  
  if (!config.configured || config.mac_address[0] == 0 || 
      strlen(config.humidity_id) == 0 || strlen(config.temperature_id) == 0) {
    
    Serial.println("Loading default values...");
    strcpy(config.humidity_id, DEFAULT_HUMIDITY_ID);
    strcpy(config.temperature_id, DEFAULT_TEMPERATURE_ID);
    strcpy(config.wifi_ssid, DEFAULT_WIFI_SSID);
    strcpy(config.wifi_password, DEFAULT_WIFI_PASSWORD);
    strcpy(config.server_url, DEFAULT_SERVER_URL);
    WiFi.macAddress(config.mac_address);
    config.configured = true;
    config.connection_failures = 0;
    saveConfig();
  }
  
  updateUrls();
  Serial.print("Humidity ID: ");
  Serial.println(config.humidity_id);
  Serial.print("Temperature ID: ");
  Serial.println(config.temperature_id);
  Serial.print("Server URLs configured");
}

void updateUrls() {
  HUM_URL = String(config.server_url) + String(config.humidity_id) + "/";
  TEMP_URL = String(config.server_url) + String(config.temperature_id) + "/";
}

void saveConfig() {
  EEPROM.put(0, config);
  EEPROM.commit();
  updateUrls();
  Serial.println("Configuration saved to EEPROM");
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    String wifiStatus = (WiFi.status() == WL_CONNECTED) ? 
      "Connected to " + String(config.wifi_ssid) + " - IP: " + WiFi.localIP().toString() : 
      "Not connected - trying to connect to: " + String(config.wifi_ssid);
    
    String html = "<html><head><meta charset='UTF-8'><title>DHT Sensor Control</title>"
                  "<style>"
                  "body { font-family: Arial, sans-serif; margin: 20px; }"
                  ".device-info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }"
                  "input[type='text'], input[type='password'] { width: 250px; padding: 5px; margin: 5px 0; }"
                  ".btn { padding: 10px 15px; border: none; border-radius: 5px; color: white; cursor: pointer; margin: 5px; }"
                  ".btn-save { background: #28a745; }"
                  ".btn-reset { background: #dc3545; }"
                  ".btn-restart { background: #007bff; }"
                  "</style></head><body>"
                  "<h1>🌡️ DHT22 Sensor Control</h1>"
                  
                  "<div class='device-info'>"
                  "<strong>Device:</strong> " + uniqueAPName + "<br>"
                  "<strong>MAC:</strong> " + 
                  String(config.mac_address[0], HEX) + ":" + 
                  String(config.mac_address[1], HEX) + ":" + 
                  String(config.mac_address[2], HEX) + ":" + 
                  String(config.mac_address[3], HEX) + ":" + 
                  String(config.mac_address[4], HEX) + ":" + 
                  String(config.mac_address[5], HEX) + "<br>"
                  "<strong>WiFi Status:</strong> " + wifiStatus + "<br>"
                  "<strong>AP Access:</strong> http://" + WiFi.softAPIP().toString() + "<br>"
                  "<strong>Humidity ID:</strong> " + String(config.humidity_id) + "<br>"
                  "<strong>Temperature ID:</strong> " + String(config.temperature_id) + "<br>"
                  "</div>"
                  
                  "<h3>⚙️ Configuration</h3>"
                  "<form method='post' action='/save'>"
                  "<h4>📶 WiFi Settings</h4>"
                  "SSID: <input type='text' name='ssid' value='" + String(config.wifi_ssid) + "'><br>"
                  "Password: <input type='password' name='password' value='" + String(config.wifi_password) + "'><br>"
                  
                  "<h4>🔧 Sensor Settings</h4>"
                  "Humidity ID: <input type='text' name='humidity_id' value='" + String(config.humidity_id) + "'><br>"
                  "Temperature ID: <input type='text' name='temperature_id' value='" + String(config.temperature_id) + "'><br>"
                  
                  "<h4>🌐 Server Settings</h4>"
                  "Server URL: <input type='text' name='server_url' value='" + String(config.server_url) + "'><br>"
                  
                  "<input type='submit' value='💾 Save Configuration' class='btn btn-save'>"
                  "</form>"
                  
                  "<h3>🔧 Actions</h3>"
                  "<form method='post' action='/restart' style='display:inline;'>"
                  "<input type='submit' value='🔄 Restart' class='btn btn-restart'>"
                  "</form>"
                  "<form method='post' action='/reset' style='display:inline;'>"
                  "<input type='submit' value='⚡ Reset Defaults' class='btn btn-reset'>"
                  "</form>"
                  
                  "<h3>📊 Sensor Data</h3>"
                  "<form method='post' action='/read'>"
                  "<input type='submit' value='📡 Read Sensors Now' class='btn' style='background:#6f42c1;'>"
                  "</form>"
                  
                  "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.on("/save", HTTP_POST, []() {
    server.arg("ssid").toCharArray(config.wifi_ssid, 32);
    server.arg("password").toCharArray(config.wifi_password, 64);
    server.arg("humidity_id").toCharArray(config.humidity_id, 10);
    server.arg("temperature_id").toCharArray(config.temperature_id, 10);
    server.arg("server_url").toCharArray(config.server_url, 100);
    
    saveConfig();
    
    // Reconnect to WiFi with new credentials
    WiFi.disconnect();
    connectToWiFiBackground();
    
    String html = "<html><head><meta charset='UTF-8'><title>Settings Saved</title></head><body>"
                  "<h1>✅ Settings Saved!</h1>"
                  "<p>Reconnecting to WiFi with new settings...</p>"
                  "<p><a href='/'>Back to control panel</a></p>"
                  "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.on("/reset", HTTP_POST, []() {
    strcpy(config.humidity_id, DEFAULT_HUMIDITY_ID);
    strcpy(config.temperature_id, DEFAULT_TEMPERATURE_ID);
    strcpy(config.wifi_ssid, DEFAULT_WIFI_SSID);
    strcpy(config.wifi_password, DEFAULT_WIFI_PASSWORD);
    strcpy(config.server_url, DEFAULT_SERVER_URL);
    config.configured = true;
    
    saveConfig();
    
    WiFi.disconnect();
    connectToWiFiBackground();
    
    String html = "<html><head><meta charset='UTF-8'></head><body>"
                  "<h1>⚡ Reset to Default Values!</h1>"
                  "<p>Restarting with default configuration...</p>"
                  "</body></html>";
    server.send(200, "text/html", html);
    
    delay(3000);
    ESP.restart();
  });
  
  server.on("/restart", HTTP_POST, []() {
    String html = "<html><head><meta charset='UTF-8'></head><body>"
                  "<h1>🔄 Restarting...</h1>"
                  "<p>Device will restart momentarily</p>"
                  "</body></html>";
    server.send(200, "text/html", html);
    
    delay(1000);
    ESP.restart();
  });
  
  server.on("/read", HTTP_POST, []() {
    String result = readAndSendSensorData();
    String html = "<html><head><meta charset='UTF-8'></head><body>"
                  "<h1>📊 Sensor Reading</h1>"
                  "<pre>" + result + "</pre>"
                  "<p><a href='/'>Back to control panel</a></p>"
                  "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.begin();
  Serial.println("Web server started");
}

String readAndSendSensorData() {
  String result = "=== Sensor Reading ===\n";
  
  int h = int(round(dht.readHumidity()));
  int t = int(round(dht.readTemperature()));

  if (isnan(h) || isnan(t)) {
    result += "Failed to read DHT sensor!\n";
    h = 0;
    t = 0;
  }

  result += "Humidity: " + String(h) + "%\n";
  result += "Temperature: " + String(t) + "°C\n";
  
  if (WiFi.status() == WL_CONNECTED) {
    bool humSuccess = sendSensorData(HUM_URL, String(h));
    delay(1000);
    bool tempSuccess = sendSensorData(TEMP_URL, String(t));
    
    result += "\n=== Server Response ===\n";
    result += "Humidity data " + String(humSuccess ? "sent successfully" : "failed") + "\n";
    result += "Temperature data " + String(tempSuccess ? "sent successfully" : "failed") + "\n";
  } else {
    result += "\nWiFi not connected - data not sent to server\n";
  }
  
  return result;
}

bool sendSensorData(const String& url, const String& value) {
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  HTTPClient http;
  bool success = false;

  String full_url = url + value;
  Serial.print("Sending to: ");
  Serial.println(full_url);

  if (http.begin(full_url)) {
    int httpResponseCode = http.GET();
    success = (httpResponseCode > 0);
    http.end();
  }

  return success;
}

void loop() {
  server.handleClient();  // Always handle web requests
  checkWiFiConnection();  // Check WiFi status periodically
  
  // Normal sensor reading operation
  if ((millis() - lastTime) > timerDelay && WiFi.status() == WL_CONNECTED) {
    readAndSendSensorData();
    lastTime = millis();
    
    Serial.print("Next reading in ");
    Serial.print(timerDelay / 1000);
    Serial.println(" seconds");
  }

  delay(10);
}
