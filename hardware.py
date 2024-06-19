import RPi.GPIO as GPIO
import ST7735

BUTTONS = [5, 6, 16, 24]
LABELS = ["A", "B", "X", "Y"]

def setup_gpio(button_pins, handle_button):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(button_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in button_pins:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=200)

def initialize_display():
    display = ST7735.ST7735(
        port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=80000000
    )
    display.begin()
    return display
