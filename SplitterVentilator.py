
import asyncio
from typing import Dict
import asyncio_dgram
from Splitter import Splitter


class SplitterStream:
    SIMULATION_IP = "127.0.0"
    WORKING_IP = "192.168.1"
    active_ip = SIMULATION_IP

    def __init__(self, splitter: Splitter, id_net: int) -> None:
        super().__init__()
        self.splitter = splitter
        self.id = id_net
        self.ip = f"{SplitterStream.active_ip}.{128 + id_net}"

    async def init_stream(self):
        self.stream = await asyncio_dgram.connect((self.ip, 16661))


class SplitterVentilator:

    def __init__(self) -> None:
        super().__init__()
        self.sync_stream = None
        self.sps: Dict[int, SplitterStream] = {}

    def add_splitter(self, splitter: Splitter, id_net: int):
        self.sps[id_net] = SplitterStream(splitter, id_net)

    async def start(self):
        for sps in self.sps.values():
            await sps.init_stream()
        self.sync_stream = await asyncio_dgram.connect((f"{SplitterStream.active_ip}.255", 16661))

    async def ventilate(self, port):
        max_len = 0
        for sps in self.sps.values():
            packet = sps.splitter.encode02(port, 1).bytes
            if max_len < len(packet):
                max_len = len(packet)
            await sps.stream.send(packet)
        await asyncio.sleep(10 / 500000 * max_len + 0.0005)
        # await asyncio.sleep(1)

        # 10/(500000)*(437+36) = 0.0095

    async def run_in_loop(self, loops: float = float('inf')):
        while loops > 0:
            max_ports = float('-inf')
            for sps in self.sps.values():
                if max_ports < len(sps.splitter.port_data_map):
                    max_ports = len(sps.splitter.port_data_map)
            for port in range(0, max_ports):
                await self.ventilate(port)
            await self.sync_stream.send(Splitter.encode04().bytes)

            loops -= 1
