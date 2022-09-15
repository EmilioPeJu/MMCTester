# MMCTester

MMCTester provides a way to test a MMC using an Arduino UNO compatible board.

## Quickstart

- Program the sketch in `mmctester-board` to an Arduino UNO compatible board

- Connect IPMB to pins D14 (SDA) and D15 (SCL)

- Connect GND if the power circuit is not shared

- Use digital pin D13 to indicate when the payload power is activated

- Use digital pin D12 to control the hotswap switch

- Install `mmctester` package making sure you have the latest `python-ipmi`

- Run: `mmctester --port /dev/ttyACM0` (replace serial port path accordingly)
