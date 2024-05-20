import game
import time
import board
import displayio
import adafruit_st7735r
from terminalio import FONT
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel

TAB_COUNT = 2
def configure_groups():
    global status_label, tabs, tab_index, tab_locked
    display.root_group = displayio.Group()
    
    display.root_group.append(Rect(0, 0, 160, 128, fill=0x0f0f0f))
    display.root_group.append(Rect(0, 20, 160, 10, fill=0x000000))

    status_label = Label(FONT, text="Hiii!", color=0xffffff)
    status_label.y = 10
    display.root_group.append(status_label)

    tabs = displayio.Group(y=20)
    display.root_group.append(tabs)

    tab_index = 0
    tab_locked = False
    
    # Init tab 0
    tabs.append(displayio.Group())
    tabs[0].append(Label(FONT, text="Random text go brrrrrrr", color=0xff0000))
    
    # Init tab 1
    tabs.append(displayio.Group())
    tabs[1].hidden = True
    tabs[1].append(Rect(5, 5, 10, 10, fill=0x00ff00))

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
#  L tab
#  L 

def update_tab_0():
    tabs[0][0].text += '!'

def update_tab_1():
    tabs[1][0].x = game.steps//10

def update_screen():
    status_label.text = f"Money: {game.money} | Steps: {game.steps}"
    [
        update_tab_0,
        update_tab_1
    ][tab_index]()
    display.refresh()

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
UP = 2
DOWN = 3
LEFT = 0
RIGHT = 1
A = 4
B = 5
for b in buttons_input: # Idk if it's useful
    b.pull = Pull.UP
buttons = [False]*6
buttons_done = [False]*6

last_used = time.monotonic()
last_saved = time.monotonic()

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
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] # To not count already pressed buttons
    if True in buttons:
        last_used = time.monotonic()
        if display == None:
            enable_screen()
        elif not tab_locked:
            move = 0
            if buttons[LEFT]:
                move = -1
            if buttons[RIGHT]:
                move = 1
            if move != 0:
                tabs[tab_index].hidden = True
                tab_index = (tab_index+move)%TAB_COUNT
                tabs[tab_index].hidden = False
        update_screen()
    
    t = time.monotonic()
    if display and t - last_used > 10:
        disable_screen()
    if t - last_saved > 60:
        last_saved = t
        game.save()
    
