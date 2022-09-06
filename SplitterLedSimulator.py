import time

import asyncio_dgram
from bitstring import BitStream

from LEDNode import LEDNode, RGBW
from LEDOutput import App
from Splitter import Splitter
from SplitterVentilator import SplitterStream


class SplitterLedSimulator:

    def __init__(self, sps: SplitterStream, app: App) -> None:
        super().__init__()
        self.server = None
        self.sps = sps
        self.app = app

    async def start(self):
        self.server = await asyncio_dgram.bind((self.sps.ip, 16661))
        print(f"Serving on {self.sps.ip}")

    async def receive_loop(self):
        while True:

            data, remote_addr = await self.server.recv()
            s = BitStream(data)
            splitter_header = s.readlist(Splitter.encode_header_format)
            print((time.time() * 100), ":", self.sps.ip, ":", splitter_header)
            ledheader = s.readlist(LEDNode.encode_header_format)
            for i in range(0, LEDNode.num_of_LED):
                color = s.readlist(RGBW.encode_format)
                code = i * 15+(self.sps.id+1)*1000+ splitter_header[4]*10000
                fill = self.app.window.rgbtohex(color[0], color[1], color[2])
                if code in self.app.window.circles:
                    self.app.window.canvas.itemconfig(self.app.window.circles[code], fill=fill)
                else:
                    x = 100+int(i%10) * 15 + splitter_header[4]*200
                    y = (self.sps.id+1)*100 + int(i/10)*5
                    self.app.window.circles[code] = self.app.window.create_circle(x, y, 5, fill=fill)
