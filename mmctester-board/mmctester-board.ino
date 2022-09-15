#include <Wire.h>
#include <util/atomic.h>

#include "utils.h"
#include "commands.h"

#define IPMB_ADDR 0x20
#define LOCAL_ADDR 0x00

// TODO: make sure that this is not overpassed anywhere
#define MAX_BINARY_MSG_SIZE 32
#define MAX_I2C_MSG_SIZE MAX_BINARY_MSG_SIZE
#define MAX_SERIAL_MSG_SIZE (MAX_I2C_MSG_SIZE*3)
#define SERIAL_BAUDRATE 115200
#define MAX_IPMB_SEND_RETRIES 3
#define TERMINATOR 10

size_t i2c_nbytes = 0;
uint8_t i2c_rx_buffer[MAX_I2C_MSG_SIZE];


// serial message format:
// "00 01 02 0a 0b 0c\n"
static size_t format_serial_message(uint8_t *inbuf, uint8_t *outbuf, size_t nbytes)
{
    size_t hex_size = bytes_to_hex(inbuf, outbuf, nbytes);
    outbuf[hex_size] = 10;
    return hex_size + 1;
}


// Receiving more than 32 bytes will crash the board,
// it's probably a limitation of the i2c peripheral
void i2c_on_receive(int nbytes)
{
    i2c_rx_buffer[0] = IPMB_ADDR;
    for (size_t i=1; i < nbytes + 1; i++) {
        if (i >= MAX_I2C_MSG_SIZE)
            Wire.read(); // flush remaining
        else
            i2c_rx_buffer[i] = Wire.read();
    }
    i2c_nbytes = min(nbytes + 1, MAX_I2C_MSG_SIZE);
}


void setup()
{
    // Initilise I2C, in arduino UNO pins A4(SDA) and A5(SCL)
    Wire.begin(IPMB_ADDR>>1);

    Wire.onReceive(i2c_on_receive);

    // Initilise serial, in arduino UNO, pins 0(RX) and 1(TX)
    Serial.begin(SERIAL_BAUDRATE);
    Serial.print(RESET_ASCII_MSG);
}


static void handle_i2c_command(uint8_t *buffer, size_t nbytes)
{
    uint8_t retries = 0;
    size_t sent = 0;
    if (nbytes > MAX_I2C_MSG_SIZE) {
        Serial.print(ERR_TOO_LONG_ASCII_MSG);
        return;
    }
    while (sent < nbytes - 1) {
        Wire.beginTransmission(buffer[0]>>1);
        sent = Wire.write(&buffer[1], nbytes - 1);
        Wire.endTransmission();
        if (++retries >= MAX_IPMB_SEND_RETRIES) {
            Serial.print(ERR_I2C_MAX_RETRIES_ASCII_MSG);
            break;
        }
  }
}


// request format: <LOCAL_ADDR> <COMMAND_BYTE> .... rest
// response format: <LOCAL_ADDR> <COMMAND_BYTE> <STATUS_BYTE> .. rest
static void handle_local_command(uint8_t *buffer, size_t nbytes)
{
    uint8_t error_code = 0;
    uint8_t reply[MAX_BINARY_MSG_SIZE];
    uint8_t tx_buffer[MAX_SERIAL_MSG_SIZE];
    // ping command
    if (nbytes == 1) {
        Serial.print(PONG_ASCII_MSG);
        return;
    }
    reply[0] = LOCAL_ADDR;
    // execute command skipping address byte
    size_t reply_nbytes = execute_command(buffer + 1, nbytes - 1, reply + 1);
    size_t tx_size = format_serial_message(reply, tx_buffer, reply_nbytes + 1);
    Serial.write(tx_buffer, tx_size);
}


static void forward_i2c_to_serial_if_needed()
{
    uint8_t tx_buffer[MAX_SERIAL_MSG_SIZE];
    size_t nbytes;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        nbytes = i2c_nbytes;
        i2c_nbytes = 0;
    }
    if (nbytes) {
        // we assume this finishes before there is a new i2c interrupt
        size_t tx_size = format_serial_message(i2c_rx_buffer, tx_buffer, nbytes);
        Serial.write(tx_buffer, tx_size);
    }
}


static void process_serial_message(uint8_t *hex_buffer, size_t hex_nbytes)
{
    uint8_t buffer[MAX_BINARY_MSG_SIZE];
    size_t nbytes = hex_to_bytes(hex_buffer, buffer, hex_nbytes);
    if (nbytes == 0) {
      Serial.print(ERR_NO_DATA_ASCII_MSG);
      return;
    }
    if (buffer[0] == LOCAL_ADDR) {
      handle_local_command(buffer, nbytes);
    } else {
      handle_i2c_command(buffer, nbytes);
    }
}


static void process_serial()
{
    static size_t len = 0;
    static uint8_t rx_buffer[MAX_SERIAL_MSG_SIZE];
    uint8_t current_byte = 0;
    if (Serial.available()) {
        if (len >= MAX_SERIAL_MSG_SIZE) {
            Serial.print(ERR_TOO_LONG_ASCII_MSG);
            len = 0;
        } else {
            rx_buffer[len++] = current_byte = (uint8_t) Serial.read();
            if (current_byte == TERMINATOR) {
                process_serial_message(rx_buffer, len);
                len = 0;
            }
        }
    }
}


void loop()
{
    for (;;) {
        forward_i2c_to_serial_if_needed();
        process_serial();
    }
}
