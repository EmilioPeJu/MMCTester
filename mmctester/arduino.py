#!/usr/bin/env python
LOW = 0x0
HIGH = 0x1
INPUT = 0x0
OUTPUT = 0x1
INPUT_PULLUP = 0x2
PIN_A0 = 14
PIN_A1 = 15
PIN_A2 = 16
PIN_A3 = 17
PIN_A4 = 18
PIN_A5 = 19
PIN_A6 = 20
PIN_A7 = 21


class ArduinoLocalCommand(object):
    OK = 0x80
    COMMAND_PIN_MODE = 0x1
    COMMAND_DIG_WRITE = 0x02
    COMMAND_DIG_READ = 0x03
    COMMAND_AN_WRITE = 0x04
    COMMAND_AN_READ = 0x05

    def __init__(self, send, recv, local_address=0x0):
        self.send = send
        self.recv = recv
        self.local_address = local_address

    def send_and_receive(self, command):
        self.send(command)
        return self.recv()

    def pin_mode(self, pin, mode):
        command = bytearray(
            (self.local_address, self.COMMAND_PIN_MODE, pin, mode))
        ans = self.send_and_receive(bytes(command))
        if ans[1] != self.COMMAND_PIN_MODE or ans[2] != self.OK:
            raise IOError(f'Invalid answer: {ans}')

    def digital_write(self, pin, val):
        command = bytearray(
            (self.local_address, self.COMMAND_DIG_WRITE, pin, val))
        ans = self.send_and_receive(bytes(command))
        if ans[1] != self.COMMAND_DIG_WRITE or ans[2] != self.OK:
            raise IOError(f'Invalid answer: {ans}')

    def digital_read(self, pin):
        command = bytearray(
            (self.local_address, self.COMMAND_DIG_READ, pin))
        ans = self.send_and_receive(bytes(command))
        if ans[1] != self.COMMAND_DIG_READ or ans[2] != self.OK:
            raise IOError(f'Invalid answer: {ans}')
        return ans[3]

    def analog_write(self, pin, val):
        command = bytearray(
            (self.local_address, self.COMMAND_AN_WRITE, pin, val))
        ans = self.send_and_receive(bytes(command))
        if ans[1] != self.COMMAND_AN_WRITE or ans[2] != self.OK:
            raise IOError(f'Invalid answer: {ans}')

    def analog_read(self, pin):
        command = bytearray(
            (self.local_address, self.COMMAND_AN_READ, pin))
        ans = self.send_and_receive(bytes(command))
        if ans[1] != self.COMMAND_AN_READ or ans[2] != self.OK:
            raise IOError(f'Invalid answer: {ans}')
        return (ans[3] & 0xff) | (ans[4] << 8)
