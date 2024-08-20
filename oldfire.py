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
LED_BRIGHTNESS = 180  # Set to 0 for darkest and 255 for brightest
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
    normal_fire_color = Color(80, 35, 0)
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
            r = random.randint(0, 80)
            diff_color = Color(r, r // 2, r // 2)
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

def alarm(timer):
    print()
    print('Bewegung')
    print()
    print('Ruhe')

def shake(pin):
    # Entprellfunktion: Timer setzen (200 ms)
    # Verhindert wiederholte ausführung
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=alarm)

# Main
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Init LEDs with NeoPixel
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    # Create an instance of the NeoFire class
    fire = Fireflame(strip)

    # Init vibration Sensor with KY-002
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(SENSOR_PIN, GPIO.FALLING, callback=shake, bouncetime=100) 

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
           #fire.draw()
           #time.sleep(random.uniform(0.05, 0.2))

           # Simulate normal fire flickering
           fire.draw()
           time.sleep(random.uniform(0.05, 0.20))

           # Occasionally trigger a big flame effect
           if random.random() < 0.1:  # 10% chance to trigger big flame
               fire.big_flame(duration=0.2)  # Adjust duration as needed

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
            GPIO.cleanup()
