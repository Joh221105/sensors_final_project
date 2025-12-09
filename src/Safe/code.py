"""
VAULT SAFE - Receiver Module
"""

import time
import board
import pwmio
from adafruit_motor import servo
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# setup servo
print("Setting up servo on D9...")
pwm = pwmio.PWMOut(board.D0, frequency=50)
lock_servo = servo.Servo(pwm, min_pulse=500, max_pulse=2500)

# setup BLE
print("Setting up BLE...")
ble = BLERadio()
ble.name = "VaultSafe"

uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
advertisement.complete_name = "VaultSafe"

# initial state - locked
print("Moving servo to LOCKED position (0°)...")
lock_servo.angle = 0
time.sleep(1)
print("✓ Safe is LOCKED")

print("\n" + "=" * 40)
print("Advertising as 'VaultSafe'")
print("Waiting for game controller...")
print("=" * 40 + "\n")

ble.start_advertising(advertisement)

# main loop
connection_count = 0

while True:
    # wait for connection
    while not ble.connected:
        time.sleep(0.5)
    
    # connected!
    connection_count += 1
    print(f"\n>>> CONNECTED (Connection #{connection_count}) <<<\n")
    
    # handle commands while connected
    while ble.connected:
        if uart.in_waiting:
            try:
                command = uart.read(uart.in_waiting).decode('utf-8').strip()
                print(f"[CMD] {command}")
                
                if command == "UNLOCK":
                    print("  → UNLOCKING SAFE...")
                    lock_servo.angle = 90
                    time.sleep(0.5)
                    uart.write("UNLOCKED\n".encode('utf-8'))
                    print("  ✓ UNLOCKED (90°)")
                    
                elif command == "LOCK":
                    print("  → LOCKING SAFE...")
                    lock_servo.angle = 0
                    time.sleep(0.5)
                    uart.write("LOCKED\n".encode('utf-8'))
                    print("  ✓ LOCKED (0°)")
                    
                elif command == "STATUS":
                    angle = lock_servo.angle
                    status = "UNLOCKED" if angle > 45 else "LOCKED"
                    uart.write(f"{status}\n".encode('utf-8'))
                    print(f"  → Status: {status} ({angle}°)")
                    
                else:
                    print(f"  ⚠ Unknown command: {command}")
                    
            except Exception as e:
                print(f"[ERROR] {e}")
        
        time.sleep(0.1)
    
    # disconnected
    print("\n>>> DISCONNECTED <<<\n")
    print("Waiting for next connection...")
    ble.start_advertising(advertisement)
    time.sleep(0.5)
