#include <AbsMouse.h> // INCLUDE THE LIBRARY WITH IDE
#include "string.h"

String triggerString = "CLIKK";
String stringIn;

void clickMous() {
  AbsMouse.press(MOUSE_LEFT);
  AbsMouse.release(MOUSE_LEFT);
}

void setup() {
  AbsMouse.init(1920, 1080);
  Serial.begin(9600);
  Serial.setTimeout(10);
}

void loop() {
  if (Serial.available() >= 1) {
    stringIn = Serial.readString();

    if (stringIn == triggerString) {
      clickMous();
      Serial.println("mouse lick");
    }
  }
}
