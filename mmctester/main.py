#!/usr/bin/env python
import argparse
import logging
import os
import select
import sys
import time

import pyipmi

from collections import deque

from pyipmi.sensor import SENSOR_TYPE_MODULE_HOT_SWAP

from mmctester.arduino import (HIGH, LOW, INPUT, OUTPUT, INPUT_PULLUP,
                               PIN_A0)
from mmctester.interface import MMCTesterBoard
from mmctester.led import set_led_long, set_led_off, set_led_short
from mmctester.tui import TuiManager


DEFAULT_TARGET = 0xa2


class Main(object):
    def __init__(self, port, target, pin_pg, pin_hs):
        self.pin_pg = pin_pg
        self.pin_hs = pin_hs
        self.interface = MMCTesterBoard(port=port)
        self.ipmi = pyipmi.create_connection(self.interface)
        self.ipmi.target = pyipmi.Target(target)
        self.sdr = list(self.ipmi.device_sdr_entries())
        self.help_lines = [
            "Keys:  "
            + ("1 => set HS HIGH    2 => set HS LOW   "
                if self.pin_hs is not None else "") +
            + "q => quit"
        ]

        self.device_lines = []
        self.fru_lines = []
        self.sensor_lines = []
        self.log_lines = []
        self.payload_lines = []
        self.max_log_size = 8
        self.tui = TuiManager()
        self.tui.add_draw_callback(self.draw)
        self.tui.add_key_callback(self.on_key_press)
        self.want_quit = False

    def draw(self):
        self.tui.clear()
        self.tui.add_str(
            ["HELP"] +
            self.help_lines +
            ["===", "DEVICE"] +
            self.device_lines +
            ["===", "FRU"] +
            self.fru_lines +
            ["===", "SENSORS"] +
            self.sensor_lines +
            ["===", "PAYLOAD"] +
            self.payload_lines +
            ["===", "LOGS"] +
            self.log_lines)

    def on_key_press(self, key):
        if key == ord('q'):
            self.want_quit = True
        elif key == ord('1') and self.pin_hs is not None:
            self.interface.arduino.digital_write(self.pin_hs, HIGH)
        elif key == ord('2') and self.pin_hs is not None:
            self.interface.arduino.digital_write(self.pin_hs, LOW)

    def log(self, line):
        ts = time.strftime('%H:%M:%S - ')
        self.log_lines.append(ts + line)
        excess = len(self.log_lines) - self.max_log_size
        if excess > 0:
            self.log_lines = self.log_lines[excess:]

    def show_general_info(self):
        device_id = self.ipmi.get_device_id()
        self.device_lines = [
            f"Device ID: {device_id.device_id}",
            f"Device Rev: {device_id.revision}",
            f"Firmware Rev: {device_id.fw_revision}"
        ]
        fru = self.ipmi.get_fru_inventory(0)
        product = fru.product_info_area
        self.fru_lines = []
        if product:
            self.fru_lines.extend([
                f"Product manufacturer {product.manufacturer}",
                f"Product name {product.name}",
                f"Product part {product.part_number}",
                f"Product version {product.version}",
                f"Product SN {product.serial_number}"
            ])

    def enable_payload(self):
        if self.pin_pg is not None:
            self.ipmi.interface.arduino.digital_write(self.pin_pg, HIGH)

    def disable_payload(self):
        if self.pin_pg is not None:
            self.ipmi.interface.arduino.digital_write(self.pin_pg, LOW)

    def process_handle_closed(self):
        self.log("Handle closed")
        set_led_long(self.ipmi)
        self.log("Negotiating power")
        self.draw()
        time.sleep(5)
        set_led_off(self.ipmi)
        self.log("Enabling payload")
        self.enable_payload()

    def process_handle_open(self):
        self.log("Handle open")
        set_led_short(self.ipmi)
        self.draw()
        time.sleep(5)
        set_led_off(self.ipmi)
        self.log("Disabling payload")
        self.disable_payload()

    def show_sensors(self):
        self.sensor_lines = []
        for sdr_entry in self.sdr:
            self.show_sensor_value(sdr_entry)

    def show_sensor_value(self, s):
        if s.type is pyipmi.sdr.SDR_TYPE_FULL_SENSOR_RECORD:
            (raw, states) = self.ipmi.get_sensor_reading(s.number, s.owner_lun)
            value = s.convert_sensor_raw_to_value(raw)
            if value is None:
                value = "na"
            self.sensor_lines.append(
                f"{s.device_id_string.decode()}: value={value}")
        elif s.type is pyipmi.sdr.SDR_TYPE_COMPACT_SENSOR_RECORD:
            (raw, states) = self.ipmi.get_sensor_reading(s.number)
            # TODO: interpret hotswap sensor and make sure it makes sense
            # Does the HS sensor provided by carrier differ?
            self.sensor_lines.append(
                f"{s.device_id_string.decode()}: raw_value={raw} "
                f"state=0x{states:x}")
        else:
            self.sensor_lines.append(
                f"{s.device_id_string.decode()}: unknown")

    def show_payload_status(self):
        self.payload_lines = []
        if self.pin_pg is not None:
            pg_val = self.interface.arduino.digital_read(self.pin_pg)
            self.payload_lines.append(f'PG value: {pg_val}')

    def setup_pins(self):
        if self.pin_pg is not None:
            self.interface.arduino.pin_mode(self.pin_pg, OUTPUT)
        if self.pin_hs is not None:
            self.interface.arduino.pin_mode(self.pin_hs, OUTPUT)

    def _run(self):
        self.setup_pins()
        self.show_general_info()
        while True:
            self.show_sensors()
            self.show_payload_status()
            event = self.interface.receive_and_ack_event()
            unprocessed = self.interface.pop_unprocessed_messages()
            if unprocessed:
                self.log(f"Unknown messages: {unprocessed}")

            if event and event.sensor_type == SENSOR_TYPE_MODULE_HOT_SWAP and \
                    event.event_type.dir == 0:
                if event.event_data[0] == 0:
                    self.process_handle_closed()
                elif event.event_data[0] == 1:
                    self.process_handle_open()

            self.tui.process_events()
            if self.want_quit:
                break

            self.draw()

        self.tui.quit()

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            self.tui.quit()
        except Exception as e:
            self.tui.quit()
            raise


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', help='Serial port device node', required=True)
    parser.add_argument(
        '--target', type=int, default=DEFAULT_TARGET,
        help="IPMB address of target device")
    parser.add_argument(
        '--pin-pg', type=int,
        help="Arduino pin used for indicating that power payload is good")
    parser.add_argument(
        '--pin-hs', type=int,
        help="Arduino pin used for indicating that hotswap switch is on")
    return parser.parse_args()


def main():
    args = parse_args()
    main = Main(args.port, args.target, args.pin_pg, args.pin_hs)
    main.run()


if __name__ == '__main__':
    main()
