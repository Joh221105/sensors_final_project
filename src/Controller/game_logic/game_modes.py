import time
import displayio
from adafruit_display_text import label
import terminalio
import gc

from input_handler import difficulty_select
from sensors import display
from .animations import show_connecting_screen

# 10 levels
LEVELS = [
    {"inputs": 3, "time": 40, "width": 120},
    {"inputs": 3, "time": 35, "width": 100},
    {"inputs": 4, "time": 40, "width": 90},
    {"inputs": 4, "time": 35, "width": 80},
    {"inputs": 5, "time": 40, "width": 75},
    {"inputs": 5, "time": 35, "width": 70},
    {"inputs": 6, "time": 40, "width": 65},
    {"inputs": 6, "time": 35, "width": 60},
    {"inputs": 7, "time": 40, "width": 55},
    {"inputs": 8, "time": 45, "width": 50},
]

target_start = 0
target_end = 0
target_width = 100


def update_pixel_color(pixel, lives):
    """updates neopixel color based on remaining lives"""
    colors = {3: (0, 255, 0), 2: (255, 120, 0), 1: (255, 0, 0), 0: (0, 0, 0)}
    pixel[0] = colors.get(lives, (0, 0, 0))


def randomize_success_zone():
    """create new random success/target zone"""
    import random
    global target_start, target_end, target_width
    target_start = random.randint(0, 359)
    target_end = (target_start + target_width) % 360


def in_success_zone(angle):
    """check if cursor angle is in the success zone"""
    if target_start < target_end:
        return target_start <= angle <= target_end
    return angle >= target_start or angle <= target_end


def run_campaign_mode(pixel):
    """campaign mode - 10 levels"""
    from safe_control import connect_to_safe, lock_safe
    from .game_loop import run_level
    from audio import game_over_sound
    
    gc.collect()
    show_connecting_screen(display, pixel)
    
    safe_connected = False
    try:
        if connect_to_safe():
            lock_safe()
            safe_connected = True
    except Exception as e:
        print(f"Safe error: {e}")
    
    difficulty = difficulty_select(display, pixel)
    lives = {"EASY": 3, "MEDIUM": 2, "HARD": 1}[difficulty]
    time.sleep(0.3)
    update_pixel_color(pixel, lives)
    
    current_level = 0
    score = 0
    
    while True:
        result = run_level(
            pixel, lives, current_level, score, difficulty,
            LEVELS, safe_connected, mode="CAMPAIGN"
        )
        
        if result["status"] in ("RESTART", "EXIT"):
            game_over_sound()
            gc.collect()
            return result["status"]
        
        lives = result["lives"]
        score = result["score"]
        current_level = result["level"]


def run_endless_mode(pixel):
    """endless mode - survive as long as possible"""
    from safe_control import connect_to_safe, lock_safe
    from .game_loop import run_endless_level
    
    gc.collect()
    show_connecting_screen(display, pixel)
    
    safe_connected = False
    try:
        if connect_to_safe():
            lock_safe()
            safe_connected = True
    except Exception as e:
        print(f"Safe error: {e}")
    
    lives = 3
    starting_width = 100
    update_pixel_color(pixel, lives)
    
    # Show intro
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text="ENDLESS MODE", x=20, y=15))
    g.append(label.Label(terminalio.FONT, text="Survive as long", x=12, y=30))
    g.append(label.Label(terminalio.FONT, text="as you can!", x=22, y=42))
    g.append(label.Label(terminalio.FONT, text="+1s per hit", x=25, y=54))
    display.root_group = g
    time.sleep(2.5)
    
    result = run_endless_level(pixel, lives, starting_width, safe_connected)
    gc.collect()
    return result["status"]
