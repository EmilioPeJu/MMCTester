#include "utils.h"


size_t bytes_to_hex(uint8_t *bytes, uint8_t *hex, size_t nbytes)
{
    size_t hex_size = 0;
    const char nibble_hex_map[] = {
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'a', 'b', 'c', 'd', 'e', 'f'
    };
    if (nbytes == 0)
        return 0;

    for (size_t i=0; i < nbytes; i++) {
        hex[hex_size++] = nibble_hex_map[bytes[i] >> 4];
        hex[hex_size++] = nibble_hex_map[bytes[i] & 0xf];
        hex[hex_size++] = ' ';
    }
    hex[hex_size - 1] = 0;
    return hex_size - 1;
}


bool is_hex(uint8_t digit)
{
    return (digit >= '0' && digit <= '9') || (digit >= 'a' && digit <= 'f');
}


char hex_to_nibble(uint8_t digit)
{
    if (digit >= '0' && digit <= '9')
        return digit - '0';
    else if (digit >= 'a' && digit <= 'f')
        return digit - 'a' + 10;
    else
        return 0;
}


size_t hex_to_bytes(uint8_t *hex, uint8_t *bytes, size_t len)
{
    bool first = true;
    char current_byte = 0;
    size_t nbytes = 0;
    for (size_t i=0; i < len; i++) {
        if (is_hex(hex[i])) {
            if (first) {
                current_byte = hex_to_nibble(hex[i]) << 4;
            } else {
                current_byte += hex_to_nibble(hex[i]);
                bytes[nbytes++] = current_byte;
            }
            first = !first;
        }
    }
    return nbytes;
}
