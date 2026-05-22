"""
Chapter 2 example — Motor movement

Demonstrates: move, turn, arc, nowait + wait, and speed control with seconds.
"""
import time
import robot

robot.init()

# --- Basic blocking move ---
robot.colour(robot.GREEN)
robot.move(200)      # forward 200 mm, pixel stays green throughout
robot.colour(robot.BLACK)

time.sleep(1)

# --- Turn on the spot ---
robot.colour(robot.BLUE)
robot.turn(90)       # clockwise quarter-turn
robot.colour(robot.BLACK)

time.sleep(1)

# --- Arc ---
robot.colour(robot.CYAN)
robot.arc(150, 90)   # quarter circle, 150 mm radius
robot.colour(robot.BLACK)

time.sleep(1)

# --- nowait: pixel changes colour while motors are still moving ---
robot.colour(robot.GREEN)
robot.move(400, nowait=True)   # start moving, return immediately
robot.colour(robot.BLUE)       # pixel turns blue at once
robot.wait()                   # now block until the move finishes
robot.colour(robot.BLACK)

time.sleep(1)

# --- Drive a square ---
for _ in range(4):
    robot.move(200)
    robot.turn(90)

# --- Speed control: slow move ---
robot.colour(robot.YELLOW)
robot.move(300, seconds=10)    # 300 mm over 10 seconds
robot.colour(robot.BLACK)
