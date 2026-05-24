import machine
import time


class HCSR04:
    """
    One-shot blocking HC-SR04 ultrasonic distance sensor driver.

    read() sends a trigger pulse, polls for the echo pin to go high (recording
    the start time in-line), then waits for a falling-edge IRQ and returns the
    distance in mm.
    Returns -1 if no echo is received within timeout_ms.

    The echo pin on the HC-SR04 outputs 5 V.  On a Pico, connect it through
    a voltage divider (e.g. 1 kΩ + 2 kΩ) to bring it down to ~3.3 V.
    """

    def __init__(self, trigger_pin, echo_pin, timeout_ms=60):
        self._trigger = machine.Pin(trigger_pin, machine.Pin.OUT)
        self._trigger.value(0)
        self._echo = machine.Pin(echo_pin, machine.Pin.IN)
        self._timeout_ms = timeout_ms

        self._echo_end = 0
        self._echo_done = False

        self._echo.irq(
            trigger=machine.Pin.IRQ_FALLING,
            handler=self._irq,
        )

    def _irq(self, pin):
        self._echo_end = time.ticks_us()
        self._echo_done = True

    def _single(self):
        """One raw reading; returns mm or -1 on timeout."""
        self._echo_end = 0
        self._echo_done = False

        # 10 µs trigger pulse
        self._trigger.value(1)
        time.sleep_us(10)
        self._trigger.value(0)

        deadline = time.ticks_add(time.ticks_ms(), self._timeout_ms)

        # Poll for rising edge and record start time in-line
        while not self._echo.value():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return -1
        echo_start = time.ticks_us()

        # Wait for falling-edge IRQ
        while not self._echo_done:
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return -1

        duration_us = max(0, time.ticks_diff(self._echo_end, echo_start))
        # speed of sound: 343 m/s → distance = duration_us * 343 / 2000
        return (duration_us * 343) // 2000

    def read(self, samples=3):
        """
        Return the median of `samples` readings.
        Errors (-1) are ignored; returns -1 only if all samples fail.
        """
        results = []
        for _ in range(samples):
            mm = self._single()
            if mm >= 0:
                results.append(mm)
            time.sleep_ms(10)   # HC-SR04 needs ~10 ms between triggers
        if not results:
            return -1
        results.sort()
        return results[len(results) // 2]
