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
BOUNCE_STRENGTH = -25
CHECKPOINT_COOLDOWN = 30  # Frames between checkpoint activations

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
LIGHT_YELLOW = (255, 255, 128)

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
        self.reset_pos = (0, 0)  # Current checkpoint or start position
        self.rect.center = self.start_pos
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.coyote_timer = 0
        self.can_jump = False
        self.checkpoint_cooldown = 0

    def reset_position(self):
        self.rect.midbottom = (self.reset_pos[0], self.reset_pos[1])
        self.velocity_y = 0
        self.velocity_x = 0

    def update(self, platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks):
        old_rect = self.rect.copy()
        
        # First check for hazards
        for hazard in hazards:
            if self.rect.colliderect(hazard.rect):
                self.reset_position()
                return
        
        # Checkpoint cooldown
        if self.checkpoint_cooldown > 0:
            self.checkpoint_cooldown -= 1
                
        # Handle horizontal movement
        self.rect.x += self.velocity_x
        self._handle_horizontal_collisions(platforms)
        self._handle_horizontal_collisions(moving_platforms)
        self._handle_horizontal_collisions(breakable_blocks)
                
        # Handle vertical movement (gravity)
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # Check collisions with normal platforms
        if self._handle_vertical_collisions(platforms, old_rect):
            pass  # Already handled in the function
        # Check collisions with moving platforms
        elif self._handle_vertical_collisions(moving_platforms, old_rect):
            pass  # Already handled in the function
        # Check collisions with breakable blocks
        elif self._handle_vertical_collisions(breakable_blocks, old_rect, break_blocks=True):
            pass  # Already handled in the function
        
        # Check bounce pads
        for bounce in bounce_pads:
            if self.rect.colliderect(bounce.rect) and self.velocity_y > 0:
                if old_rect.bottom <= bounce.rect.top + 10:
                    self.rect.bottom = bounce.rect.top
                    self.velocity_y = BOUNCE_STRENGTH
                    # Play bounce sound or animation here if needed
                    bounce.activate()
                    self.on_ground = False

        # Check checkpoints
        for checkpoint in checkpoints:
            if self.rect.colliderect(checkpoint.rect) and self.checkpoint_cooldown == 0:
                self.reset_pos = (checkpoint.rect.centerx, checkpoint.rect.top)
                self.checkpoint_cooldown = CHECKPOINT_COOLDOWN
                checkpoint.activate()
        
        # Screen boundaries
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

        # Update jump ability
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
    
    def _handle_horizontal_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
    
    def _handle_vertical_collisions(self, platforms, old_rect, break_blocks=False):
        collision_occurred = False
        for platform in list(platforms):  # Use list to allow removal during iteration
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    if old_rect.bottom <= platform.rect.top + 10:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.velocity_y = 0
                        collision_occurred = True
                        
                        # If it's a breakable block and we're landing on it, break it
                        if break_blocks and isinstance(platform, BreakableBlock):
                            platform.break_block()
                    else:
                        if self.velocity_x > 0:
                            self.rect.right = platform.rect.left
                        elif self.velocity_x < 0:
                            self.rect.left = platform.rect.right
                elif self.velocity_y < 0:
                    if old_rect.top >= platform.rect.bottom - 10:
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0
                        collision_occurred = True
                        
                        # If hitting a breakable block from below, break it
                        if break_blocks and isinstance(platform, BreakableBlock):
                            platform.break_block()
                    else:
                        if self.velocity_x > 0:
                            self.rect.right = platform.rect.left
                        elif self.velocity_x < 0:
                            self.rect.left = platform.rect.right
        return collision_occurred

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

class SmallPlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image.fill(DARK_GREEN)

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, size=50):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        pygame.draw.polygon(self.image, GRAY, [(size//2, 0), (0, size), (size, size)])

class BouncePad(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.base_image = pygame.Surface((width, height))
        self.base_image.fill(ORANGE)
        self.active_image = pygame.Surface((width, height))
        self.active_image.fill(LIGHT_YELLOW)
        
        # Add visual indicator (arrow)
        arrow_points = [(width//2, 0), (width//4, height//2), (3*width//4, height//2)]
        pygame.draw.polygon(self.base_image, WHITE, arrow_points)
        pygame.draw.polygon(self.active_image, WHITE, arrow_points)
        
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.active_timer = 0
    
    def activate(self):
        self.image = self.active_image
        self.active_timer = 10  # Show active state for 10 frames
    
    def update(self):
        if self.active_timer > 0:
            self.active_timer -= 1
            if self.active_timer == 0:
                self.image = self.base_image

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.inactive_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.active_image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw checkpoint flag
        pygame.draw.rect(self.inactive_image, YELLOW, pygame.Rect(width//2-5, 0, 10, height))
        pygame.draw.rect(self.inactive_image, YELLOW, pygame.Rect(0, 0, width, 10))
        
        pygame.draw.rect(self.active_image, LIGHT_YELLOW, pygame.Rect(width//2-5, 0, 10, height))
        pygame.draw.rect(self.active_image, LIGHT_YELLOW, pygame.Rect(0, 0, width, 10))
        
        self.image = self.inactive_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_active = False
    
    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.image = self.active_image

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, move_distance=120, move_speed=2):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.start_x = x
        self.start_y = y
        self.move_distance = move_distance
        self.move_speed = move_speed
        self.direction = 1  # 1 for right/down, -1 for left/up
        self.move_axis = "horizontal"  # or "vertical"
        self.distance_moved = 0
    
    def update(self):
        if self.move_axis == "horizontal":
            self.rect.x += self.move_speed * self.direction
            self.distance_moved += abs(self.move_speed)
            
            if self.distance_moved >= self.move_distance:
                self.direction *= -1
                self.distance_moved = 0
        else:  # vertical
            self.rect.y += self.move_speed * self.direction
            self.distance_moved += abs(self.move_speed)
            
            if self.distance_moved >= self.move_distance:
                self.direction *= -1
                self.distance_moved = 0

class BreakableBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Draw crack lines
        pygame.draw.line(self.image, BLACK, (0, 0), (width//2, height//2), 2)
        pygame.draw.line(self.image, BLACK, (width, 0), (width//2, height//2), 2)
        pygame.draw.line(self.image, BLACK, (width//2, height//2), (width//2, height), 2)
        
        self.breaking = False
        self.break_timer = 0
    
    def break_block(self):
        if not self.breaking:
            self.breaking = True
            self.break_timer = 90# Break after 10 frames
    
    def update(self):
        if self.breaking:
            self.break_timer -= 1
            # Flash the block before breaking
            if self.break_timer % 2 == 0:
                self.image.fill(LIGHT_GRAY)
            else:
                self.image.fill(BROWN)
                
            if self.break_timer <= 0:
                self.kill()  # Remove the block

def load_level(filepath):
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    bounce_pads = pygame.sprite.Group()
    checkpoints = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    breakable_blocks = pygame.sprite.Group()

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

        # Add Small Platforms
        for small_platform_data in level_data.get("small_platforms", []):
            small_platform = SmallPlatform(
                small_platform_data["x"],
                small_platform_data["y"],
                small_platform_data["width"],
                small_platform_data["height"]
            )
            all_sprites.add(small_platform)
            platforms.add(small_platform)
            
        # Add Bounce Pads
        for bounce_data in level_data.get("bounce_pads", []):
            bounce = BouncePad(
                bounce_data["x"],
                bounce_data["y"],
                bounce_data["width"],
                bounce_data["height"]
            )
            all_sprites.add(bounce)
            bounce_pads.add(bounce)
            
        # Add Checkpoints
        for checkpoint_data in level_data.get("checkpoints", []):
            checkpoint = Checkpoint(
                checkpoint_data["x"],
                checkpoint_data["y"],
                checkpoint_data["width"],
                checkpoint_data["height"]
            )
            all_sprites.add(checkpoint)
            checkpoints.add(checkpoint)
            
        # Add Moving Platforms
        for moving_platform_data in level_data.get("moving_platforms", []):
            moving_platform = MovingPlatform(
                moving_platform_data["x"],
                moving_platform_data["y"],
                moving_platform_data["width"],
                moving_platform_data["height"],
                moving_platform_data.get("move_distance", 120),
                moving_platform_data.get("move_speed", 2)
            )
            # Set movement axis if specified
            if "move_axis" in moving_platform_data:
                moving_platform.move_axis = moving_platform_data["move_axis"]
                
            all_sprites.add(moving_platform)
            moving_platforms.add(moving_platform)
            
        # Add Breakable Blocks
        for breakable_data in level_data.get("breakable_blocks", []):
            breakable = BreakableBlock(
                breakable_data["x"],
                breakable_data["y"],
                breakable_data["width"],
                breakable_data["height"]
            )
            all_sprites.add(breakable)
            breakable_blocks.add(breakable)

        # Set player start position
        if level_data.get("player_start"):
            player.start_pos = (
                level_data["player_start"]["x"],
                level_data["player_start"]["y"]
            )
            player.reset_pos = player.start_pos
        else:
            # Default player position on ground
            player.start_pos = (400, SCREEN_HEIGHT - 140)
            player.reset_pos = player.start_pos
    else:
        # Default player position
        player.start_pos = (400, SCREEN_HEIGHT - 140)
        player.reset_pos = player.start_pos

    player.reset_position()

    return all_sprites, platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks, player

def main(level_file=None):
    # If no level file specified, try to use command line argument
    if level_file is None and len(sys.argv) > 1:
        level_file = sys.argv[1]

    # Default to temp level if still no file specified
    if level_file is None:
        level_dir = "levels"
        level_file = os.path.join(level_dir, "_temp_level.json")

    # Load level
    all_sprites, platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks, player = load_level(level_file)

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

        # Update all sprites
        bounce_pads.update()
        moving_platforms.update()
        breakable_blocks.update()
        player.update(platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks)

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