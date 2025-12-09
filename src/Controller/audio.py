import time
import board
import pwmio

BUZZER_PIN = board.D3
VOLUME = 5000

buzzer = pwmio.PWMOut(BUZZER_PIN, frequency=1000, duty_cycle=0, variable_frequency=True)


def tone(freq, duration=0.1):
    buzzer.frequency = freq
    buzzer.duty_cycle = VOLUME
    time.sleep(duration)
    buzzer.duty_cycle = 0


def success_sound():
    """correct timing"""
    tone(523, 0.05)
    tone(659, 0.08)


def fail_sound():
    """lost a life"""
    tone(400, 0.1)
    tone(300, 0.1)
    tone(200, 0.15)


def wrong_sound():
    """wrong timing"""
    tone(250, 0.2)


def victory_sound():
    """win the game"""
    tone(392, 0.08)
    tone(494, 0.08)
    tone(523, 0.08)
    tone(659, 0.15)


def game_over_sound():
    """game over"""
    tone(494, 0.1)
    tone(440, 0.1)
    tone(392, 0.1)
    tone(330, 0.2)


def level_up_sound():
    """completed a level"""
    tone(440, 0.06)
    tone(494, 0.06)
    tone(587, 0.1)
    
    
def intro_music():
    """play intro music"""
    tone(784, 0.15)   # G5
    tone(784, 0.08)   # G5
    tone(880, 0.15)   # A5
    tone(784, 0.15)   # G5
    
    tone(784, 0.15)   # G5
    tone(784, 0.08)   # G5
    tone(988, 0.15)   # B5
    tone(784, 0.15)   # G5
    
    tone(784, 0.15)   # G5
    tone(784, 0.08)   # G5
    tone(880, 0.15)   # A5
    tone(784, 0.15)   # G5
    
    tone(698, 0.15)   # F5
    tone(698, 0.08)   # F5
    tone(659, 0.15)   # E5
    tone(587, 0.25)   # D5
