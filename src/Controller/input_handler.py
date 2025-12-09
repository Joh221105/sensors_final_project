import time
import displayio
import terminalio
from adafruit_display_text import label
import digitalio
import board
from rotary_encoder import RotaryEncoder

# initialize hardware
encoder = RotaryEncoder(board.D0, board.D1, pulses_per_detent=4)

button = digitalio.DigitalInOut(board.D7)
button.switch_to_input(pull=digitalio.Pull.UP)

pixel_colors = {
    3: (0, 255, 0),
    2: (255, 165, 0),
    1: (255, 0, 0),
    0: (0, 0, 0)
}


def enter_initials(display, pixel):
    """enter 2-letter initials using rotary encoder"""
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    initials = ["A", "A"]  # two letter initials
    current_position = 0  # which letter we're editing (0 or 1)
    current_index = 0  # index in letters list
    
    def draw():
        g = displayio.Group()
        
        g.append(label.Label(terminalio.FONT, text="ENTER INITIALS", x=15, y=10))
        
        # show both letters with cursor
        letter1_text = f"{'>' if current_position == 0 else ' '}{initials[0]}{'<' if current_position == 0 else ' '}"
        letter2_text = f"{'>' if current_position == 1 else ' '}{initials[1]}{'<' if current_position == 1 else ' '}"
        
        g.append(label.Label(terminalio.FONT, text=letter1_text, x=40, y=30, scale=2))
        g.append(label.Label(terminalio.FONT, text=letter2_text, x=70, y=30, scale=2))
        
        g.append(label.Label(terminalio.FONT, text="Press to confirm", x=8, y=55))
        
        display.root_group = g
    
    # find index of current letter
    current_index = letters.index(initials[current_position])
    
    draw()
    pixel[0] = (255, 255, 0)  # Yellow
    
    confirmed = False
    
    while not confirmed:
        # rotate to change letter
        if encoder.update():
            d = encoder.get_delta()
            if d:
                current_index = (current_index + d) % len(letters)
                initials[current_position] = letters[current_index]
                draw()
        
        # button to confirm current letter and move to next
        if not button.value:
            time.sleep(0.2)
            
            if current_position == 0:
                # move to second letter
                current_position = 1
                current_index = letters.index(initials[current_position])
                draw()
                
                # wait for button release
                while not button.value:
                    time.sleep(0.1)
            else:
                # both letters confirmed
                confirmed = True
    
    return "".join(initials)


def show_scoreboard(display, pixel):
    """display the high score leaderboard with mode switching"""
    from high_scores import load_high_scores, MODES
    
    current_mode_index = 0
    
    def draw():
        mode = MODES[current_mode_index]
        scores = load_high_scores(mode)
        
        g = displayio.Group()
        
        # title with current mode
        g.append(label.Label(terminalio.FONT, text=f"{mode} SCORES", x=15, y=5))
        g.append(label.Label(terminalio.FONT, text="=" * 16, x=0, y=13))
        
        if not scores:
            g.append(label.Label(terminalio.FONT, text="No scores yet!", x=15, y=32))
        else:
            # display top 3 scores
            y_pos = 23
            for i, entry in enumerate(scores):
                rank_symbol = ["1ST", "2ND", "3RD"][i]
                
                # format: "1ST AA 250 MED"
                score_text = f"{rank_symbol} {entry['initials']} {entry['score']}"
                diff_text = entry['difficulty'][:3].upper()
                
                g.append(label.Label(terminalio.FONT, text=score_text, x=5, y=y_pos))
                g.append(label.Label(terminalio.FONT, text=diff_text, x=95, y=y_pos))
                
                y_pos += 12
        
        # instructions
        g.append(label.Label(terminalio.FONT, text="Rotate: Switch", x=10, y=52))
        g.append(label.Label(terminalio.FONT, text="Press: Return", x=12, y=60))
        
        display.root_group = g
    
    draw()
    pixel[0] = (255, 215, 0)  # Gold
    
    # input loop
    while True:
        # rotary encoder to switch modes
        if encoder.update():
            d = encoder.get_delta()
            if d:
                current_mode_index = (current_mode_index + d) % len(MODES)
                draw()
        
        # button to return
        if not button.value:
            time.sleep(0.2)
            return


def main_menu(display, pixel):
    """main menu with Play, Endless, and Scoreboard options"""
    options = ["PLAY", "ENDLESS", "SCOREBOARD"]
    index = 0
    
    def draw():
        g = displayio.Group()
        
        # title
        g.append(label.Label(terminalio.FONT, text="MAIN MENU", x=25, y=15))
        
        # menu options
        for i, opt in enumerate(options):
            prefix = "> " if i == index else "  "
            g.append(label.Label(terminalio.FONT, text=prefix + opt, x=22, y=32 + i * 12))
        
        display.root_group = g
    
    draw()
    pixel[0] = (0, 255, 255)  # Cyan for menu
    
    while True:
        if encoder.update():
            d = encoder.get_delta()
            if d:
                index = (index + (1 if d > 0 else -1)) % 3
                draw()
        
        if not button.value:
            time.sleep(0.2)
            return options[index]


def difficulty_select(display, pixel):
    """difficulty selection menu"""
    options = ["EASY", "MEDIUM", "HARD"]
    index = 0
    colors = {"EASY": (0, 255, 0), "MEDIUM": (255, 165, 0), "HARD": (255, 0, 0)}
    
    def draw():
        g = displayio.Group()
        g.append(label.Label(terminalio.FONT, text="SELECT DIFFICULTY", x=5, y=10))
        for i, opt in enumerate(options):
            prefix = "> " if i == index else "  "
            g.append(label.Label(terminalio.FONT, text=prefix + opt, x=10, y=30 + i * 12))
        display.root_group = g
    
    draw()
    pixel[0] = colors[options[index]]
    
    while True:
        if encoder.update():
            d = encoder.get_delta()
            if d:
                index = (index + (1 if d > 0 else -1)) % 3
                pixel[0] = colors[options[index]]
                draw()
        
        if not button.value:
            time.sleep(0.2)
            return options[index]


def game_over_screen(display):
    """gmme over menu"""
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text="GAME OVER", x=20, y=20))
    g.append(label.Label(terminalio.FONT, text="PLAY AGAIN?", x=20, y=40))
    g.append(label.Label(terminalio.FONT, text="Press Button", x=15, y=52))
    display.root_group = g
    
    while True:
        if not button.value:
            time.sleep(0.2)
            return True 


def victory_screen(display, score):
    """victory screen with score"""
    g = displayio.Group()
    
    g.append(label.Label(
        terminalio.FONT,
        text="VICTORY!",
        x=28, y=12
    ))
    
    g.append(label.Label(
        terminalio.FONT,
        text=f"Score: {score}",
        x=28, y=28
    ))
    
    g.append(label.Label(
        terminalio.FONT,
        text="PLAY AGAIN?",
        x=20, y=45
    ))
    
    g.append(label.Label(
        terminalio.FONT,
        text="Press Button",
        x=15, y=57
    ))
    
    display.root_group = g
    
    while True:
        if not button.value:
            time.sleep(0.2)
            return True 


def lose_life(display, pixel, lives):
    """handle losing a life"""
    lives -= 1
    pixel[0] = pixel_colors[lives]
    
    if lives <= 0:
        restart = game_over_screen(display)
        return ("RESTART" if restart else "EXIT"), lives
    
    g = displayio.Group()
    g.append(label.Label(terminalio.FONT, text="-1 LIFE", x=40, y=22))
    g.append(label.Label(terminalio.FONT, text=f"Lives left: {lives}", x=25, y=40))
    display.root_group = g
    time.sleep(1.3)
    
    return "CONTINUE", lives
