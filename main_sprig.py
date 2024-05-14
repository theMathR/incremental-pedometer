import game
from consts import *
import time
import board
import displayio
import adafruit_st7735r
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel

def configure_groups():
    global status_label, menu, menu_index
    display.root_group = displayio.Group()
    display.root_group.append(Rect(0, 0, WIDTH, HEIGHT, fill=BG_COLOR))

    status_bar_group = displayio.Group()
    display.root_group.append(status_bar_group)
    status_bar_group.append(Rect(0, 0, WIDTH, BAR_HEIGHT, fill=BAR_COLOR))
    status_label = Label(FONT, text="Hiii!", color=TEXT_COLOR)
    status_label.y = BAR_HEIGHT//2
    status_bar_group.append(status_label)

    menu = displayio.Group(y=BAR_HEIGHT)
    display.root_group.append(menu)

    menu_index = 0
    
def enable_screen():
    global display, display_bus
    display_bus = SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
    display = adafruit_st7735r.ST7735R(
        FourWire(
            display_bus,
            command=board.GP22,
            chip_select=board.GP20,
            reset=board.GP26,
        ),
        rotation=270,
        width=160,
        height=128,
        backlight_pin=board.GP17
    )
    configure_groups()

def disable_screen():
    global display
    displayio.release_displays()
    display_bus.deinit()
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

def update_screen():
    status_label.text = str(game.steps)

accelerometer_sim = DigitalInOut(board.GP12)
accelerometer_sim.pull = Pull.UP
step_done = False

buttons_input = [
    DigitalInOut(board.GP6), # Left
    DigitalInOut(board.GP8), # Right
    DigitalInOut(board.GP5), # Up
    DigitalInOut(board.GP7), # Down
    DigitalInOut(board.GP15), # A
    DigitalInOut(board.GP14), # B
]
for b in buttons_input: # It's useful
    b.pull = Pull.UP
buttons = [False]*6
buttons_done = [False]*6

last_used = time.monotonic()

# THE HOLY MAIN LOOP

while True:
    # Check accelerometer
    if not accelerometer_sim.value:
        if not step_done:
            game.step()
            step_done = True
            if display != None:
                update_screen()
    else:
        step_done = False
    
    # Check buttons
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] # To not count already pressed buttons
    if True in buttons:
        last_used = time.monotonic()
        if display == None:
            enable_screen()
        update_screen()
    
    if display and time.monotonic() - last_used > 10:
        disable_screen()
