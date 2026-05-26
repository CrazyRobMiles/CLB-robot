"""
Chapter 3 example — Distance sensor

Demonstrates reading distance, conditional colour, and simple obstacle avoidance.
"""
import sys
sys.path.insert(0, '..')
import time
import robot

robot.init()

# --- Print distance readings ---
for _ in range(20):
    mm = robot.distance()
    print("Distance:", mm, "mm")
    robot.check(); time.sleep(0.5)

# --- Colour changes with distance ---
# Green when clear, yellow when close, red when very close
for _ in range(50):
    mm = robot.distance()
    if mm < 0:
        robot.colour(robot.WHITE)   # sensor error
    elif mm < 100:
        robot.colour(robot.RED)
    elif mm < 250:
        robot.colour(robot.YELLOW)
    else:
        robot.colour(robot.GREEN)
    robot.check(); time.sleep(0.2)

# --- Simple obstacle avoidance ---
# Move forward; back up and turn when something is within 150 mm.
robot.colour(robot.GREEN)
while True:
    if robot.distance() < 150:
        robot.colour(robot.RED)
        robot.move(-100)       # back up 100 mm
        robot.turn(90)         # turn right
        robot.colour(robot.GREEN)
    else:
        robot.move(50, nowait=True)   # keep inching forward
        time.sleep(0.1)
        robot.wait()
