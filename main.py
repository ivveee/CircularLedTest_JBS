import asyncio

import asyncio_dgram

from LEDNode import LEDNode
from Splitter import Splitter
from SplitterLedSimulator import SplitterLedSimulator
from SplitterVentilator import SplitterVentilator

num_of_splitters = 4


def set_up_ventilator():
    ventilator = SplitterVentilator()
    for splitter_id in range(0, num_of_splitters):
        splitter = Splitter(first_port=0)
        ventilator.add_splitter(splitter, splitter_id)

        node0 = LEDNode(panel_id=0, mode=2)
        node0.set_all_pixels_primary(255, 0, 0, int(255 / (splitter_id + 1)))
        splitter.add_node(node0)

        node1 = LEDNode(panel_id=1, mode=2)
        node1.set_all_pixels_primary(0, 0, 255, int(255 / (splitter_id + 1)))
        splitter.add_node(node1)

        node2 = LEDNode(panel_id=2, mode=2)
        node2.set_all_pixels_primary(0, 255, 0, int(255 / (splitter_id + 1)))
        splitter.add_node(node2)

        node3 = LEDNode(panel_id=3, mode=2)
        node3.set_all_pixels_primary(0, 255, 255, int(255 / (splitter_id + 1)))
        splitter.add_node(node3)

    return ventilator

    # node.set_all_pixels_primary(120, 0, 0, 120)

    # await stream.send(splitter.encode02(0, 2).bytes)
    # data, remote_addr = await stream.recv()
    # print(f"Client received: {data.decode()!r}")

    # stream.close()


async def entry_point():
    ventilator = set_up_ventilator()
    await ventilator.start()

    simulators = []
    loops = []

    for i in range(0, num_of_splitters):
        simulator = SplitterLedSimulator(ventilator.sps[i])
        simulators.append(simulator)
        await simulator.start()
        loops.append(simulator.receive_loop())

    bserver = await asyncio_dgram.bind(("127.0.0.255", 16661))
    await asyncio.gather(ventilator.run_in_loop(), *loops)


if __name__ == "__main__":
    asyncio.run(entry_point())
