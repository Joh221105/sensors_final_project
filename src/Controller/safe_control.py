import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart_connection = None
uart_service = None

def connect_to_safe():
    """connect to the VaultSafe"""
    global uart_connection, uart_service
    
    print("scanning for VaultSafe...")
    
    for adv in ble.start_scan(timeout=10):
        if adv.complete_name == "VaultSafe":
            print("Found VaultSafe! Connecting...")
            try:
                uart_connection = ble.connect(adv)
                print("Connected!")
                break
            except Exception as e:
                print(f"Connection failed: {e}")
    
    ble.stop_scan()
    
    if not uart_connection or not uart_connection.connected:
        print("Failed to connect to VaultSafe")
        return False
    
    # Get UART service
    try:
        uart_service = uart_connection[UARTService]
        print("UART service ready")
        return True
    except Exception as e:
        print(f"UART service failed: {e}")
        return False

def send_command(command):
    """Send command to safe"""
    global uart_connection, uart_service
    
    if not uart_connection or not uart_connection.connected:
        print("Not connected to safe")
        return False
    
    if not uart_service:
        print("UART service not available")
        return False
    
    try:
        uart_service.write(f"{command}\n".encode('utf-8'))
        print(f"Sent: {command}")
        
        # Wait for response
        time.sleep(0.2)
        if uart_service.in_waiting:
            response = uart_service.read(uart_service.in_waiting).decode('utf-8').strip()
            print(f"Response: {response}")
            return True
        
        return True
    except Exception as e:
        print(f"Send failed: {e}")
        return False

def lock_safe():
    """Lock the safe"""
    return send_command("LOCK")

def unlock_safe():
    """Unlock the safe"""
    return send_command("UNLOCK")

def get_safe_status():
    """Get current safe status"""
    if send_command("STATUS"):
        time.sleep(0.2)
        if uart_service and uart_service.in_waiting:
            response = uart_service.read(uart_service.in_waiting).decode('utf-8').strip()
            return response
    return "UNKNOWN"
