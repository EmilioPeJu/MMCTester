#include <stdio.h>
#include "minunit.h"
#include "utils.h"

int tests_run = 0;


static char *test_is_hex()
{
    mu_assert("is_hex: 3 should be hex", is_hex('3') == true);
    mu_assert("is_hex: a should be hex", is_hex('a') == true);
    mu_assert("is_hex: x should not be hex", is_hex('x') == false);
    return NULL;
}


static char *test_bytes_to_hex()
{
    uint8_t input[] = "\x31\x42\x63\xa4";
    uint8_t output[16];
    size_t hex_size = bytes_to_hex(input, output, 4);
    mu_assert("bytes_to_hex: incorrect size returned", hex_size == 11);
    mu_assert("bytes_to_hex: incorrect hex string",
        strcmp((char *) output, "31 42 63 a4") == 0);
    return NULL;
}


static char *test_hex_to_nibble()
{
    mu_assert("hex_to_nibble: f != 15", hex_to_nibble('f') == 15);
    mu_assert("hex_to_nibble: 1 != 1", hex_to_nibble('1') == 1);
    mu_assert("hex_to_nibble: a != 10", hex_to_nibble('a') == 10);
    return NULL;
}


static char *test_hex_to_bytes()
{
    uint8_t input[] = "a0 15 18 ff";
    uint8_t output[8];
    size_t nbytes = hex_to_bytes(input, output, 11);
    mu_assert("hex_to_bytes: incorrect output size", nbytes == 4);
    mu_assert("hex_to_bytes: unexpected output",
        memcmp((char *) output, "\xa0\x15\x18\xff", 4) == 0);
    return NULL;
}


static char *all_tests()
{
    mu_run_test(test_is_hex);
    mu_run_test(test_bytes_to_hex);
    mu_run_test(test_hex_to_nibble);
    mu_run_test(test_hex_to_bytes);
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
