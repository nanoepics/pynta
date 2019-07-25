#include <DallasTemperature.h>
#include <OneWire.h>
#include <DHT.h>
#define ONE_WIRE_BUS 2
#define DHTPIN 7     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define motor1_Pin1 3 // H-bridge pin2
#define motor1_Pin2 4 // H-bridge pin 7
#define motor2_Pin1 11 // H-bridge pin 10
#define motor2_Pin2 12 // H-bridge pin 15
#define motor1_enable 9 // H-bridge enable pin 1
#define motor2_enable 10 // H-bridge enable pin 9
#define motor_delay 5 // Delay when moving the motor
DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress insideThermometer;

String serialString;

int motor;
int direction;
float temp;
float hum_dht;
int temp_channel;

void setup() {
  // Load serial monitor
  Serial.begin (19200);
  // set all the other pins you're using as outputs:
  pinMode(motor1_Pin1, OUTPUT);
  pinMode(motor1_Pin2, OUTPUT);
  pinMode(motor2_Pin1, OUTPUT);
  pinMode(motor2_Pin2, OUTPUT);
  pinMode(motor1_enable, OUTPUT);
  pinMode(motor2_enable, OUTPUT);
  sensors.begin();
  dht.begin();
  sensors.getAddress(insideThermometer, 0);
  sensors.setResolution(insideThermometer, 11);
}

void loop() {
  serialString = "";
  while (Serial.available()) {
      char c = Serial.read();
      serialString += c;
  }
  Serial.flush();
  delay(100);
  if (serialString.length() > 0) {
    if (serialString.startsWith("t")) { // Read the temp
      temp_channel = serialString.substring(4, 5).toInt();
      if (temp_channel == 0) {
        temp = dht.readTemperature();
        Serial.println(temp);
      } else if (temp_channel == 1) {
        sensors.requestTemperatures(); // Send the command to get temperature readings
        delay(1000);
        temp = sensors.getTempCByIndex(0);
        Serial.println(temp);
      }
    } else { // Move the motor

      motor = serialString.substring(0, 1).toInt(); // Number of motor to move
      direction = serialString.substring(1, 2).toInt(); // Direction to move the motor
      
      if (direction == 0) {
        if (motor == 1) {
          digitalWrite(motor1_Pin1, LOW); 
          digitalWrite(motor1_Pin2, HIGH);
          digitalWrite(motor1_enable, HIGH);
          delay(motor_delay);
          digitalWrite(motor1_enable, LOW);
        } else if (motor == 2) {
          digitalWrite(motor2_Pin1, LOW); 
          digitalWrite(motor2_Pin2, HIGH); 
          digitalWrite(motor2_enable, HIGH);
          delay(motor_delay);
          digitalWrite(motor2_enable, LOW);
        }
      } else if (direction == 1) {
        if (motor == 1) {
          digitalWrite(motor1_Pin1, HIGH);
          digitalWrite(motor1_Pin2, LOW);
          digitalWrite(motor1_enable, HIGH);
          delay(motor_delay);
          digitalWrite(motor1_enable, LOW);
        } else if (motor == 2) {
          digitalWrite(motor2_Pin1, HIGH);
          digitalWrite(motor2_Pin2, LOW);
          digitalWrite(motor2_enable, HIGH);
          delay(motor_delay);
          digitalWrite(motor2_enable, LOW); 
        }
      }
      delay(1);
    }
  }
  delay(2);
}
