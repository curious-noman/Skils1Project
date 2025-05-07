# your_game.py (thir_person_joystick.py)

# --- Imports ---
import pygame
import sys
import queue # Still need queue for the exception type

# --- Import the BLE client class ---
from ble_joystick_client import BleJoystickClient # Assuming the file is saved as ble_joystick_client.py

# --- Initialize pygame ---
pygame.init()

# --- Pygame Constants ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -18
PLAYER_SPEED = 5
COYOTE_TIME = 6

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# --- BLE Configuration ---
TARGET_DEVICE_NAME = "PicoJoystick-AIO"
JOYSTICK_SERVICE_UUID = "f7ac806d-5c15-45de-979c-1b0773062530"
JOYSTICK_CHAR_UUID    = "b3a16388-795d-4f31-8bc5-f387994090e2"

# --- Joystick Thresholds ---
JOYSTICK_DEADZONE_LOW = 16384  # Lower X threshold for left movement
JOYSTICK_DEADZONE_HIGH = 49152 # Upper X threshold for right movement
JOYSTICK_CENTER_LOW = 24000    # Lower bound of X center deadzone
JOYSTICK_CENTER_HIGH = 40000   # Upper bound of X center deadzone

# --- NEW CONSTANT FOR JUMP ---
# Define how low the Y value needs to be to trigger a jump (adjust as needed)
# Assuming lower values mean "UP"
JOYSTICK_JUMP_THRESHOLD = 16384 # Similar to the X deadzone low

# --- Pygame Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer with BLE Joystick (Modular)")
clock = pygame.time.Clock()

# --- Pygame Classes (Player, Platform, Hazard - Same as before) ---
# [Your Player, Platform, Hazard classes remain here]
# Start Paste
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.start_pos = (0, 0)  # Will be set after platform creation
        self.rect.center = self.start_pos
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.coyote_timer = 0
        self.can_jump = False

    def reset_position(self):
        self.rect.midbottom = (self.start_pos[0], self.start_pos[1])
        self.velocity_y = 0
        self.velocity_x = 0

    def update(self, platforms, hazards):
        old_rect = self.rect.copy()

        for hazard in hazards:
            if self.rect.colliderect(hazard.rect):
                self.reset_position()
                return

        # --- X Movement Collision ---
        self.rect.x += self.velocity_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0: # Moving left
                    self.rect.left = platform.rect.right
        # Reset velocity_x after collision check if needed? Or handled by stop()?

        # --- Y Movement and Gravity ---
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        was_on_ground = self.on_ground
        self.on_ground = False # Assume not on ground until collision check

        # --- Y Collision Detection ---
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Check if landing on top
                if self.velocity_y > 0 and old_rect.bottom <= platform.rect.top + self.velocity_y + 1 : # Check if player bottom was above or near platform top in prev frame
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                # Check if hitting head on bottom
                elif self.velocity_y < 0 and old_rect.top >= platform.rect.bottom + self.velocity_y -1: # Check if player top was below or near platform bottom
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # If colliding horizontally while moving vertically (stuck in side)
                # Need careful logic here to prevent sticking if already handled X collision
                # This part can be tricky, potentially adjust based on velocity direction more?
                # For now, prioritize vertical collision resolution if landing/hitting head.

        # --- Screen Boundaries ---
        # Adjusted slightly to prevent sticking right at edge
        if self.rect.left < 190:
            self.rect.left = 190
            self.velocity_x = max(0, self.velocity_x) # Stop horizontal movement into left wall
        if self.rect.right > SCREEN_WIDTH - 190:
            self.rect.right = SCREEN_WIDTH - 190
            self.velocity_x = min(0, self.velocity_x) # Stop horizontal movement into right wall

        if self.rect.top < 100:
            self.rect.top = 100
            if self.velocity_y < 0: self.velocity_y = 0 # Stop vertical movement into ceiling

        # Ground boundary - landing check
        if self.rect.bottom > SCREEN_HEIGHT - 140:
            self.rect.bottom = SCREEN_HEIGHT - 140
            self.on_ground = True
            self.velocity_y = 0 # Should be set to 0 on landing

        # --- Coyote Time & Jump Ability ---
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.can_jump = True
        elif was_on_ground and not self.on_ground: # Just left the ground
             self.coyote_timer = COYOTE_TIME
             # Keep can_jump True during coyote time
        else: # In the air
            if self.coyote_timer > 0:
                self.coyote_timer -= 1
                self.can_jump = True # Allow jump during coyote time frames
            else:
                self.can_jump = False # Coyote time expired

    def jump(self):
        if self.can_jump:
            self.velocity_y = JUMP_STRENGTH
            self.coyote_timer = 0  # Use up coyote time
            self.can_jump = False # Prevent double jump immediately

    def move_left(self):
        self.velocity_x = -PLAYER_SPEED

    def move_right(self):
        self.velocity_x = PLAYER_SPEED

    def stop(self):
        # Stop horizontal movement only
        self.velocity_x = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, size=50):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        pygame.draw.polygon(self.image, GRAY, [(size//2, 0), (0, size), (size, size)])
# End Paste

# --- Create Sprites and Groups ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
hazards = pygame.sprite.Group()

# Create platforms
ground = Platform(0, SCREEN_HEIGHT - 140, SCREEN_WIDTH, 40)
platform1 = Platform(400, 800, 200, 20)
platform2 = Platform(800, 600, 200, 20)
platform3 = Platform(400, 400, 200, 20)
all_sprites.add(ground, platform1, platform2, platform3)
platforms.add(ground, platform1, platform2, platform3)

# Create player
player = Player()
player.start_pos = (platform1.rect.centerx, platform1.rect.y)
player.reset_position()
all_sprites.add(player)

# Create hazard
hazard = Hazard(600, SCREEN_HEIGHT - 140 - 50)
all_sprites.add(hazard)
hazards.add(hazard)


# --- Initialize and Start BLE Client ---
print("Main Thread: Initializing BLE Client...")
# Basic UUID check (keep as is)
if "YOUR_UNIQUE_SERVICE_UUID_HERE" in JOYSTICK_SERVICE_UUID or \
   "YOUR_UNIQUE_CHAR_UUID_HERE" in JOYSTICK_CHAR_UUID or \
   JOYSTICK_SERVICE_UUID == "f7ac806d-5c15-45de-979c-1b0773062530" or \
   JOYSTICK_CHAR_UUID == "b3a16388-795d-4f31-8bc5-f387994090e2": # Added check for default UUIDs
    print("\n" + "*"*40)
    print("WARNING: Using default placeholder UUIDs.")
    print("         Please replace them with your generated UUIDs")
    print("         in both this script and the Pico W code.")
    print("*"*40 + "\n")
    # Allow continuing with defaults for testing, but keep warning
joystick_client = BleJoystickClient(TARGET_DEVICE_NAME, JOYSTICK_SERVICE_UUID, JOYSTICK_CHAR_UUID)
joystick_client.start() # Start the BLE thread


# --- Game Loop ---
running = True
print("Main Thread: Starting Pygame loop...")
while running:
    # --- Timing ---
    clock.tick(FPS)

    # --- Get Joystick State from BLE Client ---
    joystick_x = 32768 # Default center
    joystick_y = 32768 # Default center
    button_pressed = False
    is_ble_connected = False

    if joystick_client:
        joystick_x, joystick_y, button_pressed = joystick_client.get_state()
        is_ble_connected = joystick_client.connected()
        # print(f"X={joystick_x}, Y={joystick_y}, Btn={button_pressed}, Connected={is_ble_connected}") # Debug print

    # --- Process Pygame Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Handle Input based on BLE Data ---
    if is_ble_connected:
        # Horizontal Movement (remains the same)
        if joystick_x < JOYSTICK_DEADZONE_LOW:
            player.move_left()
        elif joystick_x > JOYSTICK_DEADZONE_HIGH:
            player.move_right()
        elif JOYSTICK_CENTER_LOW < joystick_x < JOYSTICK_CENTER_HIGH:
            player.stop()
        else:
            player.stop()

        # --- MODIFIED JUMPING LOGIC ---
        # Check if button is pressed OR if joystick Y is below the jump threshold
        if button_pressed or (joystick_y < JOYSTICK_JUMP_THRESHOLD):
            player.jump() # Calls the player's jump method

    else:
        # If disconnected, stop horizontal movement
        player.stop()

    # Quit key (optional)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_l]:
        running = False


    # --- Update ---
    player.update(platforms, hazards)

    # --- Draw ---
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # --- Display ---
    pygame.display.flip()


# --- Clean Up ---
print("Main Thread: Exiting Pygame loop.")
if joystick_client:
    print("Main Thread: Signaling BLE client to stop...")
    joystick_client.stop()

pygame.quit()
print("Main Thread: Pygame quit.")
sys.exit()