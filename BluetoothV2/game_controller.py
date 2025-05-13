from BluetoothV2.bluetooth_controller import BluetoothController

class GameController:
    # Default thresholds for controller input
    X_CENTER = 32767  # Middle value for X axis (0-65535 range)
    Y_CENTER = 32767  # Middle value for Y axis (0-65535 range)
    DEADZONE = 5000   # Deadzone to prevent drift
    JUMP_THRESHOLD = 20000  # Threshold for jump detection
    
    def __init__(self, debug=False):
        self.bt_controller = BluetoothController(debug=debug)
        self.debug = debug
        
        # Game control state
        self.moving_left = False
        self.moving_right = False
        self.jumping = False
        self.button_pressed = False
        
        # Previous state for edge detection
        self.prev_button_state = False
        
    def log(self, message):
        """Print debug messages if debug mode is enabled"""
        if self.debug:
            print(f"[Game Controller] {message}")
    
    def start(self):
        """Start the Bluetooth controller"""
        self.bt_controller.start()
    
    def stop(self):
        """Stop the Bluetooth controller"""
        self.bt_controller.stop()
    
    def is_connected(self):
        """Check if the Bluetooth controller is connected"""
        return self.bt_controller.is_connected()
    
    def update(self):
        """Update the game control state based on Bluetooth controller state"""
        # Get the current state from the Bluetooth controller
        state = self.bt_controller.get_controller_state()
        
        # Process X-axis for horizontal movement
        x_value = state['x']
        if abs(x_value - self.X_CENTER) > self.DEADZONE:
            if x_value < self.X_CENTER - self.DEADZONE:
                self.moving_left = True
                self.moving_right = False
                self.log(f"Moving left: {x_value}")
            elif x_value > self.X_CENTER + self.DEADZONE:
                self.moving_left = False
                self.moving_right = True
                self.log(f"Moving right: {x_value}")
        else:
            self.moving_left = False
            self.moving_right = False
        
        # Process Y-axis for jumping
        y_value = state['y']
        # Lower Y values indicate upward movement
        if y_value < self.Y_CENTER - self.JUMP_THRESHOLD:
            if not self.jumping:  # Only trigger jump on the initial movement
                self.jumping = True
                self.log(f"Jump triggered: {y_value}")
        else:
            self.jumping = False
        
        # Process button state (edge detection - only trigger on press, not hold)
        current_button_state = state['button'] > 0
        if current_button_state and not self.prev_button_state:
            self.button_pressed = True
            self.log(f"Button pressed: {state['button']}")
        else:
            self.button_pressed = False
        
        # Update previous button state for next frame
        self.prev_button_state = current_button_state
        
        return {
            'moving_left': self.moving_left,
            'moving_right': self.moving_right,
            'jumping': self.jumping,
            'button_pressed': self.button_pressed,
            'x_connected': state['x_connected'],
            'y_connected': state['y_connected']
        }
