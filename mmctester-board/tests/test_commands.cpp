#include <stdio.h>
#include "Arduino.h"
#include "minunit.h"
#include "commands.h"

int tests_run = 0;


static char *test_pin_mode()
{
    uint8_t reply[32];
    uint8_t command[] = "\x01\x0d\x01";
    size_t n = execute_command(command, 3, reply);
    mu_assert("Invalid response length", n == 2);
    mu_assert("Invalid command byte in response", reply[0] == 0x01);
    mu_assert("Invalid response", reply[1] == OK);
    mu_assert("Pin mode pin not valid", _last_call_pin == 13);
    mu_assert("Pin mode mode not valid", _last_call_mode == 1);
    return NULL;
}


static char *test_dig_write()
{
    uint8_t reply[32];
    uint8_t command[] = "\x02\x03\x00";
    size_t n = execute_command(command, 3, reply);
    mu_assert("Invalid response length", n == 2);
    mu_assert("Invalid command byte in response", reply[0] == 0x02);
    mu_assert("Invalid response", reply[1] == OK);
    mu_assert("Dig write pin not valid", _last_call_pin == 3);
    mu_assert("Dig write val not valid", _last_call_val == 0);
    return NULL;
}


static char *test_dig_read()
{
    uint8_t reply[32];
    uint8_t command[] = "\x03\x0f";
    size_t n = execute_command(command, 2, reply);
    mu_assert("Invalid response length", n == 3);
    mu_assert("Invalid command byte in response", reply[0] == 0x03);
    mu_assert("Invalid response", reply[1] == OK);
    mu_assert("Invalid read value", reply[2] == _digital_read_value);
    mu_assert("Dig read pin not valid", _last_call_pin == 15);
    return NULL;
}


static char *test_an_write()
{
    uint8_t reply[32];
    uint8_t command[] = "\x04\x0b\x51";
    size_t n = execute_command(command, 3, reply);
    mu_assert("Invalid response length", n == 2);
    mu_assert("Invalid command byte in response", reply[0] == 0x04);
    mu_assert("Invalid response", reply[1] == OK);
    mu_assert("An write pin not valid", _last_call_pin == 11);
    mu_assert("An write val not valid", _last_call_val == 0x51);
    return NULL;
}


static char *test_an_read()
{
    uint8_t reply[32];
    uint8_t command[] = "\x05\x0e";
    size_t n = execute_command(command, 2, reply);
    mu_assert("Invalid response length", n == 4);
    mu_assert("Invalid command byte in response", reply[0] == 0x05);
    mu_assert("Invalid response", reply[1] == OK);
    uint16_t val = reply[2] | (reply[3] << 8);
    mu_assert("Invalid read value", val == _analog_read_value);
    mu_assert("Dig read pin not valid", _last_call_pin == 14);
    return NULL;
}


static char *all_tests()
{
    mu_run_test(test_pin_mode);
    mu_run_test(test_dig_write);
    mu_run_test(test_dig_read);
    mu_run_test(test_an_write);
    mu_run_test(test_an_read);
    return NULL;
}


int main()
{
    char *result = all_tests();
    if (result) {
        printf("%s\n", result);
    } else {
        printf("ALL PASSED\n");
    }
    printf("Tests run: %d\n", tests_run);
    return result ? 1 : 0;
}
