import time
import displayio
from adafruit_display_text import label
import terminalio
import math
from ui_display import make_pixel


def show_connecting_screen(display, pixel):
    """display 'Looking for Vault' screen"""
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text="LOOKING FOR", x=20, y=25))
    g.append(label.Label(terminalio.FONT, text="VAULT...", x=35, y=40))
    display.root_group = g
    pixel[0] = (255, 255, 0)
    time.sleep(0.5)


def show_splash_screen(display, pixel):
    """show intro unlocking animation"""
    from audio import intro_music
    
    splash_group = displayio.Group()
    display.root_group = splash_group
    
    start_time = time.monotonic()
    duration = 4.0
    
    cx, cy = 64, 32
    vault_radius = 20
    combo_angles = [0, 120, 240]
    tumbler_unlocked = [False, False, False]
    angle = 0
    rotation_speed = 20
    
    while time.monotonic() - start_time < duration:
        elapsed = time.monotonic() - start_time
        progress = elapsed / duration
        
        while len(splash_group) > 0:
            splash_group.pop()
        
        # draw vault circle
        for a in range(0, 360, 10):
            rad = math.radians(a)
            x = int(cx + vault_radius * math.cos(rad))
            y = int(cy + vault_radius * math.sin(rad))
            splash_group.append(make_pixel(x, y))
        
        # draw rotating dial
        dial_angle = angle % 360
        dial_radius = 15
        
        for r in range(0, dial_radius, 2):
            rad = math.radians(dial_angle)
            x = int(cx + r * math.cos(rad))
            y = int(cy + r * math.sin(rad))
            splash_group.append(make_pixel(x, y))
        
        # draw tumblers
        for i, tumbler_angle in enumerate(combo_angles):
            rad = math.radians(tumbler_angle)
            tumbler_x = int(cx + (vault_radius + 3) * math.cos(rad))
            tumbler_y = int(cy + (vault_radius + 3) * math.sin(rad))
            
            if progress > (i + 1) * 0.25:
                tumbler_unlocked[i] = True
            
            if tumbler_unlocked[i]:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        splash_group.append(make_pixel(tumbler_x + dx, tumbler_y + dy))
            else:
                splash_group.append(make_pixel(tumbler_x, tumbler_y))
        
        angle = (angle + rotation_speed) % 360
        
        # status text
        if progress < 0.9:
            status_text = label.Label(terminalio.FONT, text="UNLOCKING...", x=22, y=55)
        else:
            status_text = label.Label(terminalio.FONT, text="ACCESS GRANTED", x=15, y=55)
        splash_group.append(status_text)
        
        # pulse pixel
        if progress < 0.9:
            pixel[0] = (255, int(progress * 255), 0)
        else:
            pixel[0] = (0, 255, 0)
        
        try:
            display.refresh(minimum_frames_per_second=0)
        except:
            pass
        
        time.sleep(0.05)
    
    intro_music()
    
    while len(splash_group) > 0:
        splash_group.pop()


def create_star(x, y):
    """Create a star sprite for stunned screen"""
    pattern = ["00100", "01110", "11111", "01110", "00100"]
    h = len(pattern)
    w = len(pattern[0])
    bmp = displayio.Bitmap(w, h, 2)
    pal = displayio.Palette(2)
    pal[0] = 0x000000
    pal[1] = 0xFFFF00
    pal.make_transparent(0)
    
    for py in range(h):
        for px in range(w):
            if pattern[py][px] == "1":
                bmp[px, py] = 1
    
    sprite = displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)
    return sprite


def show_level_transition(display, level_number, remaining_time, new_score):
    """display level complete screen"""
    from audio import level_up_sound
    
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text=f"LEVEL {level_number} COMPLETE!", x=5, y=15))
    g.append(label.Label(terminalio.FONT, text=f"Time Bonus: {remaining_time}", x=5, y=32))
    g.append(label.Label(terminalio.FONT, text=f"Score: {new_score}", x=5, y=48))
    display.root_group = g
    level_up_sound()
    time.sleep(1.5)


def show_stun_animation(display, pixel, time_left, time_label, main_group):
    """show stunned animation when player misses"""
    original_color = pixel[0]
    
    stun_duration = 2.5
    stun_start = time.monotonic()
    flash_interval = 0.25
    last_flash = stun_start
    flash_state = False
    stun_last_tick = stun_start
    
    # animation setup
    num_stars = 6
    stars = []
    radius = 20
    cx, cy = 64, 32
    angle_offset = 0
    
    dazed_group = displayio.Group()
    
    for i in range(num_stars):
        star = create_star(0, 0)
        stars.append(star)
        dazed_group.append(star)
    
    stun_text = label.Label(terminalio.FONT, text="STUNNED!", x=30, y=55, scale=1)
    dazed_group.append(stun_text)
    
    anim_time_label = label.Label(terminalio.FONT, text=f"TIME: {time_left}", x=0, y=10)
    dazed_group.append(anim_time_label)
    
    display.root_group = dazed_group
    
    # animation loop
    while time.monotonic() - stun_start < stun_duration:
        stun_now = time.monotonic()
        
        # Count down time
        if stun_now - stun_last_tick >= 1:
            stun_last_tick = stun_now
            time_left -= 1
            anim_time_label.text = f"TIME: {time_left}"
            time_label.text = f"TIME: {time_left}"
            
            if time_left <= 0:
                display.root_group = main_group
                pixel[0] = original_color
                return time_left
        
        # animate stars
        for i, star in enumerate(stars):
            angle = (angle_offset + (i * 360 / num_stars)) % 360
            rad = math.radians(angle)
            x = int(cx + radius * math.cos(rad)) - 2
            y = int(cy + radius * math.sin(rad)) - 2
            star.x = x
            star.y = y
        
        angle_offset = (angle_offset + 10) % 360
        
        # flash pixel
        if stun_now - last_flash >= flash_interval:
            last_flash = stun_now
            flash_state = not flash_state
            pixel[0] = (255, 0, 0) if flash_state else (0, 0, 0)
        
        try:
            display.refresh(minimum_frames_per_second=0)
        except:
            pass
        
        time.sleep(0.05)
    
    pixel[0] = original_color
    return time_left
