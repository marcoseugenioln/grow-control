#include <ESP8266WiFi.h>
#include <PubSubClient.h>
 
// Connect to the WiFi
const char* ssid = "MARCOS_E_NICOLE*";                 //add your wifi Name
const char* password = "Dv010400";             //Add your wifi password here
const char* mqtt_server = "192.168.1.8"; //add the ip address of your raspberry pi you can get the ip address of your Pi by typing ifconfig in terminal
 
WiFiClient espClient;
PubSubClient client(espClient);
 
const byte relay=12; 
const byte led_pin=13;
 
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  for (int i=0;i<length;i++) {
    char receivedChar = (char)payload[i];
    Serial.print(receivedChar);
    
    if (receivedChar == '1'){
      digitalWrite(relay, HIGH);
    }
    else if (receivedChar == '0'){
      digitalWrite(relay, LOW);
    }
  }
  Serial.println();
}
 
 
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("Client")) {
      Serial.println("connected");
      // ... and subscribe to topic
      client.subscribe("m_humidifier_cmd");             // led is the topic which we are going to add in rapberry pi
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
 
void setup()
{
  Serial.begin(9600);
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
 
  pinMode(led_pin, OUTPUT);
  pinMode(relay,OUTPUT);
  digitalWrite(led_pin, LOW);
  digitalWrite(relay, LOW);
}
 
void loop()
{
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
