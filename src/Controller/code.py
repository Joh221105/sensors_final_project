import board
import neopixel
import time
import gc
import displayio
import terminalio
from adafruit_display_text import label

from game import run_game, show_splash_screen, run_endless_mode
from input_handler import main_menu, show_scoreboard
from sensors import display

pixel = neopixel.NeoPixel(board.D6, 1)
pixel.brightness = 0.1

# show splash screen once at startup
show_splash_screen(display, pixel)

# main loop
while True:
    try:
        gc.collect()
        
        # show main menu
        choice = main_menu(display, pixel)
        
        if choice == "PLAY":
            result = run_game(pixel)
            
        elif choice == "ENDLESS":
            result = run_endless_mode(pixel)
            
        elif choice == "SCOREBOARD":
            show_scoreboard(display, pixel)
            
        gc.collect()
        
    except Exception as e:
        print("Error:", e)
        pixel[0] = (255, 0, 255)  # purple for error
        time.sleep(3)
        gc.collect()
