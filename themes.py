from displayio import Palette
from random import randint

themes = []
theme_names = []

def create_theme(name, bg, bar, text, button):
    theme = Palette(4)
    theme[0] = bg
    theme[1] = bar
    theme[2] = text
    theme[3] = button
    theme_names.append(name)
    themes.append(theme)

create_theme("Default", 0xffffff, 0xffffff, 0x0, 0x0)
create_theme("Dark", 0x0, 0x0, 0xffffff, 0xffffff)
create_theme("Gameboy", 0x0, 0x001f00, 0x00ff00, 0x009f00)
create_theme("Random colors", randint(0,0xffffff), randint(0,0xffffff), randint(0,0xffffff), randint(0,0xffffff))
