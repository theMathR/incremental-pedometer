import game
import time
import board
import displayio
import adafruit_st7735r
import socketpool
import wifi
from terminalio import FONT
from gc import collect, mem_alloc
from math import floor
from ipaddress import ip_address
from themes import themes, theme_names
from busio import I2C, SPI
from fourwire import FourWire
from digitalio import DigitalInOut, Pull
from adafruit_adxl34x import ADXL345
from vectorio import Rectangle
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
        tab_container.append(Rectangle(pixel_shader=theme, width=139, height=90, x=10, y=9, color_index=2))
        tab_container.append(Rectangle(pixel_shader=theme, width=135, height=86, x=12, y=11, color_index=0))
        #tab_container.append(Rect(12, 11, 135, 86, fill=theme[0], outline=theme[2], stroke=2))
        tab_container.append(popup)
    
    def close_popup(self):
        global tab_locked
        self.popup_open = False
        tab_locked = False
        tab_container.pop()
        tab_container.pop()
        tab_container.pop()
        collect()

    def pop(self):
        if isinstance(self[-1], Button):
            self.buttons.pop()
            self.button_functions.pop()
            self.button_index = min(self.button_index, len(self.buttons)-1)
        super().pop()
        collect()

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
    
    tab.append(EZLabel(f'You have {f2str(game.money_upgrades)}\nmoney upgrades'), margin=5)
    tab.append_button(f'Buy one for {f2str(100+game.money_upgrades*150-game.effects[9]+1)}$', do_then_update(check_money(game.buy_money_upgrade)))
    
    tab.append(EZLabel(f"Your energy is at {f2str(game.energy)}%"), margin=5)
    tab.append(EZLabel(f"You lose energy every step\nand it reduces your money gain"))
    tab.append_button(f'Eat a cereal bar for {game.cereal_bar_price - game.effects[3] + 1}$', check_money(game.buy_cereal_bar))

@tab_update
def update_money_tab():
    tab[0].text = f"You gain {f2str(game.money_gained)} $/step"
    tab[1].text = f'You have {f2str(game.money_upgrades)}\nmoney upgrades'
    tab[3].text = f"Your energy is at {f2str(game.energy)}%"

@tab_init('Autobuyers')
def init_autobuyers_tab():
    tab.append(EZLabel(f'You have {game.money_upgrades_autobuyers}\nmoney upgrade autobuyers'))
    tab.append_button(f'Buy one for {f2str(game.money_upgrades_autobuyer_price)}$', do_then_update(check_money(game.buy_money_upgrades_autobuyer)))
    tab.append_button(f'Press to turn {"off" if game.money_upgrades_autobuyers_on else "on"}', do_then_update(game.toggle_money_upgrades_autobuyers))
    
    tab.append(EZLabel(f'You have {game.cereal_bar_autobuyers}\ncereal bar autobuyers'), margin=5)
    tab.append_button(f'Buy one for {f2str(game.cereal_bar_autobuyer_price)}$', do_then_update(check_money(game.buy_cereal_bar_autobuyer)))
    
    if not game.nb_orpheus: return
    tab.append(EZLabel(f'You have {game.apple_autobuyers}\napple autobuyers'), margin=5)
    tab.append_button(f'Buy one for {f2str(game.apple_autobuyer_price)}$', do_then_update(check_money(game.buy_apple_autobuyer)))

@tab_update
def update_autobuyers_tab():
    pass

foot_selected = None

def begin_equip(sock_or_shoe, foot_index):
    def wrapped():
        global foot_selected
        foot_selected = foot_index
        begin_list(sock_or_shoe)
    return wrapped

def equip(index):
    # TODO: not equip already equipped shoe
    def wrapped():
        game.equip(inventory_info[0], index, foot_selected)
        exit_list()
    return wrapped

@tab_init('Feet')
def init_feet_tab():
    if not inventory_info:
        tab.append(EZLabel(f'You have {game.feet} feet.'))
        for i in range(game.feet):
            tab.append_button("Sock: " + (game.socks[game.socks_equipped[i]].name if isinstance(game.socks_equipped[i], int) else "Nothing"),
                begin_equip(game.SOCK, i), margin=5)
            tab.append_button("Shoe: " + (game.shoes[game.shoes_equipped[i]].name if isinstance(game.shoes_equipped[i], int) else "Nothing"),
                begin_equip(game.SHOE, i))
        if game.feet < 9: tab.append_button(f'New foot for {f2str(game.foot_price)}$', do_then_update(check_money(game.buy_foot)), margin=5)
    else:
        tab.append(EZLabel(f'Select a {"sock" if inventory_info[0] == game.SOCK else "shoe"} to equip:'))
        display_list(equip)

@tab_update
def update_feet_tab():
    update_list()

inventory_info = None

@tab_init('Inventory')
def init_inventory_tab():
    if not inventory_info:
        tab.append_button(f"Buy item for {game.item_price}$", buy_item_popup(do_then_update(check_money(game.buy_item))))
        
        tab.append_button(f"See shoe list", lambda: begin_list(game.SHOE), margin=5)
        tab.append_button(f"See sock list", lambda: begin_list(game.SOCK))
        
        if game.bears:
            tab.append(EZLabel(f'Bears: {game.bears}'), margin=5)
    else:
        tab.append(EZLabel('Click on an item to see \nits description'))
        display_list(lambda i: lambda: tab.create_popup((game.shoes if inventory_info[0]==game.SHOE else game.socks)[i].name + ':\n' + (game.shoes if inventory_info[0]==game.SHOE else game.socks)[i].description))

def buy_item_popup(function):
    def wrapped():
        r = function()
        if not r: return False
        if isinstance(r, bool):
            tab.create_popup('You encountered a bear!')
        else:
            tab.create_popup('You bought a '+r.name+'!')
        return True
    return wrapped

def begin_list(sock_or_shoe):
    global tab_locked, inventory_info, refresh_c
    refresh_c = False
    tab_locked = True
    inventory_info = [sock_or_shoe, 0]
    do_then_update(lambda: True)()

def display_list(function):
    tab.append(EZLabel(f'Page {1+inventory_info[1]}/{floor(len(game.shoes if inventory_info[0]==game.SHOE else game.socks)/6)+1}|Press B to exit'))
    for i, item in enumerate((game.shoes if inventory_info[0]==game.SHOE else game.socks)[inventory_info[1]*6:inventory_info[1]*6+6]):
        tab.append_button(item.name, function(i+inventory_info[1]*6))

def update_list():
    global tab_locked, inventory_info
    tab_locked = bool(inventory_info) or tab_locked
    if inventory_info and not tab.popup_open:
        if buttons[LEFT]:
            inventory_info[1] -= 1
        if buttons[RIGHT]:
            inventory_info[1] += 1
        if buttons[LEFT] or buttons[RIGHT]:
            inventory_info[1] %= floor(len(game.shoes if inventory_info[0]==game.SHOE else game.socks)/6)+1
            tab.button_index = 0
            do_then_update(lambda: True)()
        elif buttons[B]:
            exit_list()

def exit_list():
    global tab_locked, inventory_info
    inventory_info = None
    tab_locked = False
    tab.button_index = 0
    do_then_update(lambda: True)()

@tab_update
def update_inventory_tab():
    update_list()

trade_info = None

@tab_init('Trade')
def init_trade_tab():
    if not inventory_info:
        tab.append(EZLabel('Trade items through\nWiFi to level them up!'))
        tab.append(EZLabel('Item you want to trade:'),margin=5)
        tab.append_button('None' if not trade_info else (game.shoes if trade_info[0]==game.SHOE else game.socks)[trade_info[1]].name, select_sock_or_shoe)
        tab.append_button('Host', host_trade, margin=5)
        tab.append_button('Connect', connect_trade)
    else:
        display_list(select_trade)

def select_trade(i):
    def wrapped():
        global trade_info
        trade_info = [inventory_info[0],i]
        exit_list()
    return wrapped

def select_sock_or_shoe():
    global tab_locked, refresh_c
    tab_locked = True
    refresh_c = True
    for i in range(5): tab.pop()
    tab.append_button('Choose a shoe', lambda: begin_list(game.SHOE))
    tab.append_button('Choose a sock', lambda: begin_list(game.SOCK))
    tab.append_button('Close', exit)
    tab.button_index = 0
    while tab_locked and refresh_c:
        update_buttons()
        update_screen()
    
def host_trade():
    global s, tab_locked, buttons, trade_info
    if not trade_info:
        tab.create_popup('No item to trade selected!')
        return
    tab_locked = True
    buttons = [False]*6
    for i in range(5): tab.pop()
    label = EZLabel('Starting...')
    tab.append(label)
    display.refresh()
    
    wifi.radio.start_ap("INCPOD_"+game.name, password="HACKCLUB")
    wifi.radio.set_ipv4_address_ap(ipv4=ip_address('72.65.67.75'), gateway=ip_address(0), netmask=ip_address(0))
    
    s = socketpool.SocketPool(wifi.radio).socket()
    s.bind(('72.65.67.75',4130))
    s.listen(1)
    
    label.text = "Name: "+game.name+"\nWaiting for connection..."
    tab.append_button('Close', do_then_update(exit_host))
    tab.button_index = 0
    display.refresh()
    
    while not len(wifi.radio.stations_ap):
        update_buttons()
        update_screen()
        if not tab_locked:
            return
    
    tab.pop()
    label.text = "Connected! Trading..."
    display.refresh()
    
    try:
        cs, addr = s.accept()
        
        cs.send(game.item_to_bytes((game.shoes if trade_info[0]==game.SHOE else game.socks)[trade_info[1]]))
        
        buf = bytearray(17)
        cs.recv_into(buf)
        new_item = game.bytes_to_item(buf)
        
        cs.close()
        
        game.trade(trade_info[0], trade_info[1], new_item)
        
        trade_info = None
        do_then_update(exit_host)()
        tab.create_popup('You received a '+new_item.name+'!')
    except Exception as e:
        print(e)
        do_then_update(exit_host)()
        tab.create_popup('An error occured!')

def exit_host():
    global s, tab_locked
    s.close()
    s = None
    tab_locked = False
    wifi.radio.stop_ap()
    return True

def select_host(name):
    def wrapped():
        global host_name
        host_name = name
    return wrapped

def refresh():
    global refresh_c
    refresh_c = True

def exit():
    global tab_locked
    tab_locked = False
    do_then_update(lambda: True)()

def connect_trade():
    global s, tab_locked, refresh_c, host_name, trade_info
    if not trade_info:
        tab.create_popup('No item to trade selected!')
        return
    tab_locked = True
    for i in range(5): tab.pop()
    buttons = [False]*6
    refresh_c = True
    host_name = None
    label = EZLabel('Select a host:')
    tab.append(label)
    
    while not host_name:
        if refresh_c:
            refresh_c = False
            for i in range(len(tab)-1): tab.pop()
            
            duplicates = []
            for nw in wifi.radio.start_scanning_networks():
                if nw.ssid.startswith('INCPOD_') and nw.ssid not in duplicates:
                    tab.append_button(nw.ssid[7:], select_host(nw.ssid))
                    duplicates.append(nw.ssid)
                    
            tab.append_button('Refresh', refresh, margin=5)
            tab.append_button('Exit', exit)
            tab.button_index = 0
        update_buttons()
        update_screen()
        if not tab_locked:
            return
    
    for i in range(len(tab)-1): tab.pop()
    label.text = "Connecting..."
    display.refresh()
    
    try:
        wifi.radio.connect(host_name, password="HACKCLUB")
    
        wifi.radio.set_ipv4_address(ipv4=ip_address('67.76.85.66'), gateway=ip_address(0), netmask=ip_address(0))
        
        s = socketpool.SocketPool(wifi.radio).socket()
        s.connect(('72.65.67.75',4130))
        
        label.text = "Connected! Trading..."
        display.refresh()
        
        buf = bytearray(17)
        s.recv_into(buf)
        new_item = game.bytes_to_item(buf)
        
        s.send(game.item_to_bytes((game.shoes if trade_info[0]==game.SHOE else game.socks)[trade_info[1]]))
        
        s.close()
        
        game.trade(trade_info[0], trade_info[1], new_item)
        
        tab_locked = False
        trade_info = None
        do_then_update(lambda: True)()
        tab.create_popup('You received a '+new_item.name+'!')
    except Exception as e:
        print(e)
        do_then_update(lambda: True)()
        tab.create_popup('An error occured!')
    
@tab_update
def update_trade_tab():
    update_list()

@tab_init('Training')
def init_training_tab():
    if not game.training_mode_unlocked:
        tab.append_button('Unlock for 5000$', do_then_update(check_money(game.unlock_training_mode)))
        return
    tab.append(EZLabel('In Training mode energy\nis way more punishing.\nGet as much money as possible\nto make the energy\nlimit higher!'))
    tab.append(EZLabel(f'Current max energy: {f2str(100+game.muscles)}%'), margin=8)
    tab.append_button('Enter training mode', do_then_update(game.toggle_training))

@tab_update
def update_training_tab():
    if game.training_mode:
        x = game.money_to_muscles()-game.muscles
        tab[2].label = f"Stop for +{f2str(x)}%" if x>0 else "Stop for +0%"

@tab_init('Orpheus')
def init_orpheus_tab():
    if not game.nb_orpheus: tab.append(EZLabel('Sacrificing will reset\nyour entire progression\nexcept your items\nand autobuyers.\nIn exchange you summon\nOrpheus who will boost\nyour production!'))
    tab.append_button(f'Sacrifice for {f2str(game.sacrifice_price)}$', do_then_update(check_money(game.sacrifice)))
    
    if not game.nb_orpheus: return
    tab.append(EZLabel(f'Orpheus count: {f2str(game.nb_orpheus)}'))
    
    tab.append(EZLabel(f"Their energy is at {f2str(game.energy_orpheus)}%"), margin=5)
    tab.append_button(f'Give them an apple for {game.apple_price - game.effects[3] + 1}$', game.buy_apple)
    
    bitmap=displayio.OnDiskBitmap("/assets/orpheus.bmp")
    tile_grid=displayio.TileGrid(bitmap, pixel_shader=theme, height=1 ,width=min(game.nb_orpheus,8))
    tab.append(tile_grid)
    

@tab_update
def update_orpheus_tab():
    if game.nb_orpheus:
        tab[3].text = f"Their energy is at {f2str(game.energy_orpheus)}%"

@tab_init('Settings')
def init_settings_tab():
    tab.append(EZLabel())
    tab.append_button('Change theme', change_theme)
    tab.append(EZLabel(), margin=5)
    tab.append_button('Change notation', game.change_notation)
    tab.append_button('Reset save', reset_save_ask, margin=5)

def reset_save_ask():
    global tab_locked
    tab_locked = True
    for i in range(5): tab.pop()
    tab.append(EZLabel('Are you sure?'))
    tab.append_button('No', exit)
    tab.append_button('Yes', reset_save)
    tab.button_index = 0
    while tab_locked:
        update_buttons()
        update_screen()

def reset_save():
    try:
        game.reset_save()
        supervisor.reload()
    except OSError:
        tab.create_popup('Can\'t reset save: you pressed A while booting and launched in USB mode')

@tab_update
def update_settings_tab():
    if tab_locked: return
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
    collect()

def change_theme():
    game.change_theme(len(themes))
    buttons[A] = False
    configure_groups()

def do_then_update(func):
    def wrapped():
        global tab, buttons
        buttons = [False]*6
        i = tab.button_index
        r = func()
        if not r: return False
        tab_container.pop()
        collect()
        tab = Tab()
        tab_container.append(tab)
        tab_init_functions[tab_index]()
        tab.button_index = min(len(tab.buttons)-1, i)
        update_screen()
        return r
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
    
    display.root_group.append(Rectangle(pixel_shader=theme, width=160, height=108, x=0, y=20, color_index=0))

    tab_container = displayio.Group(y=25)
    display.root_group.append(tab_container)
    
    display.root_group.append(Rectangle(pixel_shader=theme, width=160, height=20, x=0, y=0, color_index=1))
    display.root_group.append(Rectangle(pixel_shader=theme, width=160, height=2, x=0, y=20, color_index=2))
    display.root_group.append(Rectangle(pixel_shader=theme, width=2, height=20, x=80, y=0, color_index=2))    

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
    collect()

def save():
    try:
        game.save()
    except OSError:
        tab.create_popup('Can\'t save: you pressed A while booting and launched in USB mode')

# Accelerometer part

accelerometer = ADXL345(I2C(scl=board.GP17, sda=board.GP16))
accelerometer.enable_motion_detection(threshold=10)
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

def update_buttons():
    global buttons, buttons_done
    bval = [not b.value for b in buttons_input]
    buttons = [v and not d for v,d in zip(bval, buttons_done)]
    buttons_done = bval[:] 

while True:
    # Check accelerometer
    if accelerometer.events['motion']:
        if accelerometer.acceleration[0] > 2 and step_done == True:
            step_done = False
            game.step()
            if display: update_screen()
        if accelerometer.acceleration[0] < -2:
            step_done = True

    update_buttons()
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

