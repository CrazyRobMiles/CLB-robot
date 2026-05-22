# CLB Robot

A MicroPython library for the **Hull Pixelbot** — an educational robotics platform built around the Raspberry Pi Pico.

## Hardware

| Component | Part |
|---|---|
| Microcontroller | Raspberry Pi Pico (RP2040) |
| Motors | 28BYJ-48 stepper motors × 2 (via ULN2003 drivers) |
| Sensor | HC-SR04 ultrasonic distance sensor |
| LEDs | WS2812B NeoPixel strip (8 pixels) |

> **Note:** The HC-SR04 runs at 5 V. Its echo pin output must be stepped down to 3.3 V (voltage divider) before connecting to the Pico.

## Project Structure

```
robot.py          # Main public API — import this on the Pico
config.py         # Pin assignments and wheel geometry — edit once per build
lib/
  stepper.py      # StepperPair: background ISR-driven motor control
  distance.py     # HCSR04: blocking ultrasonic distance measurement
  pixels.py       # PixelStrip: NeoPixel wrapper
examples/
  ch1_pixels.py   # Beginner: LED colours
  ch2_motors.py   # Intermediate: movement
  ch3_distance.py # Advanced: distance sensing and obstacle avoidance
```

## Setup

1. Copy all files to the Pico (e.g. with [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) or the MicroPico VS Code extension).
2. Edit `config.py` to match your wiring if it differs from the defaults.

### Default pin assignments (`config.py`)

```python
LEFT_PINS         = [15, 14, 13, 12]   # ULN2003 IN1–IN4
RIGHT_PINS        = [8, 9, 10, 11]
PIXEL_PIN         = 6
PIXEL_COUNT       = 8
TRIGGER_PIN       = 5
ECHO_PIN          = 19
WHEEL_DIAMETER_MM = 69.0
WHEEL_SPACING_MM  = 110.0
```

## Usage

```python
import robot

robot.init()

robot.colour(robot.GREEN)     # set all LEDs green

robot.move(300)               # move forward 300 mm
robot.turn(90)                # turn 90 degrees clockwise
robot.arc(200, 45)            # arc: radius 200 mm, 45 degrees

d = robot.distance()          # read distance in mm (-1 if no echo)
if d > 0 and d < 150:
    robot.stop()

robot.wait(1.0)               # pause for 1 second
```

### Colour constants

`RED`, `GREEN`, `BLUE`, `CYAN`, `MAGENTA`, `YELLOW`, `WHITE`, `BLACK`

### API reference

| Function | Description |
|---|---|
| `init()` | Initialise hardware (call once at startup) |
| `move(mm)` | Move forward (`mm > 0`) or backward (`mm < 0`) |
| `turn(degrees)` | Turn clockwise (`degrees > 0`) or anticlockwise |
| `arc(radius_mm, degrees)` | Arc turn with given radius |
| `stop()` | Stop motors immediately |
| `wait(seconds)` | Pause execution |
| `distance()` | Read HC-SR04 distance in mm; `-1` if no echo |
| `colour(rgb)` | Set all NeoPixels to an RGB tuple or colour constant |
| `random_val()` | Return a random integer 1–12 |

## Examples

The `examples/` folder contains three progressively more complex programs:

- **ch1_pixels.py** — cycles through the LED colour constants
- **ch2_motors.py** — demonstrates `move()`, `turn()`, and `arc()`
- **ch3_distance.py** — reads the distance sensor and stops before an obstacle

## Motor implementation notes

Motor stepping runs in a hardware timer ISR at 5 kHz (200 µs period), so movement is non-blocking at the hardware level. The public API calls (`move`, `turn`, `arc`) block until the movement completes and automatically de-energise the coils when done.
