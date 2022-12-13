#include <WiFi.h>
#include <HTTPClient.h>

const int pin_sensor = 34; //PINO UTILIZADO PELO SENSOR
//const int pin_bomb   = 14;

const String HTTP_METHOD = "GET"; // or "POST"
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

void setup(){
  
  Serial.begin(9600); //INICIALIZA A SERIAL

  WiFi.begin(ssid, password);             // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid);

  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(500);
    Serial.print('.');
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());

  pinMode(pin_bomb, OUTPUT);
  
  Serial.println("Lendo a umidade do solo..."); //IMPRIME O TEXTO NO MONITOR SERIAL
  delay(2000); //INTERVALO DE 2 SEGUNDOS
}

void loop(){  

  while(!timeClient.update()) {
    timeClient.forceUpdate();
  }
  
  read_value = constrain(analogRead(pin_sensor),a_read_wet,a_read_dry); //MANTÉM read_value DENTRO DO INTERVALO (ENTRE a_read_wet E a_read_dry)
  read_value = map(read_value,a_read_wet,a_read_dry,max_u,min_u); //EXECUTA A FUNÇÃO "map" DE ACORDO COM OS PARÂMETROS PASSADOS
  

  delay(1000); 
  delay_count+=1000;
  
  count += read_value;

  if(int(delay_count) >= 60000){

    int su_1 = count / 60;
    
    Serial.print("su1: "); 
    Serial.print(su_1);
    Serial.print("%\n");
        
    String url = server_name + "?su_1=" + String(su_1) + "&su_2=0&su_3=0&su_4=0&au=0&t=0;"
    Serial.print(url);
    
    http.begin(url.c_str());
    int response = http.GET();

    Serial.print("\n");
    
    if (response > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(response);
      String payload = http.getString();
      Serial.println(payload);
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