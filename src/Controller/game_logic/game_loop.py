import time
import random
import displayio
from adafruit_display_text import label
import terminalio
import gc

from ui_display import draw_circle_and_arc, build_cursor, update_cursor_rotation
from input_handler import encoder, button, lose_life, enter_initials, game_over_screen, victory_screen
from sensors import display, run_stay_still_event
from audio import success_sound, fail_sound, level_up_sound, game_over_sound, victory_sound
from high_scores import is_high_score, add_high_score, get_rank

# import from same package
from .animations import show_stun_animation, show_level_transition
from . import game_modes


def run_level(pixel, lives, current_level, score, difficulty, LEVELS, safe_connected, mode="CAMPAIGN"):
    """Run a single campaign level"""
    from safe_control import unlock_safe
    
    level = LEVELS[current_level]
    inputs_left = level["inputs"]
    time_left = level["time"]
    
    # set target width
    game_modes.target_width = level["width"]
    game_modes.randomize_success_zone()
    
    # event tracking
    events_used = 0
    MAX_EVENTS = 2
    event_counter = 0
    
    # button debouncing
    last_button_time = 0
    DEBOUNCE_TIME = 0.15
    
    # create display groups
    main_group = displayio.Group()
    bg = displayio.Group()
    fg = displayio.Group()
    main_group.append(bg)
    main_group.append(fg)
    display.root_group = main_group
    
    # draw game elements
    draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
    
    time_label = label.Label(terminalio.FONT, text=f"TIME: {time_left}", x=0, y=10)
    lvl_label = label.Label(terminalio.FONT, text=f"LVL: {current_level+1}", x=80, y=10)
    inputs_label = label.Label(terminalio.FONT, text=str(inputs_left), scale=2, x=60, y=38)
    
    fg.append(time_label)
    fg.append(lvl_label)
    fg.append(inputs_label)
    
    cursor = build_cursor(fg)
    
    # cursor physics
    cursor_angle = 0
    cursor_velocity = 0
    last_tick = time.monotonic()
    
    status = "CONTINUE"
    
    # main game loop
    while True:
        # stay still challenge
        event_counter += 1
        if event_counter >= 200:
            event_counter = 0
            if events_used < MAX_EVENTS and random.random() < 0.01:
                events_used += 1
                result = run_stay_still_event(main_group)
                
                if result == "FAIL":
                    fail_sound()
                    status, lives = lose_life(display, pixel, lives)
                    game_modes.update_pixel_color(pixel, lives)
                    
                    if status in ("RESTART", "EXIT"):
                        return {"status": status, "lives": lives, "score": score, "level": current_level}
                    break
                
                last_tick = time.monotonic()
        
        # timer countdown
        now = time.monotonic()
        if now - last_tick >= 1:
            last_tick = now
            time_left -= 1
            time_label.text = f"TIME: {time_left}"
            
            if time_left <= 0:
                fail_sound()
                status, lives = lose_life(display, pixel, lives)
                game_modes.update_pixel_color(pixel, lives)
                
                if status in ("RESTART", "EXIT"):
                    return {"status": status, "lives": lives, "score": score, "level": current_level}
                break
        
        # rotary encoder input
        if encoder.update():
            d = encoder.get_delta()
        else:
            d = 0
        
        ACCEL = 2.0
        FRICTION = 0.985
        MAX_SPEED = 22
        
        cursor_velocity += d * ACCEL
        cursor_velocity = max(min(cursor_velocity, MAX_SPEED), -MAX_SPEED)
        cursor_velocity *= FRICTION
        cursor_angle = (cursor_angle + cursor_velocity) % 360
        
        # button press detection
        now_time = time.monotonic()
        button_pressed = not button.value
        
        if button_pressed and (now_time - last_button_time) > DEBOUNCE_TIME:
            last_button_time = now_time
            
            if game_modes.in_success_zone(cursor_angle):
                success_sound()
                inputs_left -= 1
                inputs_label.text = str(inputs_left)
                
                game_modes.randomize_success_zone()
                draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
                
                if inputs_left <= 0:
                    # level complete
                    score += time_left
                    current_level += 1
                    
                    if current_level >= len(LEVELS):
                        # win game!
                        victory_sound()
                        
                        # unlock safe
                        if safe_connected:
                            try:
                                unlock_safe()
                            except Exception as e:
                                print(f"Unlock error: {e}")
                        
                        # check high score
                        if is_high_score(score, mode="CAMPAIGN"):
                            rank = get_rank(score, mode="CAMPAIGN")
                            
                            g = displayio.Group()
                            g.append(label.Label(terminalio.FONT, text="NEW HIGH", x=25, y=15, scale=2))
                            g.append(label.Label(terminalio.FONT, text="SCORE!", x=30, y=35, scale=2))
                            g.append(label.Label(terminalio.FONT, text=f"Rank #{rank}!", x=30, y=55))
                            display.root_group = g
                            pixel[0] = (255, 215, 0)
                            time.sleep(2)
                            
                            initials = enter_initials(display, pixel)
                            add_high_score(initials, score, difficulty, mode="CAMPAIGN")
                        
                        # victory screen
                        g = displayio.Group()
                        g.append(label.Label(terminalio.FONT, text="MISSION", x=30, y=8, scale=2))
                        g.append(label.Label(terminalio.FONT, text="COMPLETE!", x=20, y=28, scale=2))
                        g.append(label.Label(terminalio.FONT, text="SAFE UNLOCKED!", x=10, y=48))
                        g.append(label.Label(terminalio.FONT, text=f"Score: {score}", x=30, y=58))
                        display.root_group = g
                        pixel[0] = (0, 255, 0)
                        time.sleep(3)
                        
                        play_again = victory_screen(display, score)
                        gc.collect()
                        
                        status = "RESTART" if play_again else "EXIT"
                        return {"status": status, "lives": lives, "score": score, "level": current_level}
                    
                    show_level_transition(display, current_level, time_left, score)
                    gc.collect()
                    break
            
            else:
                # miss - stun animation
                fail_sound()
                time_left = show_stun_animation(display, pixel, time_left, time_label, main_group)
                
                if time_left <= 0:
                    fail_sound()
                    status, lives = lose_life(display, pixel, lives)
                    game_modes.update_pixel_color(pixel, lives)
                    
                    if status in ("RESTART", "EXIT"):
                        game_over_sound()
                        gc.collect()
                        return {"status": status, "lives": lives, "score": score, "level": current_level}
                    break
                
                # restore display
                display.root_group = main_group
                game_modes.randomize_success_zone()
                draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
                last_tick = time.monotonic()
        
        # update cursor
        update_cursor_rotation(cursor, cursor_angle)
        display.refresh(minimum_frames_per_second=0)
    
    # level end
    if status in ("RESTART", "EXIT"):
        game_over_sound()
        gc.collect()
        return {"status": status, "lives": lives, "score": score, "level": current_level}
    
    return {"status": "CONTINUE", "lives": lives, "score": score, "level": current_level}


def run_endless_level(pixel, lives, starting_width, safe_connected):
    """endless mode"""
    from safe_control import unlock_safe
    
    total_hits = 0
    time_left = 30
    game_modes.target_width = starting_width
    game_modes.randomize_success_zone()
    
    # event tracking
    events_used = 0
    MAX_EVENTS = 2
    event_counter = 0
    
    last_button_time = 0
    DEBOUNCE_TIME = 0.15
    
    # create display
    main_group = displayio.Group()
    bg = displayio.Group()
    fg = displayio.Group()
    main_group.append(bg)
    main_group.append(fg)
    display.root_group = main_group
    
    draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
    
    time_label = label.Label(terminalio.FONT, text=f"TIME: {time_left}", x=0, y=10)
    hits_label = label.Label(terminalio.FONT, text=f"HITS: {total_hits}", x=70, y=10)
    
    fg.append(time_label)
    fg.append(hits_label)
    
    cursor = build_cursor(fg)
    
    # cursor physics
    cursor_angle = 0
    cursor_velocity = 0
    last_tick = time.monotonic()
    game_start_time = time.monotonic()
    
    status = "CONTINUE"
    
    while True:
        # Random events
        event_counter += 1
        if event_counter >= 500:
            event_counter = 0
            if events_used < MAX_EVENTS and random.random() < 0.005:
                events_used += 1
                result = run_stay_still_event(main_group)
                
                if result == "FAIL":
                    fail_sound()
                    status, lives = lose_life(display, pixel, lives)
                    game_modes.update_pixel_color(pixel, lives)
                    
                    if status in ("RESTART", "EXIT"):
                        break
                    
                    display.root_group = main_group
                last_tick = time.monotonic()
        
        # timer
        now = time.monotonic()
        if now - last_tick >= 1:
            last_tick = now
            time_left -= 1
            time_label.text = f"TIME: {time_left}"
            
            if time_left <= 0:
                fail_sound()
                break
        
        # encoder input
        if encoder.update():
            d = encoder.get_delta()
        else:
            d = 0
        
        ACCEL = 2.0
        FRICTION = 0.985
        MAX_SPEED = 22
        
        cursor_velocity += d * ACCEL
        cursor_velocity = max(min(cursor_velocity, MAX_SPEED), -MAX_SPEED)
        cursor_velocity *= FRICTION
        cursor_angle = (cursor_angle + cursor_velocity) % 360
        
        # button press
        now_time = time.monotonic()
        button_pressed = not button.value
        
        if button_pressed and (now_time - last_button_time) > DEBOUNCE_TIME:
            last_button_time = now_time
            
            if game_modes.in_success_zone(cursor_angle):
                # SUCCESS
                success_sound()
                total_hits += 1
                hits_label.text = f"HITS: {total_hits}"
                time_left += 1
                time_label.text = f"TIME: {time_left}"
                
                # shrink target
                if total_hits % 3 == 0:
                    game_modes.target_width = max(25, game_modes.target_width - 2)
                    level_up_sound()
                
                game_modes.randomize_success_zone()
                draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
            
            else:
                # MISS
                fail_sound()
                time_left = show_stun_animation(display, pixel, time_left, time_label, main_group)
                
                if time_left <= 0:
                    break
                
                display.root_group = main_group
                game_modes.randomize_success_zone()
                draw_circle_and_arc(bg, game_modes.target_start, game_modes.target_end)
                last_tick = time.monotonic()
        
        # update cursor
        update_cursor_rotation(cursor, cursor_angle)
        display.refresh(minimum_frames_per_second=0)
    
    # GAME OVER
    game_over_sound()
    final_time = int(time.monotonic() - game_start_time)
    
    if safe_connected and final_time >= 120:
        try:
            unlock_safe()
        except:
            pass
    
    # show stats
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text="GAME OVER!", x=22, y=5))
    g.append(label.Label(terminalio.FONT, text=f"Hits: {total_hits}", x=5, y=25))
    g.append(label.Label(terminalio.FONT, text=f"Time: {final_time}s", x=5, y=40))
    g.append(label.Label(terminalio.FONT, text=f"Width: {game_modes.target_width}", x=5, y=55))
    display.root_group = g
    pixel[0] = (255, 0, 0)
    time.sleep(3)
    
    # check high score
    if is_high_score(total_hits, mode="ENDLESS"):
        rank = get_rank(total_hits, mode="ENDLESS")
        
        g = displayio.Group()
        g.append(label.Label(terminalio.FONT, text="NEW HIGH", x=25, y=15, scale=2))
        g.append(label.Label(terminalio.FONT, text="SCORE!", x=30, y=35, scale=2))
        g.append(label.Label(terminalio.FONT, text=f"Rank #{rank}!", x=30, y=55))
        display.root_group = g
        pixel[0] = (255, 215, 0)
        time.sleep(2)
        
        initials = enter_initials(display, pixel)
        add_high_score(initials, total_hits, "ENDLESS", mode="ENDLESS")
    
    restart = game_over_screen(display)
    gc.collect()
    
    status = "RESTART" if restart else "EXIT"
    return {"status": status}
