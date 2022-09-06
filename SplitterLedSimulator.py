import time

import asyncio_dgram
from bitstring import BitStream

from Splitter import Splitter
from SplitterVentilator import SplitterStream


class SplitterLedSimulator:

    def __init__(self, sps: SplitterStream) -> None:
        super().__init__()
        self.server = None
        self.sps = sps

    async def start(self):
        self.server = await asyncio_dgram.bind((self.sps.ip, 16661))
        print(f"Serving on {self.sps.ip}")

    async def receive_loop(self):
        while True:
            data, remote_addr = await self.server.recv()
            s = BitStream(data)
            print((time.time() * 100), ":", self.sps.ip, ":", s.readlist(Splitter.encode_header_format))
            # print(s.readlist(LEDNode.encode_header_format))
            # for i in range(0, LEDNode.num_of_LED):
            #   print(f'{s.pos} {s.readlist(RGBW.encode_format)}')
            # print(s.readlist(LEDNode.encode_header_format))
