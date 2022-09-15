#ifndef _UTILS_H
#define _UTILS_H

#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

size_t bytes_to_hex(uint8_t *bytes, uint8_t *hex, size_t nbytes);

bool is_hex(uint8_t digit);

char hex_to_nibble(uint8_t digit);

size_t hex_to_bytes(uint8_t *hex, uint8_t *bytes, size_t len);

#endif
