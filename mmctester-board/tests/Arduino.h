#ifndef _ARDUINO_H_
#define _ARDUINO_H_
#include <stdint.h>

extern uint8_t _last_call_pin;
extern uint8_t _last_call_mode;
extern uint8_t _last_call_val;
extern int _analog_read_value;
extern int _digital_read_value;

void pinMode(uint8_t pin, uint8_t mode);
void digitalWrite(uint8_t pin, uint8_t val);
int digitalRead(uint8_t pin);
void analogWrite(uint8_t pin, int val);
int analogRead(uint8_t pin);

#endif
