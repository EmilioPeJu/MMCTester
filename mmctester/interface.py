#!/usr/bin/env python
import pyipmi
import serial
import time

from array import array
from pyipmi.errors import IpmiTimeoutError
from pyipmi.interfaces.ipmb import (IpmbHeaderReq, IpmbHeaderRsp, checksum,
                                    rx_filter, encode_ipmb_msg)
from pyipmi.logger import log
from pyipmi.msgs import (create_message, constants, encode_message,
                         decode_message)
from pyipmi.msgs.registry import create_request_by_name

from mmctester.arduino import ArduinoLocalCommand
from mmctester.util import hex_to_bin

TERMINATOR = b'\n'
LOCAL_ADDR = 0x0


class MMCTesterBoard(object):
    '''mmctester-board forwards between serial and IPMB.'''

    NAME = 'mmctester-board'

    def __init__(self, port='/dev/ttyACM0', baudrate=115200, address=0x20):
        self.address = address
        self.port = port
        self.next_sequence_number = 0
        self.timeout = 1.0
        self.max_retries = 3
        self._ser = serial.Serial(
            port, baudrate=baudrate, timeout=self.timeout)
        self._recv_queue = []
        self._wait_until_ready()
        self.arduino = ArduinoLocalCommand(
            self._serial_send_raw, self._local_receive_raw, LOCAL_ADDR)
        self.received_acc = bytearray()

    # sends ping command until it is answered
    # as a side effect, it flushes old messages
    def _wait_until_ready(self):
        retries = 0
        while True:
            self._ser.write(b'00\n')
            retries += 1
            if self._ser.read_until(TERMINATOR) == b'00\n':
                break
            elif retries >= self.max_retries:
                raise IOError('Board not ready to accept serial commands')

    def establish_session(self, session):
        # just remember session parameters here
        self._session = session

    def close_session(self):
        self._ser.close()

    def is_ipmc_accessible(self, target):
        header = IpmbHeaderReq()
        header.netfn = 6
        header.rs_lun = 0
        header.rs_sa = target.ipmb_address
        header.rq_seq = self.next_sequence_number
        header.rq_lun = 0
        header.rq_sa = self.address
        header.cmdid = 1
        self._send_raw(header, None)
        self._receive_raw(header)
        return True

    def _inc_sequence_number(self):
        self.next_sequence_number = (self.next_sequence_number + 1) % 64

    @staticmethod
    def _encode_ipmb_msg_req(header, cmd_data):
        data = header.encode()
        data.extend(cmd_data)
        data.append(checksum(data[2:]))

        return data

    def _send_raw(self, header, raw_bytes):
        full_raw_bytes = encode_ipmb_msg(header, raw_bytes)
        self._serial_send_raw(full_raw_bytes)

    def _receive_raw(self, header):
        return self._serial_receive_raw(
            lambda data: data[0] == self.address and rx_filter(header, data))

    def _local_receive_raw(self):
        return self._serial_receive_raw(lambda data: data[0] == LOCAL_ADDR)

    def _serial_send_raw(self, raw_bytes):
        hex_data = b' '.join([b'%02x' % b for b in raw_bytes])
        log().debug('I2C TX [%s]', hex_data.decode())
        self._ser.write(hex_data + b'\n')

    def _serial_receive_raw(self, filter_func=None):
        rsp_received = False

        # first search in receive queue
        for rx_data in self._recv_queue[:]:
            if filter_func is None or filter_func(rx_data):
                self._recv_queue.remove(rx_data)
                return rx_data

        while not rsp_received:

            received = self._ser.read_until(TERMINATOR)

            self.received_acc.extend(received)

            if not received.endswith(TERMINATOR):
                raise IpmiTimeoutError()

            hex_data = self.received_acc.decode()

            self.received_acc = bytearray()
            log().debug('I2C RX [%s]', hex_data[:-1])
            rx_data = array('B', hex_to_bin(hex_data))

            rsp_received = filter_func is None or filter_func(rx_data)

            if not rsp_received:
                self._recv_queue.append(rx_data)

        return rx_data

    def is_platform_event(self, data):
        return IpmbHeaderReq(data).cmdid == constants.CMDID_PLATFORM_EVENT

    def _receive_event_raw(self):
        return self._serial_receive_raw(self.is_platform_event)

    def receive_and_ack_event(self):
        try:
            raw_rx_data = self._receive_event_raw()
        except IpmiTimeoutError:
            return None
        header = IpmbHeaderReq(raw_rx_data)
        req = create_message(header.netfn, header.cmdid, None)
        decode_message(req, raw_rx_data[6:-1])
        rsp_header = IpmbHeaderReq()
        rsp_header.netfn = header.netfn | 1
        rsp_header.rs_lun = header.rq_lun
        rsp_header.rs_sa = header.rq_sa
        rsp_header.rq_seq = header.rq_seq
        rsp_header.rq_lun = header.rs_lun
        rsp_header.rq_sa = header.rs_sa
        rsp_header.cmdid = header.cmdid
        rsp = create_message(rsp_header.netfn, rsp_header.cmdid, None)
        rsp.completion_code = constants.CC_OK
        self._send_raw(rsp_header, encode_message(rsp))

        return req

    def _send_and_receive(self, target, lun, netfn, cmdid, payload):
        '''Send and receive data using ipmb-dev-int interface.

        target:
        lun:
        netfn:
        cmdid:
        payload: IPMI message payload as bytestring

        Returns the received data as bytestring
        '''
        self._inc_sequence_number()

        # assemble IPMB header
        header = IpmbHeaderReq()
        header.netfn = netfn
        header.rs_lun = lun
        header.rs_sa = target.ipmb_address
        header.rq_seq = self.next_sequence_number
        header.rq_lun = 0
        header.rq_sa = self.address
        header.cmdid = cmdid

        retries = 0
        while retries < self.max_retries:
            try:
                self._send_raw(header, payload)
                rx_data = self._receive_raw(header)
                break
            except IpmiTimeoutError:
                pass
            except IOError:
                pass

            retries += 1
            time.sleep(retries * 0.2)

        else:
            log().debug('Recv queue: %s', self._recv_queue)
            raise IpmiTimeoutError()

        # returns only from completion code to (excluding) payload checksum
        # the excluded data has already been used for validation
        return rx_data[6:-1]

    def send_and_receive_raw(self, target, lun, netfn, raw_bytes):
        '''Interface function to send and receive raw message.

        target: IPMI target
        lun: logical unit number
        netfn: network function
        raw_bytes: RAW bytes as bytestring

        Returns the IPMI message response bytestring.
        '''
        return self._send_and_receive(target=target,
                                      lun=lun,
                                      netfn=netfn,
                                      cmdid=array('B', raw_bytes)[0],
                                      payload=raw_bytes[1:])

    def send_and_receive(self, req):
        '''Interface function to send and receive an IPMI message.

        target: IPMI target
        req: IPMI message request

        Returns the IPMI message response.
        '''
        log().debug('IPMI Request [%s]', req)

        rx_data = self._send_and_receive(target=req.target,
                                         lun=req.lun,
                                         netfn=req.netfn,
                                         cmdid=req.cmdid,
                                         payload=encode_message(req))
        rsp = create_message(req.netfn + 1, req.cmdid, req.group_extension)
        decode_message(rsp, rx_data)

        log().debug('IPMI Response [%s])', rsp)

        return rsp

    def pop_unprocessed_messages(self):
        result = self._recv_queue
        self._recv_queue = []
        return result
