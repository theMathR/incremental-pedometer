import board
import displayio
import adafruit_st7735
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.label import Label
from adafruit_display_text.scrolling_label import ScrollingLabel
from adafruit_bitmap_font import bitmap_font

# Constants
WIDTH = 160
HEIGHT = 128
BAR_HEIGHT = 20
BG_COLOR = 0x000000
BAR_COLOR = 0x0f0f0f
TEXT_COLOR = 0xffffff
raise NotImplementedError('Configure a font first!')
FONT = bitmap_font.load_font("/fonts/font.bdf")

# Configure display

displayio.release_displays()

raise NotImplementedError('Configure the proper pins first, idiot!')
display_bus = displayio.FourWire(
    board.SPI(),
)

display = adafruit_st7735.ST7735(
    display_bus,
    width=128,
    height=160,
    auto_refresh=False
)

# Configure groups
# The tree looks like this:
# root_group
#  L Background rect
#  L status_bar_group
#  |   L Background rect
#  |   L Information label
#  L menus
#      L One group for each menu, only one shown at once

display.root_group = displayio.Group()
display.root_group.append(Rect(0, 0, WIDTH, HEIGHT, fill=BG_COLOR))

status_bar_group = displayio.Group()
display.root_group.append(status_bar_group)
status_bar_group.append(Rect(0, 0, WIDTH, BAR_HEIGHT, fill=BAR_COLOR))
status_label = Label(FONT, text="Hiii!", color=TEXT_COLOR)
status_bar_group.append(status_label)

menus = displayio.Group(y=BAR_HEIGHT)
display.root_group.append(menus)

menu_index = 0
menu_number = 1

for i in range(menu_number):
    menus.append(displayio.Group())
    menus[i].hidden = True
menus[menu_index].hidden = False

# Functions to create and update each menu

def init_test_menu():
    pass

def update_test_menu():
    pass

init_functions = [init_test_menu]
update_functions = [update_test_menu]

for i in init_functions:i()

def update():
    update_functions[menu_index]()
    status_label.text = 'Updated!'
    display.refresh()

def set_menu(new_index):
    menus[menu_index].hidden = True
    menu_index = new_index
    menus[menu_index].hidden = False

update()
