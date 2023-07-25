import logging
import time
from threading import Thread

import struct

import cflib
from cflib.crazyflie import Crazyflie

from google.protobuf.message import DecodeError

import proto
from proto.message_pb2 import Message

logging.basicConfig(level=logging.ERROR)


class RadioPacketParser(object):
    def __init__(self):
        self.initialize()

    def update(self, byte):
        def when_waiting_header():
            if byte == 255:
                self.state = "WAITING_LENGTH"
            return None

        def when_waiting_length():
            self.length = min(byte, 255)
            if self.length > 0:
                self.state = "PARSING_BODY"
                self.buffer = bytearray()
            else:
                self.state = "WAITING_HEADER"
                self.length = 0
            return None

        def when_parsing_body():
            self.length -= 1
            self.buffer.append(byte)

            if self.length <= 0:
                result = bytes(self.buffer)
                self.state = "WAITING_HEADER"
                self.length = 0
                return result
            else:
                return None

        if self.state == "WAITING_HEADER":
            return when_waiting_header()
        elif self.state == "WAITING_LENGTH":
            return when_waiting_length()
        elif self.state == "PARSING_BODY":
            return when_parsing_body()

    def initialize(self):
        self.state = "WAITING_HEADER"
        self.length = 0
        self.buffer = bytearray()


class AppchannelTest:
    def __init__(self, link_uri):
        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.appchannel.packet_received.add_callback(self._app_packet_received)

        self._cf.open_link(link_uri)

        self._parser = RadioPacketParser()

        print("Connecting to %s" % link_uri)

    def _connected(self, link_uri):
        Thread(target=self._test_appchannel).start()

    def _connection_failed(self, link_uri, msg):
        print("Connection to %s failed: %s" % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        print("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        print("Disconnected from %s" % link_uri)

    def _app_packet_received(self, data):
        for byte in data:
            packet = self._parser.update(byte)
            if packet is None:
                continue
            message = Message()
            try:
                message.ParseFromString(packet)
            except DecodeError:
                print("Decode Error!")
                continue
            self._message_received(message)

    def _message_received(self, message):
        print(message)

    def _test_appchannel(self):
        ## TODO - send messages

        self._cf.close_link()


if __name__ == "__main__":
    cflib.crtp.init_drivers(enable_debug_driver=False)

    print("Scanning interfaces for Crazyflies...")

    available = cflib.crtp.scan_interfaces()
    print("Crazyflies found:")
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = AppchannelTest(available[0][0])
    else:
        print("No Crazyflies found, cannot run example")
