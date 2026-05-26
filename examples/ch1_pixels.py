"""
Chapter 1 example — Pixel colours and sequences
"""
import sys
sys.path.insert(0, '..')
import time
import robot

robot.init()

# Solid colours
robot.colour(robot.RED)
robot.check(); time.sleep(1)

robot.colour(robot.GREEN)
robot.check(); time.sleep(1)

robot.colour(robot.BLUE)
robot.check(); time.sleep(1)

robot.colour(robot.BLACK)
robot.check(); time.sleep(0.5)

# Cycle through all eight named colours
colours = [robot.RED, robot.GREEN, robot.BLUE, robot.CYAN,
           robot.MAGENTA, robot.YELLOW, robot.WHITE, robot.BLACK]

for c in colours:
    robot.check()
    robot.colour(c)
    time.sleep(0.5)

robot.colour(robot.BLACK)
