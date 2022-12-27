#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

const int pin_su_sensor  = 34; 
const int pin_led_net = 32;
const int pin_led_water = 35;
const int pin_led_req = 34;
const int pin_dht     = 2;
const int pin_bomb    = 13;

const String server_name   = "http://192.168.1.66:3000/insert";

int read_value; 
int a_read_dry = 1040; 
int a_read_wet = 150; 
int min_u = 0; 
int max_u = 100; 

HTTPClient http;

const char* ssid = "Marcos Eugênio 2.4G";
const char* password = "#Dv010400";

int delay_count = 0;
int count = 0;

DHT dht(pin_dht, DHT11);

void setup(){
  
  Serial.begin(9600);

  pinMode(pin_led_req, OUTPUT);
  pinMode(pin_led_net, OUTPUT);
  dht.begin();

  WiFi.begin(ssid, password);             
  Serial.print("Connecting to ");
  Serial.print(ssid);

  while (WiFi.status() != WL_CONNECTED) { 
    delay(500);
    digitalWrite(pin_led_net, HIGH);    
    Serial.print('.');
    digitalWrite(pin_led_net, LOW);    
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());
  digitalWrite(pin_led_net, HIGH);   

  pinMode(pin_bomb, OUTPUT);
  
  Serial.println("Lendo a umidade do solo...");
  delay(2000); 
}

void loop(){  

  if( WiFi.status() != WL_CONNECTED){
   digitalWrite(pin_led_net, LOW);
  }
  else{
    digitalWrite(pin_led_net, HIGH);    
  }
       
  digitalWrite(pin_bomb, HIGH);
  read_value = constrain(analogRead(pin_su_sensor),a_read_wet,a_read_dry); //MANTÉM read_value DENTRO DO INTERVALO (ENTRE a_read_wet E a_read_dry)
  read_value = map(read_value,a_read_wet,a_read_dry,max_u,min_u); //EXECUTA A FUNÇÃO "map" DE ACORDO COM OS PARÂMETROS PASSADOS
  
  Serial.write(int(read_value));
  Serial.write("\n");
  
  delay(1000); 
  delay_count+=1000;
  
  
  count += read_value;

  if(int(delay_count) >= 60000){
    

    

    int su_1 = count / 60;
    float au = dht.readHumidity();
    float t = dht.readTemperature();
    
    Serial.print("Soil Umidity: "); 
    Serial.print(su_1);
    Serial.print(" Air Humidity: ");
    Serial.println(au);    
    Serial.print(" Temperature: ");
    Serial.print(t);
    Serial.print("ºC\n");
    
    String url = server_name + "?su_1=" + String(su_1) + "&su_2=0&su_3=0&su_4=0&au=" + String(au) + "&t=" + String(t);
    Serial.print(url);
    
    http.begin(url.c_str());

    digitalWrite(pin_led_req, HIGH);
    int response = http.GET();
    digitalWrite(pin_led_req, LOW);

    Serial.print("\n");
    
    if (response > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(response);
      String payload = http.getString();
      Serial.println(payload);

      switch(payload.toInt()){

      case 1:
        Serial.write("Watering plants.");
      } 
    }
    
    else {
        Serial.print("Error code: ");
        Serial.println(response);
    }

    http.end();
    Serial.print("\n");

    delay_count = 0;
    count = 0;   
    

  } 
} 