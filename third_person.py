import pygame
import sys
import time
from BluetoothV2.game_controller import GameController

# Initialize pygame
pygame.init()

# Constants
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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer")
clock = pygame.time.Clock()

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

        self.rect.x += self.velocity_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        was_on_ground = self.on_ground
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    if old_rect.bottom <= platform.rect.top + 10:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.velocity_y = 0
                    else:
                        if self.velocity_x > 0:
                            self.rect.right = platform.rect.left
                        elif self.velocity_x < 0:
                            self.rect.left = platform.rect.right
                elif self.velocity_y < 0:
                    if old_rect.top >= platform.rect.bottom - 10:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0
                    else:
                        if self.velocity_x > 0:
                            self.rect.right = platform.rect.left
                        elif self.velocity_x < 0:
                            self.rect.left = platform.rect.right

        if self.rect.left < 190:
            self.rect.left = 190
        if self.rect.right > SCREEN_WIDTH - 190:
            self.rect.right = SCREEN_WIDTH - 190
        if self.rect.top < 100:
            self.rect.top = 100
            self.velocity_y = 0
        if self.rect.bottom > SCREEN_HEIGHT - 140:
            self.rect.bottom = SCREEN_HEIGHT - 140
            self.on_ground = True
            self.velocity_y = 0

        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.can_jump = True
        elif was_on_ground and not self.on_ground:
            self.coyote_timer = COYOTE_TIME
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1
                self.can_jump = True
            else:
                self.can_jump = False

    def jump(self):
        if self.can_jump:
            self.velocity_y = JUMP_STRENGTH
            self.coyote_timer = 0
            self.can_jump = False

    def move_left(self):
        self.velocity_x = -PLAYER_SPEED

    def move_right(self):
        self.velocity_x = PLAYER_SPEED

    def stop(self):
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

# Create sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
hazards = pygame.sprite.Group()

# Create platforms
platform1 = Platform(400, 800, 200, 20)
platform2 = Platform(800, 600, 200, 20)
platform3 = Platform(400, 400, 200, 20)

all_sprites.add(platform1, platform2, platform3)
platforms.add(platform1, platform2, platform3)

# Create player and set spawn position on platform1
player = Player()
player.start_pos = (platform1.rect.centerx, platform1.rect.y)
player.reset_position()
all_sprites.add(player)

# Create hazard
hazard = Hazard(600, SCREEN_HEIGHT - 140 - 50)
all_sprites.add(hazard)
hazards.add(hazard)

# Initialize Bluetooth controller
bt_controller = GameController(debug=True)
bt_controller.start()

# Wait a moment for Bluetooth to initialize
time.sleep(1)

# Display connection status
font = pygame.font.Font(None, 36)

# Game loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.velocity_x < 0:
                player.stop()
            if event.key == pygame.K_RIGHT and player.velocity_x > 0:
                player.stop()

    # Handle keyboard controls (as fallback)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_left()
    if keys[pygame.K_RIGHT]:
        player.move_right()
    if keys[pygame.K_SPACE]:
        player.jump()
    if keys[pygame.K_l]:
        running = False

    # Handle Bluetooth controller input
    if bt_controller.is_connected():
        controller_state = bt_controller.update()
        
        # Handle movement based on controller input
        if controller_state['moving_left']:
            player.move_left()
        elif controller_state['moving_right']:
            player.move_right()
        else:
            # Only stop if we were moving due to controller input
            if player.velocity_x != 0 and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                player.stop()
        
        # Handle jumping with Y controller
        if controller_state['jumping']:
            player.jump()
    
    # Update game state
    player.update(platforms, hazards)
    
    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Display connection status
    if bt_controller.is_connected():
        status_text = font.render("Bluetooth Connected", True, GREEN)
    else:
        status_text = font.render("Bluetooth Disconnected", True, RED)
    screen.blit(status_text, (10, 10))
    
    pygame.display.flip()

# Clean up Bluetooth controller before exiting
bt_controller.stop()

pygame.quit()
sys.exit()