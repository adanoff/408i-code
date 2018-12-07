#include "DualMC33926MotorShield.h"

#define L_PING 2
#define R_PING 13
#define M_PING 3

#define MAX_SPEED 400
#define STOP 0
//#define STRAIGHT_SPEED 75
//#define TURN_SPEED 75
#define STRAIGHT_SPEED 60 
#define TURN_SPEED 100
#define OFFWHEEL_SPEED (TURN_SPEED/2)
#define MAX_TURNS 8

#define GO
#define TURN

int turnsSinceLastForward = 0;

DualMC33926MotorShield md;
int serialReadInt() {
    while (!Serial.available()) {
    }
    int b = Serial.read();
    return b;
}

void stopIfFault()
{
  if (md.getFault())
  {
    Serial.println("fault");
    while(1);
  }
}

void forward() {
  #ifdef GO
    md.setM1Speed(STRAIGHT_SPEED);
    md.setM2Speed(STRAIGHT_SPEED);
    stopIfFault();
    turnsSinceLastForward = 0;
  #endif
}

void follow() {
  #ifdef GO
    md.setM1Speed(STRAIGHT_SPEED);
    md.setM2Speed(STRAIGHT_SPEED);
    stopIfFault();
    turnsSinceLastForward = 0;
  #endif
}

void halt() {
    md.setM1Speed(STOP);
    md.setM2Speed(STOP);
    stopIfFault();
}
void turnLeft() {
  #ifdef TURN
    md.setM1Speed(TURN_SPEED);
    md.setM2Speed(OFFWHEEL_SPEED);
    stopIfFault();
    turnsSinceLastForward++;
  #endif
}

void turnRight() {
  #ifdef TURN
    md.setM2Speed(TURN_SPEED);
    md.setM1Speed(OFFWHEEL_SPEED);
    stopIfFault();
    turnsSinceLastForward++;
  #endif
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  md.init();
}

long readPing(const int pin) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
  delayMicroseconds(5);
  digitalWrite(pin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pin, LOW);

  pinMode(pin, INPUT);
  return pulseIn(pin, HIGH);
}

void loop() {
//  long ldur, rdur, mdur;
//Serial.println("on");
    int inByte = 0;

  if (Serial.available()) {
    inByte = Serial.read();
    Serial.print("got byte: ");
    Serial.println(inByte);
    if (inByte < 200) {
    //PRINT("(move_code=%d)", inByte);
    //Serial.println(inByte);
    switch (inByte) {
      case 4: forward(); break;
      case 1: turnLeft(); break;
      case 2: turnRight(); break;
      case 3: halt(); break;
     // default: halt(); break;
    }
  }
  }

  delay(50);
  //delay(100);
}
