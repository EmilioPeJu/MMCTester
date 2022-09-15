#include "Arduino.h"

uint8_t _last_call_pin;
uint8_t _last_call_mode;
uint8_t _last_call_val;
int _analog_read_value = 0x1234;
int _digital_read_value = 0x1;


void pinMode(uint8_t pin, uint8_t mode)
{
    _last_call_pin = pin;
    _last_call_mode = mode;
}

void digitalWrite(uint8_t pin, uint8_t val)
{
    _last_call_pin = pin;
    _last_call_val = val;
}

int digitalRead(uint8_t pin)
{
    _last_call_pin = pin;
    return _digital_read_value;
}

void analogWrite(uint8_t pin, int val)
{
    _last_call_pin = pin;
    _last_call_val = val;
}

int analogRead(uint8_t pin)
{
    _last_call_pin = pin;
    return _analog_read_value;
}
