#!/usr/bin/env python


def set_led(ipmi, led_function, on_duration):
    return ipmi.send_message_with_name('SetFruLedState', fru_id=0, led_id=0,
                                       led_function=led_function,
                                       on_duration=on_duration, color=0xf)


def set_led_off(ipmi):
    return set_led(ipmi, 0x0, 0x0)  # off override


def set_led_on(ipmi):
    return set_led(ipmi, 0xff, 0x0)  # on override


def set_led_short(ipmi):
    return set_led(ipmi, 0x5a, 0xa)  # short blink


def set_led_long(ipmi):
    return set_led(ipmi, 0xa, 0x5a)  # long blink
