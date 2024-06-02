import game
import time
import board
import displayio
import adafruit_st7735r
from terminalio import FONT
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel

BG_COLOR = 0x032412
BAR_COLOR = 0x0f0f0f
TEXT_COLOR = 0xFFF5D8
TAB_COUNT = -1

menu_index = 0
tab_init_functions = []
def tab_init(func):
    global TAB_COUNT
    TAB_COUNT+=1
    tab_init_functions.append(func)
    return func
tab_update_functions = []
def tab_update(func):
    tab_update_functions.append(func)
    return func

tab_index = 0
def update_screen():
    temp = status_label.current_index
    status_label.full_text = f"Money: {game.float_to_str(game.money)} | Steps: {game.steps} | "*2
    status_label.current_index = temp
    tab_update_functions[tab_index](tabs[tab_index])
    status_label.update()
    display.refresh()

def configure_groups():
    global status_label, tabs, tab_index, tab_locked, TAB_COUNT
    display.root_group = displayio.Group()
    
    display.root_group.append(Rect(0, 20, 160, 100, fill=BG_COLOR))
    
    tabs = displayio.Group(y=20)
    display.root_group.append(tabs)
    
    display.root_group.append(Rect(0, 0, 160, 20, fill=BAR_COLOR))

    status_label = ScrollingLabel(FONT, text="Hiii!", max_characters=29, color=TEXT_COLOR)
    status_label.y = 10
    display.root_group.append(status_label)
    
    tab_locked = False

    for i in range(TAB_COUNT+1): # for the secret tab
        tabs.append(displayio.Group())
        tab_init_functions[i](tabs[i])
        tabs[i].hidden = True
    tabs[0].hidden = False
    update_screen()

def enable_screen():
    global display, display_bus
    display_bus = SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)
    display = adafruit_st7735r.ST7735R(
        FourWire(
            display_bus,
            command=board.GP7,
            chip_select=board.GP6,
            reset=board.GP8,
        ),
        rotation=270,
        width=160,
        height=128,
        backlight_pin=board.GP5,
        auto_refresh=False
    )
    configure_groups()

def disable_screen():
    global display
    displayio.release_displays()
    display_bus.deinit()
    display = None

accelerometer = ADXL345(I2C(scl=board.GP17, sda=board.GP16))
accelerometer.enable_motion_detection(threshold=20) # TODO: Set threshold
step_done = False

buttons_input = [
    DigitalInOut(board.GP10), # Left
    DigitalInOut(board.GP11), # Right
    DigitalInOut(board.GP12), # Up
    DigitalInOut(board.GP13), # Down
    DigitalInOut(board.GP14), # A
    DigitalInOut(board.GP15), # B
]
UP = 2
DOWN = 3
LEFT = 1
RIGHT = 0
A = 4
B = 5
for b in buttons_input:
    b.pull = Pull.UP
buttons = [False]*6
buttons_done = [False]*6

konami_code = [UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A]
konami_index = 0

last_used = time.monotonic()
last_saved = time.monotonic()


# CREATE TABS HERE
    
@tab_init
def init_steps_tab(tab):
    tab.append(Label(FONT, text=f"Steps: {game.steps} ({game.steps*0.037} calories)\nPress A to reset the count\nTotal: {game.total_steps} ({game.total_steps*0.037} calories)\n(1000 steps = 37 cal)", color=TEXT_COLOR, y=50))

@tab_update
def update_steps_tab(tab):
    tab[0].text=f"Steps: {game.steps} ({game.steps*0.037} calories)\nPress A to reset\nTotal: {game.total_steps} ({game.total_steps*0.037} calories)\n(1000 steps = 37 cal)"
    if buttons[A]:
        game.reset_steps()

@tab_init
def init_tab_1(tab):
    tab.append(Rect(5, 5, 10, 10, fill=0x00ff00))

@tab_update
def update_tab_1(tab):
    tab[0].y += 1
    
@tab_init
def init_secret_tab(tab):
    tab.append(Label(FONT, text="This is MathR's secret tab,\n           enjoy.", color=0x00ff00, y=30, x=0))
    bitmap=displayio.OnDiskBitmap("/assets/secret_nubert.bmp")
    nubert=displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    nubert.x = 69 # nice
    nubert.y = 60
    tab.append(nubert)

@tab_update
def update_secret_tab(tab):
    pass
#------------

displayio.release_displays()
enable_screen()

# THE HOLY MAIN LOOP
while True:
    # Check accelerometer
    if accelerometer.events['motion']:
        if not step_done:
            game.step()
            if display != None:
                update_screen()
        if not step_done%2:
            step_done += 1
    else:
        if step_done % 2:
            step_done = (step_done+1)%4
    
    # Check buttons
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] # To not count already pressed buttons
    if True in buttons:
        last_used = time.monotonic()
        if display == None:
            enable_screen()
            menu_index = 0
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
                menu_index = 0
        if buttons[konami_code[konami_index]]:
            konami_index+=1
            if konami_index == 10:
                tabs[tab_index].hidden = True
                tab_index = -1
                tabs[tab_index].hidden = False
                konami_index=0
        else: konami_index=0
        update_screen()
    
    t = time.monotonic()
    if display and (t - last_used > 15 or (not tab_locked and buttons[B] and konami_index!=9)):
        disable_screen()
    if t - last_saved > 60:
        last_saved = t
        game.save()
    
    if display:
        status_label.update()
        display.refresh()
        