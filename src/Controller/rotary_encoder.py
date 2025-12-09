import time
import digitalio

class RotaryEncoder:

    _TRANSITION_TABLE = {
        0b0001: +1,  # CW: 00 -> 01
        0b0111: +1,  # CW: 01 -> 11
        0b1110: +1,  # CW: 11 -> 10
        0b1000: +1,  # CW: 10 -> 00
        
        0b0010: -1,  # CCW: 00 -> 10
        0b1011: -1,  # CCW: 10 -> 11
        0b1101: -1,  # CCW: 11 -> 01
        0b0100: -1,  # CCW: 01 -> 00
    }
    
    def __init__(self, pin_a, pin_b, *, pull=digitalio.Pull.UP, pulses_per_detent=4):
        self._a = digitalio.DigitalInOut(pin_a)
        self._a.switch_to_input(pull=pull)
        self._b = digitalio.DigitalInOut(pin_b)
        self._b.switch_to_input(pull=pull)
        
        self._pulses_per_detent = pulses_per_detent
        
        # state tracking
        self._last_state = self._read_state()
        self._raw_pos = 0
        self._detent_pos = 0
        self._delta = 0
        
        # smoothing- accumulate small movements
        self._accumulated = 0
        
        # debouncing
        self._last_update_time = time.monotonic()
        self._min_interval = 0.001  # 1ms minimum between updates
    
    def _read_state(self):
        return (self._a.value << 1) | self._b.value
    
    def update(self):
        """
        Update encoder state. Returns True if position changed.
        Call this frequently in your main loop.
        """
        now = time.monotonic()
        
        # debounce: ignore updates that are too fast
        if (now - self._last_update_time) < self._min_interval:
            return False
        
        curr_state = self._read_state()
        
        # no change
        if curr_state == self._last_state:
            return False
        
        # build transition key: (prev_state << 2) | curr_state
        transition = (self._last_state << 2) | curr_state
        
        # look up movement direction
        move = self._TRANSITION_TABLE.get(transition, 0)
        
        # update state regardless of valid transition
        self._last_state = curr_state
        self._last_update_time = now
        
        # valid transition detected
        if move != 0:
            self._raw_pos += move
            
            # check if we've completed a detent
            new_detent = self._raw_pos // self._pulses_per_detent
            
            if new_detent != self._detent_pos:
                # detent position changed
                detent_delta = new_detent - self._detent_pos
                self._delta += detent_delta
                self._detent_pos = new_detent
                return True
        
        return False
    
    def get_delta(self):
        """
        get accumulated movement since last call.
        returns +N for clockwise, -N for counter-clockwise.
        """
        delta = self._delta
        self._delta = 0
        return delta
    
    def get_position(self):
        """get absolute detent position"""
        return self._detent_pos
    
    def reset(self):
        """reset position to zero"""
        self._raw_pos = 0
        self._detent_pos = 0
        self._delta = 0
