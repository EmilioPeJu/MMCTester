# MMCTester

MMCTester provides a way to test a MMC using an Arduino UNO compatible board.

## Quickstart

- Program the sketch in `mmctester-board` to an Arduino UNO compatible board

- Connect IPMB to pins D14 (SDA) and D15 (SCL)

- Connect GND if the power circuit is not shared

- [Optional] Use digital pin D13 (for example) to indicate when the payload
power is activated

- [Optional] Use digital pin D3 (for example) to control the hotswap switch

- Install `mmctester` package making sure you have the latest `python-ipmi`

- Run: `mmctester --port /dev/ttyACM0 --pin-pg 13 --pin-hs 3`
 (replace serial port path and pins accordingly)

This will show a tui interface with FRU and SDR info, when a HotSwap event is
detected, the power-good pin (pin-pg) will be set acordingly to emulate that
power has been given. Additionally, the number keys can be used to manually
control some of the digital outputs, pin-hs can be used to programatically
control the HotSwap switch if the board has been wired accordingly.

Demo:
```bash
$ mmctester --port /dev/ttyACM0

HELP
Keys:  q => quit
===
DEVICE
Device ID: 0
Device Rev: 0
Firmware Rev: 1.1
===
FRU
Product manufacturer STM32
Product name NUCLEOF303RE
Product part NUCLEOF303RE:1.0
Product version 1.0
Product SN CNxxxxx
===
SENSORS
training_board: unknown
HOTSWAP AMC: raw_value=0 state=0x2
PG AMC: raw_value=1 state=0xc4
P3V3: value=0.192
TEMP UC: value=22.5
===
PAYLOAD
===
LOGS
```

## MMC Commands Tester

A small utility to test if the most important IPMI commands have been
implemented in the target MMC.

Demo:
```bash
$ mmccommandstester --port /dev/ttyACM0
Get Device ID: OK
Device ID: 0 revision: 0 available: 0 fw version: 1.1 ipmi: 2.0 manufacturer: 12634 product: 0 functions: sensor,fru_inventory,ipmb_event_generator
Get Device GUID: OK
Device GUID: 00000000-0000-0000-0000-000000000000
Get FRU Data: OK
Reserve SDR Repository: OK
Get Device SDR: OK
Get Sensor Reading: OK
Set Event Receiver: OK
Get PICMG Properties: OK
Set LED State: OK


# Passing an IP in the port argument to use the MCH to bridge commands to the
# target
$ mmccommandstester --port 192.168.40.250 --target 0x72
Get Device ID: OK
Device ID: 0 revision: 1 available: 0 fw version: 1.10 ipmi: 1.5 manufacturer: 11111 product: 1111 functions: sensor,fru_inventory,ipmb_event_generator
Get Device GUID: OK
Device GUID: 00112233-4455-6677-8899-aabbccddeeff
Get FRU Data: OK
Reserve SDR Repository: OK
Get Device SDR: OK
Get Sensor Reading: OK
Set Event Receiver: OK
Get PICMG Properties: OK
Set LED State: OK
```
