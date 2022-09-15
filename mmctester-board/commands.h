#ifndef _COMMANDS_H_
#define _COMMANDS_H_
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define PONG_ASCII_MSG "00\n"
#define RESET_ASCII_MSG "00 FF\n"
#define OK_ASCII_MSG "00 80\n"
#define ERR_INVALID_FORMAT_ASCII_MSG "00 81\n"
#define ERR_INVALID_MSG_ASCII_MSG "00 82\n"
#define ERR_NO_DATA_ASCII_MSG "00 83\n"
#define ERR_I2C_MAX_RETRIES_ASCII_MSG "00 84\n"
#define ERR_NO_COMMAND_ASCII_MSG "00 85\n"
#define ERR_TOO_LONG_ASCII_MSG "00 86\n"

#define OK 0x80
#define ERR_INVALID_FORMAT 0x81
#define ERR_INVALID_MSG 0x82
#define ERR_NO_DATA 0x83
#define ERR_I2C_MAX_RETRIES 0x84
#define ERR_NO_COMMAND 0x85
#define ERR_TOO_LONG 0x86

size_t execute_command(uint8_t *buffer, size_t nbytes, uint8_t *reply);

#endif
