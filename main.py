import game
import time
import board
import storage
import displayio
import adafruit_st7735r
import terminalio
from themes import themes, theme_names
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_display_text import LabelBase
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_button.button import Button

import supervisor
supervisor.runtime.autoreload = False

f2str = game.float_to_str

def add_newlines(text):
    words = text.split(" ")
    lines = ['']
    for w in words:
        if '\n' in w:
            w = w.split('\n')
            lines[-1] += w[0]
            w = w[1]
            lines.append('')
        if len(lines[-1] + w + ' ') > 21:
            lines.append('')
        lines[-1] += w + ' '
    return '\n'.join(lines)

def EZLabel(text=""):
    return Label(FONT, text=text, color=theme[2], x=1)

# Importants var
TAB_COUNT = -1

FONT = terminalio.FONT
FONT_SIZE = FONT.get_bounding_box()[1]

# Tabs
tab_locked = False
class Tab(displayio.Group):
    def __init__(self):
        self.popup_open = False
        super().__init__()
        self.button_index = 0
        self.buttons = []
        self.button_functions = []
    
    def append(self, g, margin=2):
        if len(self) == 0:
            g.y = 0
        elif isinstance(self[-1], LabelBase):
            g.y = int(self[-1].y+(self[-1].line_spacing+FONT_SIZE)*self[-1].text.count('\n')+FONT_SIZE/2)
        else:
            g.y=self[-1].y+self[-1].height 
        if isinstance(g, LabelBase):
            g.y += int((g.line_spacing*g.text.count('\n')+FONT_SIZE)/2)
        g.y+=margin
        super().append(g)
    
    def _append_button(self, b, f, margin=2):
        self.buttons.append(b)
        self.append(b, margin=margin)
        self.button_functions.append(f)

    def append_button(self, text, function, height=20, margin=None):
        if margin is None: margin = 1 if len(tab) and isinstance(tab[-1], Button) else 2
        self._append_button(
            Button(x=0, y=0, height=height, label=text, width=160, label_font=FONT,
            label_color=theme[2], fill_color=theme[1], outline_color=theme[2],
            selected_label=theme[1], selected_fill=theme[3], selected_outline=theme[2]),
        function, margin=margin)

    def scroll(self):
        if not self.buttons: return
        if self.popup_open:
            if buttons[A]:
                self.close_popup()
            return
        if buttons[UP]:
            if self.button_index==0 and self.y != 0:
                self.y=0
            else:
                self.button_index = (self.button_index-1)%len(self.buttons)
        if buttons[DOWN]:
            self.button_index = (self.button_index+1)%len(self.buttons)
            if self.button_index==0:
                self.y = 0
        for i in range(len(self.buttons)):
            self.buttons[i].selected = i==self.button_index
        if self.y + self.buttons[self.button_index].y + self.buttons[self.button_index].height > 103:
            self.y = 103-self.buttons[self.button_index].height-self.buttons[self.button_index].y 
        if self.y + self.buttons[self.button_index].y < 0:
            self.y = -self.buttons[self.button_index].y
        if buttons[A]:
            self.button_functions[self.button_index]()

    def create_popup(self, text):
        global tab_locked
        text = add_newlines(text)
        self.popup_open = True
        tab_locked = True
        popup = displayio.Group()
        popup.x=12
        popup.y=11
        popup.append(Label(FONT, text=text, color=theme[2], x=4, y=30-int(text.count('\n')*FONT_SIZE/2)))
        button = Button(x=3, y=62, height=20, label='Close', width=129, label_font=FONT,
            label_color=theme[2], fill_color=theme[1], outline_color=theme[2],
            selected_label=theme[1], selected_fill=theme[3], selected_outline=theme[2])
        button.selected = True
        popup.append(button)
        tab_container.append(Rect(12, 11, 135, 86, fill=theme[0], outline=theme[2], stroke=2))
        tab_container.append(popup)
    
    def close_popup(self):
        global tab_locked
        self.popup_open = False
        tab_locked = False
        tab_container.pop()
        tab_container.pop()

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
def init_steps_tab():
    tab.append(EZLabel())
    tab.append_button("Reset step counter", game.reset_steps)
    tab.append(EZLabel())
    tab.append(EZLabel("(1000 steps = 37 cal)"))

@tab_update
def update_steps_tab():
    tab[0].text=f"Steps: {game.steps} ({game.steps*0.037} calories)"
    tab[2].text=f"Total: {game.total_steps} ({game.total_steps*0.037} calories)"


@tab_init('Money')
def init_money_tab():
    tab.append(EZLabel(f"You gain {f2str(game.money_gained)} $/step"))
    
    tab.append(EZLabel(f'You have {f2str(game.money_upgrades)}\n money upgrades'), margin=5)
    tab.append_button(f'Buy one for {f2str(game.money_upgrade_price)}$', do_then_update(check_money(game.buy_money_upgrade)))
    
    tab.append(EZLabel(f"Your energy is at {f2str(game.energy)}%"), margin=5)
    tab.append(EZLabel(f"You lose energy every step\nand it reduces your money gain"))
    tab.append_button(f'Eat a cereal bar for 500$', check_money(game.buy_cereal_bar))

@tab_update
def update_money_tab():
    tab[0].text = f"You gain {f2str(game.money_gained)} $/step"
    tab[1].text = f'You have {f2str(game.money_upgrades)}\n money upgrades'
    tab[3].text = f"Your energy is at {f2str(game.energy)}%"

@tab_init('Autobuyers')
def init_autobuyers_tab():
    tab.append(EZLabel(f'You have {game.money_upgrades_autobuyers}\nmoney upgrade autobuyers'))
    tab.append_button(f'Buy one for {f2str(game.money_upgrades_autobuyer_price)}$', do_then_update(check_money(game.buy_money_upgrades_autobuyer)))
    tab.append_button(f'Press to turn {"off" if game.money_upgrades_autobuyers_on else "on"}', do_then_update(game.toggle_money_upgrades_autobuyers))
    
    tab.append(EZLabel(f'You have {game.cereal_bar_autobuyers}\nmoney upgrade autobuyers'), margin=5)
    tab.append_button(f'Buy one for {f2str(game.cereal_bar_autobuyer_price)}$', do_then_update(check_money(game.buy_cereal_bar_autobuyer)))
    
    if not game.nb_orpheus: return
    tab.append(EZLabel(f'You have {game.apple_autobuyers}\napple autobuyers'), margin=5)
    tab.append_button(f'Buy one for {f2str(game.apple_autobuyer_price)}$', do_then_update(check_money(game.buy_apple_autobuyer)))

@tab_update
def update_autobuyers_tab():
    pass

item_select_info = None

def begin_selection(sock_or_shoe, unequip=False):
    def wrapped():
        global item_select_info, tab_locked
        if not unequip and len(game.socks if sock_or_shoe == game.SOCK else game.shoes) == len(game.socks_equipped if sock_or_shoe == game.SOCK else game.shoes_equipped):
            tab.create_popup(f'You don\'t have any unequipped {"sock" if sock_or_shoe == game.SOCK else "shoe"}s!')
            return False
        tab_locked = True
        item_select_info = [sock_or_shoe]
        if unequip:
            item_select_info.append(index)
            game.equip(item_select_info[0], None, index)
        return True
    return do_then_update(wrapped)

def select_item(function):
    def wrapped():
        global item_select_info, tab_locked
        function()
        tab_locked = False
        item_select_info = None
        return True
    return do_then_update(wrapped)

def list_items(function):
    for i, item in enumerate(game.socks if item_select_info[0] == game.SOCK else game.shoes):
        if i in (game.socks_equipped if item_select_info[0] == game.SOCK else game.shoes_equipped):
            continue
        tab.append_button(item.name, select_item(function(i)))

def equip(index):
    return lambda: game.equip(item_select_info[0], index, item_select_info[1])

@tab_init('Feet')
def init_feet_tab():
    if item_select_info is None:
        tab.append(EZLabel(f'You have {game.feet} feet.'))
        for i in range(game.feet):
            tab.append_button("Sock: " + (game.socks[game.socks_equipped[i]].name if isinstance(game.socks_equipped[i], int) else "Nothing"),
                begin_selection(game.SOCK, True), margin=5)
            tab.append_button("Shoe: " + (game.shoes[game.shoes_equipped[i]].name if isinstance(game.shoes_equipped[i], int) else "Nothing"),
                begin_selection(game.SHOE, True))
        if game.feet < 9: tab.append_button(f'New foot for {f2str(game.foot_price)}$', do_then_update(check_money(game.buy_foot)), margin=5)
    else:
        tab.append(EZLabel(f'Select a {"sock" if item_select_info[0] == game.SOCK else "shoe"} to equip:'))
        list_items(equip)

@tab_update
def update_feet_tab():
    pass # TODO: Change equipped feet

@tab_init('Inventory')
def init_inventory_tab():
    tab.append_button(f"Buy shoe for {game.shoe_price}$", do_then_update(check_money(game.buy_shoe)))
    tab.append_button(f"Buy sock for {game.sock_price}$", do_then_update(check_money(game.buy_sock)))
    
    tab.append_button(f"List shoes", lambda: None, margin=5)
    tab.append_button(f"List socks", lambda: None)
    return
    # TODO
    tab.append(EZLabel('Click on an item to see \nits description'), margin=5)
    tab.append(EZLabel(f'Shoes: ({len(game.shoes)}/10)'), margin = 5)
    for shoe in game.shoes:
        tab.append_button(shoe.name, lambda: (tab.create_popup(shoe.name + ':\n' + shoe.description)))
    tab.append_button('Remove shoe', begin_selection(game.SHOE))
    
    
    tab.append(EZLabel(f'Socks: ({len(game.socks)}/10)'), margin = 5)
    for sock in game.socks:
        tab.append_button(sock.name, lambda: (tab.create_popup(sock.name + ':\n' + sock.description)))
    tab.append_button('Remove shoe', begin_selection(game.SOCK))


@tab_update
def update_inventory_tab():
    pass

@tab_init('Training')
def init_training_tab():
    if not game.training_mode_unlocked:
        tab.append_button('Unlock for 5000$', do_then_update(check_money(game.unlock_training_mode)))
        return
    tab.append(EZLabel('In training mode\nenergy is way more\npunishing.\nGet as much money\nas possible to\nmake the energy limit higher!'))
    tab.append(EZLabel(f'Current max energy: {f2str(100+game.muscles)}%'))
    tab.append_button('Enter training mode', do_then_update(game.toggle_training_mode))

@tab_update
def update_training_tab():
    if game.training_mode:
        tab[2].label = f"Stop for +{f2str(game.money_to_muscles()-game.muscles)}%"

@tab_init('Orpheus')
def init_orpheus_tab():
    tab.append(EZLabel('Sacrificing will\nreset your entire\nprogression except\n your items.\nIn exchange you summon\nOrpheus who will\nboost your production!'))
    tab.append_button(f'Sacrifice for {f2str(game.sacrifice_price)}$', do_then_update(check_money(game.sacrifice)))
    
    if not game.nb_orpheus: return
    tab.append(EZLabel(f'Orpheus count: {f2str(nb_orpheus)}'))
    
    tab.append(EZLabel(f"Their energy is at {f2str(game.energy_orpheus)}%"), margin=5)
    tab.append_button('Give them an apple for 1000$', game.buy_apple)
    
    # TODO: Les sprites d'Orpheus!
    # N'oublie pas de rajouter une limite car il va en avoir de + en +

@tab_update
def update_orpheus_tab():
    if game.nb_orpheus:
        tab[-2].text = f"Their energy is at {f2str(game.energy_orpheus)}%"

@tab_init('Settings')
def init_settings_tab():
    tab.append(EZLabel())
    tab.append_button('Change theme', change_theme)
    tab.append(EZLabel(), margin=5)
    tab.append_button('Change notation', game.change_notation)

@tab_update
def update_settings_tab():
    tab[0].text = f'Theme: {theme_names[game.theme_index]}'
    tab[2].text = f'Notation: {["Scientific","Standard","Mixed scientific"][game.notation]}'

@tab_init('Secret')
def init_secret_tab():
    tab.append(Label(FONT, text="This is MathR's secret tab,\n           enjoy.", color=theme[2], y=30, x=0))
    bitmap=displayio.OnDiskBitmap("/assets/secret_nubert.bmp")
    nubert=displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    nubert.x = 69 # nice
    nubert.y = 60
    tab.append(nubert)

@tab_update
def update_secret_tab():
    pass
#------------

# Configuring hardware
# Screen part
def update_screen():
    tab.scroll()
    tab_update_functions[tab_index]()
    money_label.text = game.float_to_str(game.money)+"$"
    display.refresh()

def change_theme():
    game.change_theme(len(themes))
    buttons[A] = False
    configure_groups()

def do_then_update(func):
    def wrapped():
        global tab
        buttons[A] = False
        i = tab.button_index
        if not func(): return
        tab_container.pop()
        tab = Tab()
        tab_container.append(tab)
        tab_init_functions[tab_index]()
        tab.button_index = min(len(tab.buttons)-1, i)
        update_screen()
    return wrapped

def check_money(func):
    def wrapped():
        v = func()
        if not v:
            tab.create_popup("You don't have enough money!")
        return v
    return wrapped

def configure_groups():
    global tab_name, money_label, tab, tab_container, tab_index, tab_locked, TAB_COUNT, theme
    theme = themes[game.theme_index]
    
    display.root_group = displayio.Group()
    
    display.root_group.append(Rect(0, 20, 160, 108, fill=theme[0]))

    tab_container = displayio.Group(y=25)
    display.root_group.append(tab_container)
    
    display.root_group.append(Rect(0, 0, 160, 20, fill=theme[1]))
    display.root_group.append(Rect(0, 20, 160, 2, fill=theme[2]))
    display.root_group.append(Rect(80, 0, 2, 20, fill=theme[2]))    

    tab_name = Label(FONT,text=tab_names[tab_index], max_characters=29, color=theme[2])
    money_label = Label(FONT,text=game.float_to_str(game.money), max_characters=29, color=theme[2])
    tab_name.y = 10
    tab_name.x = 10
    money_label.y = 10
    money_label.x = 90
    display.root_group.append(tab_name)
    display.root_group.append(money_label)
    tab_locked = False

    tab=Tab()
    tab_container.append(tab)
    tab_init_functions[tab_index]()

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

def switch_tab():
    global tab
    tab_name.text = tab_names[tab_index]
    tab_container.pop()
    tab=Tab()
    tab_init_functions[tab_index]()
    tab_container.append(tab)


def disable_screen():
    global display
    displayio.release_displays()
    display_bus.deinit()
    display = None

def save():
    try:
        storage.remount('/', readonly=False)
        game.save()
        storage.remount('/', readonly=True)
    except RuntimeError:
        print('USB enabled, save skipped')

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
            if display: update_screen()
        if accelerometer.acceleration[0] < -2:
            step_done = True
    # Checking buttons
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] 
    if True in buttons:
        last_used = time.monotonic()
        if display == None:
            buttons = [False]*6
            enable_screen()
        else:
            if not tab_locked:
                move = 0
                if buttons[LEFT]:
                    move = -1
                if buttons[RIGHT]:
                    move = 1
                if move != 0:
                    tab_index = (tab_index+move)%TAB_COUNT
                    switch_tab()
            if buttons[konami_code[konami_index]]:
                konami_index+=1
                if konami_index == 10:
                    tab_index = -1
                    switch_tab()
                    konami_index=0
            else: 
                konami_index=0
            update_screen()

    t = time.monotonic()
    if display and (not tab_locked) and (t - last_used > 120 or (buttons[B] and konami_index!=9)):
        save()
        disable_screen()
    if t - last_saved > 60:
        last_saved = t
        save()

