#include <Servo.h>

#define NUM_SERVOS 6
#define BUZZER_PIN 10
#define LETTER_DELAY 2000
#define SERIAL_CHECK_INTERVAL 10

Servo servos[NUM_SERVOS];
const int servoPins[NUM_SERVOS] = {A0, A1, A2, A3, A4, A5};

unsigned long lastSerialCheck = 0;
String inputString = "";
bool newData = false;

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(0); // posição de repouso
  }
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastSerialCheck >= SERIAL_CHECK_INTERVAL) {
    checkSerial();
    lastSerialCheck = currentMillis;
  }

  if (newData) {
    processBraille(inputString);
    inputString = "";
    newData = false;
    Serial.println("OK");
  }
}

void checkSerial() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      newData = true;
      return;
    } else {
      inputString += inChar;
    }
  }
}

void processBraille(String brailleData) {
  int length = brailleData.length();

  for (int i = 0; i < length; i += 6) {
    if (i + 5 >= length) break; // ignora se não for múltiplo de 6

    for (int j = 0; j < 6; j++) {
      char bit = brailleData.charAt(i + j);
      if (bit == '1') {
        servos[j].write(90); // ativa ponto
      } else {
        servos[j].write(0); // desativa ponto
      }
    }

    delay(LETTER_DELAY);

    // desativa todos os servos
    for (int j = 0; j < 6; j++) {
      servos[j].write(0);
    }

    // buzina no final da letra
    tone(BUZZER_PIN, 1000, 200); // 1kHz por 200ms
    delay(200);

    // delay de 1 segundo antes da próxima letra
    delay(1000);
  }
}
