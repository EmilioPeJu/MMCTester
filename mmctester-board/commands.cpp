#include <Arduino.h>

#include "commands.h"

#define COMMAND_PIN_MODE 0x01
#define COMMAND_DIG_WRITE 0x02
#define COMMAND_DIG_READ 0x03
#define COMMAND_AN_WRITE 0x04
#define COMMAND_AN_READ 0x05


// byte 0: pin number
// byte 1: mode (INPUT = 0, OUTPUT = 1, INPUT_PULLUP = 2)
static size_t pin_mode_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    if (nbytes != 2) {
        reply[0] = ERR_INVALID_FORMAT;
        return 1;
    }
    pinMode(buffer[0], buffer[1]);
    reply[0] = OK;
    return 1;
}


// byte 0: pin number
// byte 1: pin output (LOW = 0, HIGH = 1)
static size_t dig_write_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    if (nbytes != 2) {
        reply[0] = ERR_INVALID_FORMAT;
        return 1;
    }
    digitalWrite(buffer[0], buffer[1]);
    reply[0] = OK;
    return 1;
}


// byte 0: pin number
static size_t dig_read_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    if (nbytes != 1) {
        reply[0] = ERR_INVALID_FORMAT;
        return 1;
    }
    reply[0] = OK;
    reply[1] = digitalRead(buffer[0]);
    return 2;
}

// byte 0: pin number
// byte 1: duty cicle
static size_t an_write_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    if (nbytes != 2) {
        reply[0] = ERR_INVALID_FORMAT;
        return 1;
    }
    analogWrite(buffer[0], buffer[1]);
    reply[0] = OK;
    return 1;
}

// byte 0: pin number
static size_t an_read_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    if (nbytes != 1) {
        reply[0] = ERR_INVALID_FORMAT;
        return 1;
    }
    int val = analogRead(buffer[0]);
    reply[0] = OK;
    reply[1] = val & 0xff;
    reply[2] = (val>>8) & 0xff;
    return 3;
}


struct command_entry {
    uint8_t command_byte;
    size_t (*command_func)(uint8_t *buffer, size_t nbytes, uint8_t *reply);
} command_table[] = {
    {COMMAND_PIN_MODE, pin_mode_command},
    {COMMAND_DIG_WRITE, dig_write_command},
    {COMMAND_DIG_READ, dig_read_command},
    {COMMAND_AN_WRITE, an_write_command},
    {COMMAND_AN_READ, an_read_command},
    {0, NULL}
};


size_t execute_command(uint8_t *buffer, size_t nbytes, uint8_t *reply)
{
    size_t i = 0;
    while (command_table[i].command_byte) {
        if (buffer[0] == command_table[i].command_byte) {
            reply[0] = buffer[0];
            // call command function skipping command byte in buffer
            return command_table[i].command_func(buffer + 1, nbytes - 1, reply + 1) + 1;
        }
        i++;
    }
    reply[0] = ERR_NO_COMMAND;
    return 1;
}

