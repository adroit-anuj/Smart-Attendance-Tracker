#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

#define RST_PIN 9
#define SS_PIN 10
#define DHT_PIN 2
#define DHT_TYPE DHT22
#define BUZZER_PIN 3

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);
DHT dht(DHT_PIN, DHT_TYPE);

int lastTempRead = 0;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Wire.begin();
  lcd.begin(16, 2);
  lcd.backlight();
  dht.begin();
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  lcd.setCursor(0, 0);
  lcd.print("Scan Prof Card");
  Serial.println("Arduino Ready - Waiting for Prof");
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidUID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidUID += String(rfid.uid.uidByte[i], HEX);
    }
    rfidUID.toUpperCase();

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ID: " + rfidUID.substring(0, 8));
    lcd.setCursor(0, 1);
    lcd.print("Scanned!");

    Serial.print("Student ID: ");
    Serial.println(rfidUID);

    String response = "";
    int startTime = millis();
    int retries = 0;
    const int MAX_RETRIES = 1000;
    while (millis() - startTime < 1500 && retries < MAX_RETRIES) {
      if (Serial.available() > 0) {
        response = Serial.readStringUntil('\n');
        break;
      }
      delay(150);
      retries++;
    }
    if (retries >= MAX_RETRIES) {
      Serial.println("Timeout waiting for Python response - Resetting");
      Serial.flush();
    }

    int beepDuration = 2000;
    if (response.startsWith("Rejected_")) {
      int freq = response.substring(9).toInt();
      tone(BUZZER_PIN, freq, 400);
      beepDuration -= 400;
    } else if (response.startsWith("Ignored_")) {
      int freq = response.substring(8).toInt();
      tone(BUZZER_PIN, freq, 200);
      beepDuration -= 200;
    } else if (response.startsWith("Logged_")) {
      int freq = response.substring(7).toInt();
      tone(BUZZER_PIN, freq, 600);
      beepDuration -= 600;
    } else if (response.startsWith("Tone_")) {
      int freq = response.substring(5).toInt();
      tone(BUZZER_PIN, freq, 200);
      beepDuration -= 200;
    } else {
      tone(BUZZER_PIN, 1000, 600);
      beepDuration -= 600;
    }

    delay(beepDuration);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Scan RFID Card");
    delay(100);

    rfid.PICC_HaltA();
    Serial.flush();

    int currentTime = millis();
    if (currentTime - lastTempRead >= 3000) {
      float temp = dht.readTemperature();
      float humid = dht.readHumidity();
      if (isnan(temp) || isnan(humid)) {
        Serial.println("!!!!!!DHT Error!!!!!!"); 
      } else {
        Serial.print("Temp: ");
        Serial.print(temp);
        Serial.print(" C | Humid: ");
        Serial.print(humid);
        Serial.println(" %");
      }
      lastTempRead = currentTime;
    }
  }
}
