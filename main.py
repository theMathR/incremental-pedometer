import game
from consts import *

import board
import displayio
import adafruit_st7735
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel

def enable_screen():
    global display
    display = adafruit_st7735.ST7735(
        ddisplayio.FourWire(
            board.SPI() # TODO: Set pinout
        ),
        width=WIDTH,
        height=HEIGHT,
        auto_refresh=False
    )
    configure_groups()

def disable_screen():
    global display
    displayio.release_displays()
    display = None

displayio.release_displays()
enable_screen()

# Configure groups for display
# The tree looks like this:
# root_group
#  L Background rect
#  L status_bar_group
#  |   L Background rect
#  |   L Information label
#  L menu

def configure_groups():
    global status_label, menu, menu_index
    display.root_group = displayio.Group()
    display.root_group.append(Rect(0, 0, WIDTH, HEIGHT, fill=BG_COLOR))

    status_bar_group = displayio.Group()
    display.root_group.append(status_bar_group)
    status_bar_group.append(Rect(0, 0, WIDTH, BAR_HEIGHT, fill=BAR_COLOR))
    status_label = Label(FONT, text="Hiii!", color=TEXT_COLOR)
    status_bar_group.append(status_label)

    menu = displayio.Group(y=BAR_HEIGHT)
    display.root_group.append(menus)

    menu_index = 0

def update_screen():
    status_label.text = str(game.steps)

accelerometer = ADXL345(board.I2C()) # TODO: Set pinout
accelerometer.enable_motion_detection() # TODO: Set threshold
step_done = False

# TODO: Set pinout
buttons_input = [
    DigitalInOut(board.D1),
    DigitalInOut(board.D1),
    DigitalInOut(board.D1),
    DigitalInOut(board.D1),
    DigitalInOut(board.D1),
    DigitalInOut(board.D1),
]
for b in buttons_input: # Idk if it's useful
    b.pull = Pull.DOWN
buttons = [False]*6
buttons_done = [False]*6

# THE HOLY MAIN LOOP
while True:
    # Check accelerometer
    if accelerometer.events['motion']:
        if not step_done:
            game.step()
            step_done = True
            if display != None:
                update_screen()
    else:
        step_done = False
    
    # Check buttons
    buttons = [b.value and not d for b,d in buttons_input, buttons_done]
    buttons_done = [b.value for b in buttons_input] # To not count already pressed buttons
    if True in buttons:
        if display == None:
            enable_screen()
        update_screen()
