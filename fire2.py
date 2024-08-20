#!/usr/bin/env python3
import time
import random
import argparse
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color

# Configuration:
LED_COUNT = 144        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 200  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
SENSOR_PIN = 23       # Sensor pin for KY-002

# Fire simulation classes
class Fireplace:
    fire_color = Color(80, 35, 0)
    off_color = Color(0, 0, 0)
    strip = None

    def __init__(self, strip):
        self.strip = strip

    def draw(self):
        self.clear()
        for i in range(LED_COUNT):
            self.add_color(i, self.fire_color)
            r = random.randint(0, 80)
            diff_color = Color(r, r // 2, r // 2)
            self.subtract_color(i, diff_color)
        self.strip.show()

    def clear(self):
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, self.off_color)

    def add_color(self, position, color):
        blended_color = self.blend(self.strip.getPixelColor(position), color)
        self.strip.setPixelColor(position, blended_color)

    def subtract_color(self, position, color):
        blended_color = self.subtract(self.strip.getPixelColor(position), color)
        self.strip.setPixelColor(position, blended_color)

    def blend(self, color1, color2):
        r1, g1, b1 = self.unpack_color(color1)
        r2, g2, b2 = self.unpack_color(color2)
        return Color(min(r1 + r2, 255), min(g1 + g2, 255), min(b1 + b2, 255))

    def subtract(self, color1, color2):
        r1, g1, b1 = self.unpack_color(color1)
        r2, g2, b2 = self.unpack_color(color2)
        r = max(r1 - r2, 0)
        g = max(g1 - g2, 0)
        b = max(b1 - b2, 0)
        return Color(r, g, b)

    @staticmethod
    def unpack_color(color):
        return (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff

class Fireflame:
    normal_fire_color = Color(100, 30, 0)
    big_fire_flame = Color(220, 80, 0)
    off_color = Color(0, 0, 0)
    strip = None

    def __init__(self, strip):
        self.strip = strip

    def draw(self, color=None):
        self.clear()
        if color is None:
            color = self.normal_fire_color
        for i in range(LED_COUNT):
            self.add_color(i, color)
            r = random.randint(0, 30) + 50  # (0,80)
            diff_color = Color(r, r // 3, r // 4) #(r,r 2, r 2)
            self.subtract_color(i, diff_color)
        self.strip.show()

    def clear(self):
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, self.off_color)

    def add_color(self, position, color):
        current_color = self.strip.getPixelColor(position)
        blended_color = self.blend(current_color, color)
        self.strip.setPixelColor(position, blended_color)

    def subtract_color(self, position, color):
        current_color = self.strip.getPixelColor(position)
        blended_color = self.subtract(current_color, color)
        self.strip.setPixelColor(position, blended_color)

    def blend(self, color1, color2):
        r1, g1, b1 = self.unpack_color(color1)
        r2, g2, b2 = self.unpack_color(color2)
        return Color(min(r1 + r2, 255), min(g1 + g2, 255), min(b1 + b2, 255))

    def subtract(self, color1, color2):
        r1, g1, b1 = self.unpack_color(color1)
        r2, g2, b2 = self.unpack_color(color2)
        r = max(r1 - r2, 0)
        g = max(g1 - g2, 0)
        b = max(b1 - b2, 0)
        return Color(r, g, b)

    @staticmethod
    def unpack_color(color):
        return (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff

    def big_flame(self, duration=0.5):
        """Show a big flame effect for a short duration."""
        self.draw(self.big_fire_flame)  # Draw big flame
        time.sleep(duration)        # Hold the flame for the specified duration
        self.clear()                # Clear the flame
        self.strip.show()
        #self.draw()

def debounce(sensor_pin, debounce_time_ms=50):
    """
    Debounces the input from a GPIO sensor pin.

    Args:
        sensor_pin (int): The GPIO pin number where the sensor is connected.
        debounce_time_ms (int): The debounce time in milliseconds. Default is 50 ms.

    Returns:
        bool: The debounced state of the sensor (True if triggered, False otherwise).
    """
    stable_state = GPIO.input(sensor_pin)
    last_state = stable_state
    start_time = time.time()

    while True:
        current_state = GPIO.input(sensor_pin)

        if current_state != last_state:
            # State has changed, reset the debounce timer
            start_time = time.time()
            last_state = current_state

        # Check if the state has been stable for the debounce time
        elapsed_time = (time.time() - start_time) * 1000.0
        if elapsed_time >= debounce_time_ms:
            if current_state == stable_state:
                return stable_state
            else:
                stable_state = current_state
                return stable_state

def flame_up(fire):
    # Occasionally trigger a big flame effect
    if random.random() < 0.95:  # 95% chance to trigger big flame
        fire.big_flame(duration=0.9)  # Adjust duration as needed
        time.sleep(random.uniform(0.05, 0.20))

def shake_wrapper(fire):
    # Wrappes the callback function for custom a parameter
    def wrapped_callback(channel):
        shake(channel, fire)
    return wrapped_callback

def shake(channel):
    # Entprellfunktion: Timer setzen (200 ms)
    # Verhindert wiederholte ausführung
    debounced_state = debounce(SENSOR_PIN)
    if debounced_state:
        print("Vibration detected!")
        flame_up(fire)
    else:
        print("Debounced!")

# Init LEDs with NeoPixel
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
fire = Fireflame(strip)
fire.draw()
time.sleep(random.uniform(0.05, 0.20))

# Main
if __name__ == '__main__':
    print("Start fire show")
    # Process arguments
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    # Init vibration Sensor with KY-002
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(SENSOR_PIN, GPIO.FALLING, callback=shake, bouncetime=100) 

    try:
        while True:
            time.sleep(1)
            fire.draw()
    except KeyboardInterrupt:
         print("Program terminated!")
    finally:
         fire.clear()
         GPIO.cleanup()
