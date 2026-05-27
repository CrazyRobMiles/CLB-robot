"""
Motor wiring validation test
============================
Drives each motor in isolation so you can verify correct wiring and direction.

  RED   -> left motor only, 100 mm forward
  GREEN -> right motor only, 100 mm forward
  WHITE -> both motors together, 100 mm forward

Repeats until a key is pressed (when connected via Thonny / mpremote).
"""

import sys
sys.path.insert(0, '..')

import time
import robot

robot.init()

PAUSE_S = 1.5   # pause between phases so you can see the robot settle


def _drive(left_mm, right_mm):
    """Queue individual-motor steps and block until done."""
    s = robot._stepper
    s._queue(left_mm, right_mm, s._min_delay)
    robot.wait()


while True:
    # --- Phase 1: left motor only ---
    # Expected: only the LEFT wheel turns; robot pivots right
    robot.colour(robot.RED)
    _drive(100, 0)
    robot.colour(robot.BLACK)
    robot.check()
    time.sleep(PAUSE_S)

    # --- Phase 2: right motor only ---
    # Expected: only the RIGHT wheel turns; robot pivots left
    robot.colour(robot.GREEN)
    _drive(0, 100)
    robot.colour(robot.BLACK)
    robot.check()
    time.sleep(PAUSE_S)

    # --- Phase 3: both motors ---
    # Expected: both wheels turn; robot moves forward in a straight line
    robot.colour(robot.WHITE)
    _drive(100, 100)
    robot.colour(robot.BLACK)
    robot.check()
    time.sleep(PAUSE_S)
