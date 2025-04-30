import pygame
import sys
import json
import os

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
pygame.display.set_caption("2D Platformer - Custom Level")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.start_pos = (0, 0)  # Will be set after loading level
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

def load_level(filepath):
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    hazards = pygame.sprite.Group()

    # Create player
    player = Player()
    all_sprites.add(player)

    # Add default ground platform
    ground = Platform(0, SCREEN_HEIGHT - 140, SCREEN_WIDTH, 40)
    all_sprites.add(ground)
    platforms.add(ground)

    # Load level data from file
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            level_data = json.load(f)

        # Add platforms
        for platform_data in level_data.get("platforms", []):
            platform = Platform(
                platform_data["x"],
                platform_data["y"],
                platform_data["width"],
                platform_data["height"]
            )
            all_sprites.add(platform)
            platforms.add(platform)

        # Add hazards
        for hazard_data in level_data.get("hazards", []):
            hazard = Hazard(
                hazard_data["x"],
                hazard_data["y"],
                hazard_data.get("size", 50)
            )
            all_sprites.add(hazard)
            hazards.add(hazard)

        # Set player start position
        if level_data.get("player_start"):
            player.start_pos = (
                level_data["player_start"]["x"],
                level_data["player_start"]["y"]
            )
        else:
            # Default player position on ground
            player.start_pos = (400, SCREEN_HEIGHT - 140)
    else:
        # Default player position
        player.start_pos = (400, SCREEN_HEIGHT - 140)

    player.reset_position()

    return all_sprites, platforms, hazards, player

def main(level_file=None):
    # If no level file specified, try to use command line argument
    if level_file is None and len(sys.argv) > 1:
        level_file = sys.argv[1]

    # Default to temp level if still no file specified
    if level_file is None:
        level_dir = "levels"
        level_file = os.path.join(level_dir, "_temp_level.json")

    # Load level
    all_sprites, platforms, hazards, player = load_level(level_file)

    # Font setup for UI
    font = pygame.font.SysFont('Arial', 20)

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
                if event.key == pygame.K_r:
                    # Reset player position
                    player.reset_position()
                if event.key == pygame.K_ESCAPE:
                    # Return to level builder
                    running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.velocity_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.velocity_x > 0:
                    player.stop()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()

        player.update(platforms, hazards)

        # Draw everything
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw UI text
        controls_text = font.render("Controls: Arrow Keys to Move, SPACE to Jump, R to Reset, ESC to Exit", True, WHITE)
        screen.blit(controls_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()