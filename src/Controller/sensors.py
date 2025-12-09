import displayio
import board
import busio
import time
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306
import adafruit_adxl34x
import terminalio

displayio.release_displays()

i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

accel = adafruit_adxl34x.ADXL345(i2c)


def run_stay_still_event(main_group):
    """random event: player must stay still"""
    # warning screen
    warn = displayio.Group()
    warn.append(label.Label(terminalio.FONT, text="EVENT!", x=40, y=18))
    warn.append(label.Label(terminalio.FONT, text="STAY STILL IN 1s", x=5, y=38))
    display.root_group = warn
    time.sleep(1)
    
    still = displayio.Group()
    still.append(label.Label(terminalio.FONT, text="STAY STILL!", x=25, y=25))
    display.root_group = still
    
    # baseline accelerometer reading
    readings = []
    for _ in range(5):
        readings.append(accel.acceleration)
        time.sleep(0.02)
    
    # average the baseline
    avg_x = sum(r[0] for r in readings) / len(readings)
    avg_y = sum(r[1] for r in readings) / len(readings)
    avg_z = sum(r[2] for r in readings) / len(readings)
    
    prev_x, prev_y, prev_z = avg_x, avg_y, avg_z
    
    # increased threshold, more forgiving
    THRESH = 1.0 
    FAILED = False
    start = time.monotonic()
    
    # sample less frequently to be more forgiving
    while time.monotonic() - start < 3:
        x, y, z = accel.acceleration
        
        # check if movement exceeds threshold
        if abs(x - prev_x) > THRESH or abs(y - prev_y) > THRESH or abs(z - prev_z) > THRESH:
            FAILED = True
            break
        
        prev_x, prev_y, prev_z = x, y, z
        time.sleep(0.1)  # changed from 0.05 to 0.1 (sample half as often)
    
    display.root_group = main_group
    return "FAIL" if FAILED else "SUCCESS"
