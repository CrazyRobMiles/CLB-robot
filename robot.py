"""
CLB Robot Library
=================
A MicroPython library for the Hull Pixelbot.

Provides sequential robot control that matches the behaviour described in the
PythonIsh specification: move, turn, arc, pixel colours, distance sensing, and
timing — with motor movement running in the background via a timer ISR.

Usage
-----
    import robot

    robot.init(
        left_pins  = [15, 14, 13, 12],   # ULN2003 IN1-IN4 for left motor
        right_pins = [8,  9,  10, 11],   # ULN2003 IN1-IN4 for right motor
        pixel_pin  = 18,
        pixel_count= 8,
        trigger_pin= 5,                  # HC-SR04 TRIG (optional)
        echo_pin   = 19,                 # HC-SR04 ECHO via voltage divider
    )

    robot.colour(robot.GREEN)
    robot.move(200)                      # move 200 mm, blocks until done
    robot.turn(90)                       # turn 90 degrees clockwise, blocks
    robot.colour(robot.RED)

Pin defaults match the standard Hull Pixelbot wiring.  Override any of them in
the init() call.
"""

import sys
import select as _select
import time
import random as _random
from lib.stepper import StepperPair
from lib.distance import HCSR04
from lib.pixels import PixelStrip

# Non-blocking stdin poll — only returns data when a console is connected
# (USB CDC in Thonny / mpremote). When running standalone on battery there
# is no input, so check() becomes a harmless no-op.
_poll = _select.poll()
_poll.register(sys.stdin, _select.POLLIN)

_stepper = None
_sensor  = None
_pixels  = None


# ---------------------------------------------------------------------------
# Colour constants
# Use these with colour() and _pixels.set().
# Custom colours can be written as plain tuples: (255, 128, 0) for orange.
# ---------------------------------------------------------------------------

RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
CYAN    = (  0, 255, 255)
MAGENTA = (255,   0, 255)
YELLOW  = (255, 255,   0)
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init(
    left_pins   = None,
    right_pins  = None,
    pixel_pin   = None,
    pixel_count = None,
    trigger_pin = None,
    echo_pin    = None,
    wheel_diameter_mm = None,
    wheel_spacing_mm  = None,
    steps_per_rev     = 4096,
    min_step_delay_us = 1200,
):
    """
    Set up the robot hardware.  Call once at the top of your program.

    With no arguments, hardware settings are read from config.py.
    Any argument you supply overrides the corresponding config.py value.
    """
    global _stepper, _sensor, _pixels

    import config as _cfg

    left_pins         = left_pins         or _cfg.LEFT_PINS
    right_pins        = right_pins        or _cfg.RIGHT_PINS
    pixel_pin         = pixel_pin         if pixel_pin  is not None else _cfg.PIXEL_PIN
    pixel_count       = pixel_count       if pixel_count is not None else _cfg.PIXEL_COUNT
    trigger_pin       = trigger_pin       if trigger_pin is not None else _cfg.TRIGGER_PIN
    echo_pin          = echo_pin          if echo_pin    is not None else _cfg.ECHO_PIN
    wheel_diameter_mm = wheel_diameter_mm if wheel_diameter_mm is not None else _cfg.WHEEL_DIAMETER_MM
    wheel_spacing_mm  = wheel_spacing_mm  if wheel_spacing_mm  is not None else _cfg.WHEEL_SPACING_MM

    _stepper = StepperPair(
        left_pins, right_pins,
        wheel_diameter_mm = wheel_diameter_mm,
        wheel_spacing_mm  = wheel_spacing_mm,
        steps_per_rev     = steps_per_rev,
        min_step_delay_us = min_step_delay_us,
    )

    _pixels = PixelStrip(pixel_pin, pixel_count)

    if trigger_pin is not None and echo_pin is not None:
        _sensor = HCSR04(trigger_pin, echo_pin)


# ---------------------------------------------------------------------------
# Pixel colour
# ---------------------------------------------------------------------------

def colour(rgb):
    """
    Set all pixels to rgb.

    Pass one of the colour constants or any (r, g, b) tuple:
        colour(RED)
        colour(GREEN)
        colour((255, 128, 0))   # orange
    """
    _pixels.fill(rgb)


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------

def check():
    """Stop the robot and raise KeyboardInterrupt if any console input is waiting."""
    if _poll.poll(0):
        sys.stdin.read(1)
        _stepper.stop()
        raise KeyboardInterrupt


def wait():
    """Block until the current move, turn, or arc has finished."""
    while _stepper.is_moving:
        time.sleep_ms(10)
        check()


def moving():
    """Return True if the motors are currently moving."""
    return _stepper.is_moving


def move(mm, seconds=None, nowait=False):
    check()
    """
    Move the robot forward (positive mm) or backward (negative mm).

    seconds  — how long the move should take.  Omit for full speed.
    nowait   — if True, return immediately without waiting for the move
               to complete.  Use wait() later to synchronise.

    Examples:
        move(200)                  # forward 200 mm at full speed, blocks
        move(-100)                 # backward 100 mm, blocks
        move(500, seconds=10)      # forward 500 mm over 10 seconds, blocks
        move(200, nowait=True)     # start moving, return immediately
    """
    _stepper.move(mm, seconds=seconds)
    if not nowait:
        wait()


def turn(degrees, seconds=None, nowait=False):
    check()
    """
    Turn the robot on the spot.  Positive degrees = clockwise.

    Examples:
        turn(90)         # quarter turn clockwise, blocks
        turn(-180)       # half turn anti-clockwise, blocks
    """
    _stepper.turn(degrees, seconds=seconds)
    if not nowait:
        wait()


def arc(radius_mm, angle_deg, seconds=None, nowait=False):
    check()
    """
    Move the robot along a circular arc.

    radius_mm — radius of the arc.  Positive = centre to the right.
                0 = rotate on the spot (equivalent to turn()).
    angle_deg — angular distance to travel.  Positive = clockwise.

    Examples:
        arc(200, 90)     # quarter-circle arc, 200 mm radius, clockwise
        arc(0, 180)      # rotate 180° on the spot
    """
    _stepper.arc(radius_mm, angle_deg, seconds=seconds)
    if not nowait:
        wait()


def stop():
    """Stop the motors immediately and de-energise all coils."""
    _stepper.stop()


# ---------------------------------------------------------------------------
# Distance sensor
# ---------------------------------------------------------------------------

def distance():
    """
    Trigger one ultrasonic reading and return the distance in mm.
    Returns -1 if no echo is received (nothing in range, or sensor absent).
    """
    if _sensor is None:
        return -1
    return _sensor.read()


# ---------------------------------------------------------------------------
# Random numbers  (matches @random in PythonIsh — returns 1..12)
# ---------------------------------------------------------------------------

def random_val():
    """Return a random integer between 1 and 12 inclusive."""
    return _random.randint(1, 12)
