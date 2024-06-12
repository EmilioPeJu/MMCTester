#!/usr/bin/env python
import argparse

import pyipmi
import pyipmi.interfaces
import pyipmi.msgs.picmg
from pyipmi.utils import check_completion_code

from mmctester.interface import MMCTesterBoard
from mmctester.led import set_led_long
from mmctester.util import hex_or_int

DEFAULT_TARGET = 0xa2


class CommandsTester(object):
    def __init__(self, port_or_ip: str, target: str):
        if port_or_ip.startswith('/dev/'):
            self.interface = MMCTesterBoard(port=port_or_ip)
            self.ipmi = pyipmi.create_connection(self.interface)
            self.ipmi.target = pyipmi.Target(target)
        else:
            self.interface = pyipmi.interfaces.create_interface(
                interface='rmcp', slave_address=0x81, host_target_address=0x20)
            self.ipmi = pyipmi.create_connection(self.interface)
            self.ipmi.session.set_session_type_rmcp(host=port_or_ip, port=623)
            self.ipmi.session.set_auth_type_user(username='', password='')
            self.ipmi.target = pyipmi.Target(
                ipmb_address=target,
                routing=[(0x81, 0x20, 0),
                         (0x20, 0x82, 7),
                         (0x82, target, None)])
            self.ipmi.session.establish()

    def try_get_device_id(self):
        print('Get Device ID: ', end='')
        try:
            device_id = self.ipmi.get_device_id()
            print('OK')
            print(device_id)
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_device_guid(self):
        print('Get Device GUID: ', end='')
        try:
            guid = self.ipmi.get_device_guid()
            print('OK')
            print(guid)
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_fru_data(self):
        print('Get FRU Data: ', end='')
        try:
            self.ipmi.get_fru_inventory_header(0)
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_sdr_repository_info(self):
        print('Get SDR Repository Info: ', end='')
        try:
            self.ipmi.get_sdr_repository_info()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_sdr_repository_allocation_info(self):
        print('Get SDR Repository Allocation Info: ', end='')
        try:
            self.ipmi.get_sdr_repository_allocation_info()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_reserve_sdr_repository(self):
        print('Reserve SDR Repository: ', end='')
        try:
            self.ipmi.reserve_sdr_repository()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_sdr(self):
        print('Get SDR: ', end='')
        try:
            next(self.ipmi.sdr_repository_entries())
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_reserve_device_sdr_repository(self):
        print('Reserve SDR Repository: ', end='')
        try:
            self.ipmi.reserve_device_sdr_repository()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_device_sdr(self):
        print('Get Device SDR: ', end='')
        try:
            next(self.ipmi.device_sdr_entries())
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_sensor_reading(self):
        print('Get Sensor Reading: ', end='')
        try:
            sdr = None
            for item in self.ipmi.device_sdr_entries():
                if hasattr(item, 'number'):
                    sdr = item
                    break

            if sdr and hasattr(sdr, 'number'):
                self.ipmi.get_sensor_reading(sdr.number, sdr.owner_lun)
                print('OK')
            else:
                print('No readable sensor found')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_fru_control_warm_reset(self):
        print('FRU Control Warm Reset: ', end='')
        try:
            self.ipmi.fru_control_warm_reset()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_fru_control_cold_reset(self):
        print('FRU Control Cold Reset: ', end='')
        try:
            self.ipmi.fru_control_cold_reset()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_fru_control_graceful_reboot(self):
        print('FRU Control Graceful Reboot: ', end='')
        try:
            self.ipmi.fru_control_graceful_reboot()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_set_event_receiver(self):
        print('Set Event Receiver: ', end='')
        try:
            self.ipmi.set_event_receiver(0x20, 0)
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_event_receiver(self):
        print('Get Event Receiver: ', end='')
        try:
            self.ipmi.get_event_receiver()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_get_picmg_properties(self):
        print('Get PICMG Properties: ', end='')
        try:
            self.ipmi.get_picmg_properties()
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def try_set_led_state(self):
        print('Set LED State: ', end='')
        try:
            set_led_long(self.ipmi)
            print('OK')
        except Exception as e:
            print(f'FAIL ({e})')

    def run(self):
        self.try_get_device_id()
        self.try_get_device_guid()
        self.try_get_fru_data()
        # self.try_reserve_sdr_repository()
        # self.try_get_sdr_repository_info()
        # self.try_get_sdr_repository_allocation_info()
        # self.try_get_sdr()
        self.try_reserve_device_sdr_repository()
        self.try_get_device_sdr()
        self.try_get_sensor_reading()
        self.try_set_event_receiver()
        # self.try_get_event_receiver()
        self.try_get_picmg_properties()
        self.try_set_led_state()
        # self.try_fru_control_cold_reset()
        # self.try_fru_control_warm_reset()
        # self.try_fru_control_graceful_reboot()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', help='Serial port device node e.g. /dev/ttyACM0',
        required=True)
    parser.add_argument(
        '--target', type=hex_or_int, default=DEFAULT_TARGET,
        help="IPMB address of target device")
    return parser.parse_args()


def main():
    args = parse_args()
    main = CommandsTester(args.port, args.target)
    main.run()


if __name__ == '__main__':
    main()
