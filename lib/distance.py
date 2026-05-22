import machine
import time


class HCSR04:
    """
    One-shot blocking HC-SR04 ultrasonic distance sensor driver.

    read() sends a trigger pulse, waits for the echo pin to go high then low
    (captured by a pin IRQ), and returns the distance in mm.
    Returns -1 if no echo is received within timeout_ms.

    The echo pin on the HC-SR04 outputs 5 V.  On a Pico, connect it through
    a voltage divider (e.g. 1 kΩ + 2 kΩ) to bring it down to ~3.3 V.
    """

    def __init__(self, trigger_pin, echo_pin, timeout_ms=60):
        self._trigger = machine.Pin(trigger_pin, machine.Pin.OUT)
        self._trigger.value(0)
        self._echo = machine.Pin(echo_pin, machine.Pin.IN)
        self._timeout_ms = timeout_ms

        self._echo_start = 0
        self._echo_end = 0
        self._echo_done = False

        self._echo.irq(
            trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
            handler=self._irq,
        )

    def _irq(self, pin):
        if pin.value():             # rising edge: pulse left the sensor
            self._echo_start = time.ticks_us()
        else:                       # falling edge: echo returned
            self._echo_end = time.ticks_us()
            self._echo_done = True

    def read(self):
        self._echo_done = False

        # 10 µs trigger pulse
        self._trigger.value(1)
        time.sleep_us(10)
        self._trigger.value(0)

        deadline = time.ticks_add(time.ticks_ms(), self._timeout_ms)
        while not self._echo_done:
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return -1

        duration_us = max(0, time.ticks_diff(self._echo_end, self._echo_start))
        # speed of sound: 343 m/s → distance = duration_us * 343 / 2000
        return (duration_us * 343) // 2000
