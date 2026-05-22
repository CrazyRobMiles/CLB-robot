import machine
import neopixel


class PixelStrip:
    """
    Thin wrapper around MicroPython's neopixel module.

    fill(rgb) sets every pixel to one colour and pushes the update immediately.
    set(index, rgb) changes a single pixel by index.

    Both accept an (r, g, b) tuple — use the colour constants from robot.py
    or write a literal tuple for custom colours: (255, 128, 0) for orange.
    """

    def __init__(self, pin_num, count):
        pin = machine.Pin(pin_num, machine.Pin.OUT)
        self._np = neopixel.NeoPixel(pin, count, bpp=3)
        self._count = count
        self.fill((0, 0, 0))

    def fill(self, rgb):
        for i in range(self._count):
            self._np[i] = rgb
        self._np.write()

    def set(self, index, rgb):
        self._np[index] = rgb
        self._np.write()
