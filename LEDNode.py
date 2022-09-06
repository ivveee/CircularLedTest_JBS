# <break> 0x00 <gb1> <gb2> <sm> <id> <rgbwdata>
# <gb1>, <gb2> is global brightness for side 1 (primary) & 2 (secondary) respectively (bit 0
# ignored)
# <sm> is smoothing value:
# 0 : no smoothing, LEDs updated on receipt of new packet
# >0 : LEDs updated 100 times/sec, with filtering of incoming packets to reduce
# steppiness at low framerates. Useful values will be in the range 80-160 decimal,
# optimal value will be content dependent.
# <rgbwdata> is 864 or 432 ( dec) bytes of RGBW pixel data.
# <id> bits 0..3 : Device ID 1..15. ID=0 broadcasts to all panels.
# <id> bits 4,5 unused, must be set to 0
# <id> bits 7,6 :
# Bit 7 Bit 6 Function Packet length
# 0 0 Full pixel addressability on both rings 864+5=869
# 0 1 reserved
# 1 0 Secondary ring shows copy of primary 432+5=437
# 1 1 Secondary ring shows mirrored copy of primary 432+5=437

import bitstring


class RGBW:
    encode_format = '4*uint:8'

    def __init__(self, r=255, g=255, b=255, w=255) -> None:
        self.red: int = r
        self.green: int = g
        self.blue: int = b
        self.white: int = w

    def set_color(self, r, g, b, w):
        self.red = r
        self.green = g
        self.blue = b
        self.white = w

    def encode(self):
        return bitstring.pack(RGBW.encode_format, self.red, self.green, self.blue, self.white)


class LEDNode:
    num_of_LED = 108
    encode_header_format = 'uint:8 = break, \
                            uint:8 = zeroes, \
                            uint:8 = gb1, \
                            uint:8 = gb2, \
                            uint:8 = sm, \
                            uint:4 = id_num, \
                            uint:2 = id_zero, \
                            uint:2 = id_mode, \
                           '

    def empty_cache(self):
        if hasattr(self, 'cache'):
            del self.cache

    def __init__(self, panel_id, mode) -> None:
        super().__init__()
        self._brightness_primary = 255
        self._brightness_secondary = 255
        self._smoothing = 100
        # 432 bytes: 432/36 columns/3 rows = 4 bytes. 108 leds
        self._leds_primary = [RGBW() for x in range(LEDNode.num_of_LED)]
        self._leds_secondary = [RGBW() for x in range(LEDNode.num_of_LED)]
        self._panel_id = panel_id  # (1..15)
        self._mode = mode

    def set_pixel(self, pos, r, g, b, w):
        self._leds_primary[pos].set_color(r, g, b, w)
        self.empty_cache()

    def set_all_pixels_primary(self, r, g, b, w):
        for led in self._leds_primary:
            led.set_color(r, g, b, w)
        self.empty_cache()

    def set_all_pixels_secondary(self, r, g, b, w):
        for led in self._leds_secondary:
            led.set_color(r, g, b, w)
        self.empty_cache()

    def encode(self):
        if hasattr(self, 'cache'):
            return self.cache
        else:
            packet_struct = {'break': 0,
                             'zeroes': 0,
                             'gb1': self._brightness_primary,
                             'gb2': self._brightness_secondary,
                             'sm': self._smoothing,
                             'id_num': self._panel_id,
                             'id_zero': 0,
                             'id_mode': self._mode
                             }
            packet = bitstring.pack(LEDNode.encode_header_format, **packet_struct)
            for led in self._leds_primary:
                packet.append(led.encode())
            if self._mode == 0:
                for led in self._leds_secondary:
                    packet.append(led.encode())
            self.cache = packet
            return packet
