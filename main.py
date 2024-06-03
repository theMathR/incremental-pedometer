import game
import time
import board
import storage
import displayio
import adafruit_st7735r
import terminalio
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.scrolling_label import ScrollingLabel
from game import steps
from game import money
from adafruit_button.button import Button

def EZLabel(text=""):
    return Label(FONT, text=text, color=TEXT_COLOR)

# Importants var

BG_COLOR = 0xffffff
BAR_COLOR = 0xffffff
TEXT_COLOR = 0x000000
TAB_COUNT = -1

FONT = terminalio.FONT
FONT_SIZE = FONT.get_bounding_box()[1]

# Tabs

class Tab(displayio.Group):
    def __init__(self):
        super().__init__()
        self.button_index = 0
        self.buttons = []
        self.button_functions = []
    
    def append(self, g, margin=2):
        if len(self) == 0:
            g.y = 0
        elif isinstance(self[-1], Label):
            g.y = int(self[-1].y+(self[-1].line_spacing*self[-1].text.count('\n')+FONT_SIZE)/2)
        else:
            g.y=self[-1].y+self[-1].height 
        if isinstance(g, Label):
            g.y += int((g.line_spacing*g.text.count('\n')+FONT_SIZE)/2)
        g.y+=margin
        super().append(g)
    
    def _append_button(self, b, f, margin=2):
        self.buttons.append(b)
        self.append(b, margin=margin)
        self.button_functions.append(f)

    def append_button(self, text, function, height=20, margin=2):
        self._append_button(
            Button(x=0, y=0, height=height, label=text, width=160, label_font=FONT),
        function, margin=margin)

    def scroll(self):
        if not self.buttons: return
        if buttons[UP]:
            self.button_index = (self.button_index-1)%len(self.buttons)
        if buttons[DOWN]:
            self.button_index = (self.button_index+1)%len(self.buttons)
        for i in range(len(self.buttons)):
            self.buttons[i].selected = i==self.button_index
        if self.y + self.buttons[self.button_index].y + self.buttons[self.button_index].height > 108:
            self.y = 108-self.buttons[self.button_index].height-self.buttons[self.button_index].y 
        if self.y + self.buttons[self.button_index].y < 0:
            self.y = -self.buttons[self.button_index].y
        if buttons[A]:
            self.button_functions[self.button_index]()


menu_index = 0
tab_init_functions = []
tab_names = []
def tab_init(name):
    tab_names.append(name)
    def decorator(func):
        global TAB_COUNT
        TAB_COUNT+=1
        tab_init_functions.append(func)
        return func
    return decorator
tab_update_functions = []
def tab_update(func):
    tab_update_functions.append(func)
    return func

tab_index = 0

# Init tabs here

@tab_init('Steps')
def init_steps_tab(tab):
    tab.append(EZLabel())
    tab.append_button("Reset step counter", game.reset_steps)
    tab.append(EZLabel())
    tab.append(EZLabel("(1000 steps = 37 cal)"))

@tab_update
def update_steps_tab(tab):
    tab[0].text=f"Steps: {game.steps} ({game.steps*0.037} calories)"
    tab[2].text=f"Total: {game.total_steps} ({game.total_steps*0.037} calories)"


@tab_init('Test')
def init_tab_1(tab):
    tab.append_button("Button 1", lambda: print("Button 1"))
    tab.append_button("Button 2 | 20K", lambda: print("Button 2"))


@tab_update
def update_tab_1(tab):
    pass
    
@tab_init('Secret')
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

# Configuring hardware
# Screen part
def update_screen():
    tabs[tab_index].scroll()
    tab_update_functions[tab_index](tabs[tab_index])
    display.refresh()

def configure_groups():
    global tab_name, status_label, tabs, tab_index, tab_locked, TAB_COUNT
    display.root_group = displayio.Group()
    
    display.root_group.append(Rect(0, 20, 160, 108, fill=BG_COLOR))

    tabs = displayio.Group(y=20)
    display.root_group.append(tabs)
    
    display.root_group.append(Rect(0, 0, 160, 20, fill=BAR_COLOR))
    display.root_group.append(Rect(0, 20, 160, 2, fill=TEXT_COLOR))
    display.root_group.append(Rect(80, 0, 2, 20, fill=TEXT_COLOR))    

    tab_name = Label(FONT,text=tab_names[tab_index], max_characters=29, color=TEXT_COLOR)
    money_label = Label(FONT,text="3,4e128 $", max_characters=29, color=TEXT_COLOR)
    tab_name.y = 10
    tab_name.x = 10
    money_label.y = 10
    money_label.x = 90
    display.root_group.append(tab_name)
    display.root_group.append(money_label)
    tab_locked = False

    for i in range(TAB_COUNT+1): # for the secret tab
        tabs.append(Tab())
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
        auto_refresh=False,
    )
    configure_groups()


def disable_screen():
    global display
    displayio.release_displays()
    display_bus.deinit()
    display = None

# Accelerometer part

accelerometer = ADXL345(I2C(scl=board.GP17, sda=board.GP16))
accelerometer.enable_motion_detection(threshold=10) # TODO: Set threshold
step_done = False

# Buttons now !

buttons = [False]*6
buttons_done = [False]*6

buttons_input = [
    DigitalInOut(board.GP10),
    DigitalInOut(board.GP11),
    DigitalInOut(board.GP12),
    DigitalInOut(board.GP13),
    DigitalInOut(board.GP14),
    DigitalInOut(board.GP15)
]

UP = 2
DOWN = 3
LEFT = 1
RIGHT = 0
A = 4
B = 5

#Buttons vars
last_used = time.monotonic()
last_saved = time.monotonic()
konami_code = [UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A]
konami_index = 0


# Init

for b in buttons_input:
    b.pull = Pull.UP

displayio.release_displays()
enable_screen()

# Main game loop


while True:
    # Check accelerometer
    if accelerometer.events['motion']:
        if accelerometer.acceleration[0] > 2 and step_done == True:
            step_done = False
            game.step()
            update_screen()
            print(game.steps)
        if accelerometer.acceleration[0] < -2:
            step_done = True
    # Checking buttons
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] 
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
                tab_name.text = tab_names[tab_index]
                tabs[tab_index].hidden = False
                menu_index = 0
        if buttons[konami_code[konami_index]]:
            konami_index+=1
            if konami_index == 10:
                tabs[tab_index].hidden = True
                tab_index = -1
                tab_name.text = tab_names[tab_index]
                tabs[tab_index].hidden = False
                konami_index=0
        else: 
            konami_index=0
        update_screen()
    
    t = time.monotonic()
    if display and (t - last_used > 120 or (not tab_locked and buttons[B] and konami_index!=9)):
        disable_screen()
    if t - last_saved > 60:
        last_saved = t
        try:
            storage.remount('/', readonly=False)
            game.save()
            storage.remount('/', readonly=True)
        except RuntimeError:
            print('USB enabled, save skipped')
