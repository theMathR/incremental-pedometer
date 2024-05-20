import game
import time
import board
import displayio
import adafruit_st7735
from terminalio import FONT
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel

tab_init_functions = []
def tab_init(func):
    tab_init_functions.append(func)
    return func
tab_update_functions = []
def tab_update(func):
    tab_update_functions.append(func)
    return func

# CREATE TABS HERE
TAB_COUNT = 2

@tab_init
def init_tab_0(tab):
    tab.append(Label(FONT, text="Random text go brr", color=0xff0000, y=50))

@tab_update
def update_tab_0(tab):
    tab[0].text += 'r'

@tab_init
def init_tab_1(tab):
    tab.append(Rect(5, 5, 10, 10, fill=0x00ff00))

@tab_update
def update_tab_1(tab):
    tab[0].y += 1

#------------
tab_index = 0
def update_screen():
    temp = status_label.current_index
    status_label.full_text = f"Money: {game.float_to_str(game.money)} | Steps: {game.steps} | " *2
    status_label.current_index = temp
    tab_update_functions[tab_index](tabs[tab_index])
    status_label.update()
    display.refresh()

def configure_groups():
    global status_label, tabs, tab_index, tab_locked
    display.root_group = displayio.Group()
    
    display.root_group.append(Rect(0, 20, 160, 100, fill=0x000000))
    display.root_group.append(Rect(0, 0, 160, 20, fill=0x1f1f1f))

    status_label = ScrollingLabel(FONT, text="Hiii!", max_characters=29, color=0xffffff)
    status_label.y = 10
    display.root_group.append(status_label)

    tabs = displayio.Group(y=20)
    display.root_group.append(tabs)

    tab_locked = False
    
    for i in range(TAB_COUNT):
        tabs.append(displayio.Group())
        tab_init_functions[i](tabs[i])
        tabs[i].hidden = True
    tabs[0].hidden = False
    update_screen()

def enable_screen():
    global display, display_bus
    display_bus = SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)
    display = adafruit_st7735.ST7735(
        FourWire(
            display_bus,
            command=board.GP7,
            chip_select=board.GP6,
            reset=board.GP8,
        ),
        width=160,
        height=128,
        auto_refresh=False
    )
    configure_groups()

def disable_screen():
    global display
    displayio.release_displays()
    display_bus.deinit()
    display = None

displayio.release_displays()
enable_screen()

accelerometer = ADXL345(I2C(scl=board.GP17, sda=board.GP16))
accelerometer.enable_motion_detection() # TODO: Set threshold
step_done = False

buttons_input = [
    DigitalInOut(board.GP10), # Left
    DigitalInOut(board.GP11), # Right
    DigitalInOut(board.GP12), # Up
    DigitalInOut(board.GP13), # Down
    DigitalInOut(board.GP14), # A
    DigitalInOut(board.GP15), # B
]
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
A = 4
B = 5
for b in buttons_input:
    b.pull = Pull.DOWN
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
    bval = [b.value for b in buttons_input]
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
    if display and t - last_used > 15:
        disable_screen()
    if t - last_saved > 60:
        last_saved = t
        game.save()
    
    if display:
        status_label.update()
        display.refresh()

