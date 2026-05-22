import machine
import math
import time

# 8-step half-step sequence for 28BYJ-48 (IN1..IN4)
_HALFSTEP = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)


class StepperPair:
    """
    Drives two 28BYJ-48 steppers via ULN2003 using an 8-step half-step sequence.

    All stepping happens inside a hardware timer ISR — coils are de-energised in
    the ISR the moment remain reaches zero, so no update() call is ever needed
    from user code.  move(), turn(), and arc() queue steps and return immediately;
    the caller decides whether to block by calling wait().
    """

    def __init__(
        self,
        left_pins,
        right_pins,
        wheel_diameter_mm=69.0,
        wheel_spacing_mm=110.0,
        steps_per_rev=4096,
        min_step_delay_us=1200,
    ):
        self._spacing = float(wheel_spacing_mm)
        self._steps_per_rev = steps_per_rev
        self._min_delay = min_step_delay_us

        self._motors = [
            self._make_motor(left_pins, wheel_diameter_mm),
            self._make_motor(right_pins, wheel_diameter_mm),
        ]
        self._moving = False

        # Timer fires every 200 µs; the ISR advances each motor when its
        # individual per-step delay has elapsed.
        self._timer = machine.Timer()
        self._timer.init(
            mode=machine.Timer.PERIODIC,
            freq=5000,  # 200 µs period
            callback=self._irq,
        )

    def _make_motor(self, pins, diameter_mm):
        objs = [machine.Pin(p, machine.Pin.OUT) for p in pins]
        for p in objs:
            p.value(0)
        return {
            "pins": objs,
            "diam": float(diameter_mm),
            "seq": 0,
            "dir": 1,
            "remain": 0,
            "delay": self._min_delay,
            "next": time.ticks_us(),
        }

    # --- Timer ISR ---

    def _irq(self, _t):
        now = time.ticks_us()
        any_moving = False
        for m in self._motors:
            remain = m["remain"]
            if remain == 0:
                continue
            if time.ticks_diff(now, m["next"]) >= 0:
                m["seq"] = (m["seq"] + m["dir"]) % 8
                a, b, c, d = _HALFSTEP[m["seq"]]
                p = m["pins"]
                p[0].value(a); p[1].value(b); p[2].value(c); p[3].value(d)
                remain -= 1
                m["remain"] = remain
                if remain == 0:
                    # de-energise immediately — no update() call needed
                    p[0].value(0); p[1].value(0); p[2].value(0); p[3].value(0)
                else:
                    m["next"] = time.ticks_add(now, m["delay"])
                    any_moving = True
            else:
                any_moving = True  # step not due yet but motor still has work
        self._moving = any_moving

    # --- Internal helpers ---

    def _mm_to_steps(self, motor, mm):
        circumference = math.pi * motor["diam"]
        return int(round((mm / circumference) * self._steps_per_rev))

    def _calc_delay(self, left_mm, right_mm, seconds):
        if seconds is None:
            return self._min_delay
        steps = max(
            abs(self._mm_to_steps(self._motors[0], left_mm)),
            abs(self._mm_to_steps(self._motors[1], right_mm)),
        )
        if steps <= 1 or seconds <= 0:
            return self._min_delay
        requested = int((seconds * 1_000_000) / steps)
        return max(requested, self._min_delay)

    def _queue(self, left_mm, right_mm, delay_us):
        # Disable IRQs for the whole queuing operation so the ISR cannot
        # see a partially-updated state or overwrite _moving before we set it.
        irq = machine.disable_irq()
        try:
            for idx, mm in enumerate((left_mm, right_mm)):
                m = self._motors[idx]
                steps = self._mm_to_steps(m, mm)
                m["dir"] = 1 if steps >= 0 else -1
                m["remain"] = abs(steps)
                m["delay"] = delay_us
                m["next"] = time.ticks_us()
            self._moving = True
        finally:
            machine.enable_irq(irq)

    # --- Public API ---

    @property
    def is_moving(self):
        return self._moving

    def move(self, distance_mm, seconds=None):
        delay = self._calc_delay(distance_mm, distance_mm, seconds)
        self._queue(distance_mm, distance_mm, delay)

    def turn(self, angle_deg, seconds=None):
        arc_len = (math.pi * self._spacing * angle_deg) / 360.0
        delay = self._calc_delay(arc_len, -arc_len, seconds)
        self._queue(+arc_len, -arc_len, delay)

    def arc(self, radius_mm, angle_deg, seconds=None):
        rL = radius_mm - self._spacing / 2.0
        rR = radius_mm + self._spacing / 2.0
        dL = 2 * math.pi * rL * (angle_deg / 360.0)
        dR = 2 * math.pi * rR * (angle_deg / 360.0)
        delay = self._calc_delay(dL, dR, seconds)
        self._queue(dL, dR, delay)

    def stop(self):
        irq = machine.disable_irq()
        try:
            for m in self._motors:
                m["remain"] = 0
                for p in m["pins"]:
                    p.value(0)
            self._moving = False
        finally:
            machine.enable_irq(irq)

    def deinit(self):
        self._timer.deinit()
        self.stop()
