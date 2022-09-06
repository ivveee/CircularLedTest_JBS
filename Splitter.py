# 02 <format> <flags> <port> <nbyteslo> <nbyteshi> <nports> <portsinpkt> <data1>
# [<data2>..<dataN>]
# ● <format>:
# ○ 00: DMX style with initial break
# ○ 01: Raw UART
# ● <flags>:
# ○ Bit 0 is set to start frame transmission (value is 128 to start transmission;
# alternatively use the sync packet below and leave this set to 0)
# ○ Bit 1-7 reserved
# ● <port>: First splitter port number for this packet (1-16) or 0 for same data to all ports
# ● <nbytes>: bytes per port (must be the same for all ports). Max 1400 decimal
# ● <nports>: number of ports in use
# ● <portsinpkt>: number of ports for which this packet contains data
# ● Reserved bytes and bits must be set to 0
from typing import List

import bitstring
from bitstring import BitStream

from LEDNode import LEDNode


class Splitter:
    encode_header_format = 'uint:8 = package_type, \
                            uint:8 = format, \
                            uint:1 = flags, \
                            uint:7 = zeros, \
                            uint:8 = port, \
                            uint:16 = nbyteslo, \
                            uint:16 = nbyteshi, \
                            uint:8 = nports, \
                            uint:8 = portsinpkt, \
                           '

    def __init__(self, first_port) -> None:
        super().__init__()
        self.send_format = 0
        self.flags = 0
        self.first_port = first_port
        self.port_data_map: List[LEDNode] = []

    def add_node(self, node: LEDNode):
        self.port_data_map.append(node)

    def encode02(self, first_port_to_output, num_of_ports_to_output):
        node_data = BitStream()
        node_encoded_size_min = float("inf")
        node_encoded_size_max = 0

        for port_num in range(first_port_to_output - self.first_port,
                              first_port_to_output - self.first_port + num_of_ports_to_output):
            node = self.port_data_map[port_num]
            node_encoded = node.encode()
            size = len(node_encoded)
            if node_encoded_size_min > size:
                node_encoded_size_min = size
            if node_encoded_size_max < size:
                node_encoded_size_max = size
            node_data.append(node.encode())

        packet_struct = {'package_type': 2,
                         'format': self.send_format,
                         'flags': self.flags,
                         'zeros': 0,
                         'port': first_port_to_output,
                         'nbyteslo': node_encoded_size_min,
                         'nbyteshi': node_encoded_size_max,
                         'nports': len(self.port_data_map),
                         'portsinpkt': num_of_ports_to_output,
                         }
        packet = bitstring.pack(Splitter.encode_header_format, **packet_struct)
        packet.append(node_data)

        return packet

    @staticmethod
    def encode04():
        return bitstring.pack("uint:8", 4)
