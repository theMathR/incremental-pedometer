import storage
import board, digitalio

button = digitalio.DigitalInOut(board.GP14)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

storage.remount('/', readonly=not button.value)
