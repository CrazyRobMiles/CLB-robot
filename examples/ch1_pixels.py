"""
Chapter 1 example — Pixel colours and sequences
"""
import time
import robot

robot.init()

# Solid colours
robot.colour(robot.RED)
time.sleep(1)

robot.colour(robot.GREEN)
time.sleep(1)

robot.colour(robot.BLUE)
time.sleep(1)

robot.colour(robot.BLACK)
time.sleep(0.5)

# Cycle through all eight named colours
colours = [robot.RED, robot.GREEN, robot.BLUE, robot.CYAN,
           robot.MAGENTA, robot.YELLOW, robot.WHITE, robot.BLACK]

for c in colours:
    robot.colour(c)
    time.sleep(0.5)

robot.colour(robot.BLACK)
