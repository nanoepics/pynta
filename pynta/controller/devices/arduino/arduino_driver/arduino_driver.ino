#include <DallasTemperature.h>
#include <OneWire.h>
#include <DHT.h>
#define ONE_WIRE_BUS 2
#define DHTPIN 7     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define motor1Pin 3 // H-bridge pin2
#define motor2Pin 4 // H-bridge pin 7
#define motor3Pin 11 // H-bridge pin 10
#define motor4Pin 12 // H-bridge pin 15
#define speedPin1 9 // H-bridge enable pin 1
#define speedPin2 10 // H-bridge enable pin 9

DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress insideThermometer;

String serialString;

int motor;
int direction;
int speed = 0; //Set start speed to be 0
float temp;
float hum_dht;
int temp_channel;

void setup() {
  // Load serial monitor
  Serial.begin (19200);
  // set all the other pins you're using as outputs:
  pinMode(motor1Pin, OUTPUT);
  pinMode(motor2Pin, OUTPUT);
  pinMode(motor3Pin, OUTPUT);
  pinMode(motor4Pin, OUTPUT);
  pinMode(speedPin1, OUTPUT);
  pinMode(speedPin2, OUTPUT);
  sensors.begin();
  dht.begin();
  sensors.getAddress(insideThermometer, 0);
  sensors.setResolution(insideThermometer, 11);
}

void loop() {
  serialString = "";
  while (Serial.available()) {
//    delay(5);
//    if (Serial.available() > 0) {
      char c = Serial.read();
      serialString += c;
//    }
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
      Serial.println(serialString.substring(4, 5));
    } else { // Move the motor

      motor = serialString.substring(0, 1).toInt(); // Number of motor to move
      direction = serialString.substring(1, 2).toInt(); // Direction to move the motor
      speed = serialString.substring(2, 5).toInt(); // Speed for the PWM

      // if the switch is high, motor 1 will turn on one direction:
      if (direction == 0) {
        if (motor == 1) {
          digitalWrite(motor1Pin, LOW); // set leg 1 of the H-bridge low
          digitalWrite(motor2Pin, HIGH); // set leg 2 of the H-bridge high
          analogWrite(speedPin1, speed);
        } else if (motor == 2) {
          digitalWrite(motor3Pin, LOW); // set leg 1 of the H-bridge low
          digitalWrite(motor4Pin, HIGH); // set leg 2 of the H-bridge high
          analogWrite(speedPin2, speed);
        }
      } else if (direction == 1) {
        if (motor == 1) {
          digitalWrite(motor1Pin, HIGH); // set leg 1 of the H-bridge high
          digitalWrite(motor2Pin, LOW); // set leg 2 of the H-bridge low
          analogWrite(speedPin1, speed);
        } else if (motor == 2) {
          digitalWrite(motor3Pin, HIGH); // set leg 1 of the H-bridge low
          digitalWrite(motor4Pin, LOW); // set leg 2 of the H-bridge high
          analogWrite(speedPin2, speed);
        }
      }
      delay(1);
      Serial.println(speed);
    }
  }
  delay(2);
}
