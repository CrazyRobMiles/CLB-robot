# Hull Pixelbot hardware configuration
# Copy this file to your Pico alongside robot.py and lib/.
# Edit the values here once to match your robot's wiring.
# Your programs can then just call robot.init() with no arguments.

# Left motor: ULN2003 IN1-IN4
LEFT_PINS = [15, 14, 13, 12]

# Right motor: ULN2003 IN1-IN4
RIGHT_PINS = [8, 9, 10, 11]

# NeoPixel strip
PIXEL_PIN   = 6
PIXEL_COUNT = 12

# HC-SR04 ultrasonic sensor
# ECHO must be connected through a voltage divider (5V → 3.3V)
TRIGGER_PIN = 17
ECHO_PIN    = 16

# Wheel geometry — adjust these to improve movement accuracy
WHEEL_DIAMETER_MM = 69.0
WHEEL_SPACING_MM  = 110.0
