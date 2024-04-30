from adafruit_bitmap_font import bitmap_font

WIDTH = 160
HEIGHT = 128
BAR_HEIGHT = 20
BG_COLOR = 0x000000
BAR_COLOR = 0x0f0f0f
TEXT_COLOR = 0xffffff
raise NotImplementedError('Configure a font first!')
FONT = bitmap_font.load_font("/fonts/font.bdf")

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
A = 4
B = 5
