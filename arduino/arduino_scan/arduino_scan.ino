#include <Servo.h>

const byte SERVO_PIN = 9;
const byte TRIG_PIN  = 2;
const byte ECHO_PIN  = 3;

const int  MIN_ANG   = 20;
const int  MAX_ANG   = 160;
const int  STEP      = 2;
const long TIME_BETWEEN_SWEEPS_MS = 30;

Servo myServo;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  myServo.attach(SERVO_PIN);
}

float readUltrasonicCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  return duration * 0.0343 / 2.0;
}

void loop() {
  static bool forward = true;
  for (int ang = forward ? MIN_ANG : MAX_ANG;
           forward ? ang <= MAX_ANG : ang >= MIN_ANG;
           ang += forward ? STEP : -STEP) {

    myServo.write(ang);
    delay(30);

    float dist_cm = readUltrasonicCM();
    if (dist_cm > 0) {
      Serial.print(ang);
      Serial.print(',');
      Serial.println(dist_cm / 100.0, 3);   // metres
    }
    delay(TIME_BETWEEN_SWEEPS_MS);
  }
  forward = !forward;
}