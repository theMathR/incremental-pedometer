import board, ui, game
from analogio import AnalogIn
from adafruit_adxl34x import ADXL345

accelerometer = ADXL345(board.I2C()) # TODO: Set pinout?
accelerometer.enable_motion_detection() # TODO: Set threshold

bpin = AnalogIn(board.A1) # TODO: Set pinout
buttons = [False for i in range(6)]
BUTTON_THRESHOLDS = [0,0,0,0,0,0,0,0] # TODO: Set

# TODO: Button inputs

screen_activated = False

while True:
    # Check accelerometer
    if accelerometer.events['motion']:
        game.step()
        if screen_activated:
            ui.update()
    
    # Check buttons
    v = bpin.value
    pressed = False
    for i in range(6):
        if pressed:
            buttons[i] = False
        else:
            buttons[i] = pressed = v >= BUTTON_THRESHOLDS[i]
            
    if pressed:
        if not screen_activated:
            ui.activate_screen()
        ui.update()
