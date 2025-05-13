import pygame
import sys
import json
import os
import time
from first_person import run_game
from BluetoothV2.game_controller import GameController

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -18
PLAYER_SPEED = 7
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
        # Load wizard sprites
        self.sprites = []
        # Increased player size from 30x50 to 60x100
        PLAYER_WIDTH = 200
        PLAYER_HEIGHT = 300
        
        for i in range(1, 9):  # wizard1.png to wizard8.png
            try:
                sprite = pygame.image.load(f"sprites/wizards{i}.png").convert_alpha()
                # Scale to new larger size
                sprite = pygame.transform.scale(sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))
                self.sprites.append(sprite)
            except:
                # Fallback if sprites not found
                print(f"Warning: Could not load wizards{i}.png, using fallback")
                surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(surf, BLUE, (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT))
                self.sprites.append(surf)
        
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.start_pos = (0, 0)
        self.reset_pos = (0, 0)
        self.rect.center = self.start_pos
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.coyote_timer = 0
        self.can_jump = False
        self.checkpoint_cooldown = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # Adjust for animation speed
        self.facing_right = True
        self.is_moving = False

    def reset_position(self):
        self.rect.midbottom = (self.reset_pos[0], self.reset_pos[1])
        self.velocity_y = 0
        self.velocity_x = 0

    def update(self, platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks):
        old_rect = self.rect.copy()
        
        # Update animation first
        self.update_animation()
        
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
        self.facing_right = False
        self.is_moving = True

    def move_right(self):
        self.velocity_x = PLAYER_SPEED
        self.facing_right = True
        self.is_moving = True

    def stop(self):
        self.velocity_x = 0
        self.is_moving = False
        self.current_sprite = 0  # Reset to first frame when not moving
        self.image = self.sprites[self.current_sprite]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update_animation(self):
        if self.is_moving:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
                self.image = self.sprites[self.current_sprite]
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)


class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, size=50):
        super().__init__()
        # Increased hazard size by 50%
        size = int(size)
        self.image = pygame.image.load("sprites/spikes.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (size * 2, size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        try:
            # Try to load the platform texture
            self.image = pygame.image.load("sprites/platform_wild_west.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except pygame.error:
            # Fallback if texture not found
            print("Warning: Could not load platform texture, using fallback")
            self.image = pygame.Surface((width, height))
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class SmallPlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image.fill(DARK_GREEN)

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

# Global Bluetooth controller that can be accessed by all classes
bt_controller = None

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        
        # Load the images
        try:
            self.inactive_image = pygame.image.load("images/dino4.png").convert_alpha()
            self.active_image = pygame.image.load("images/dino4.png").convert_alpha()
            
            # Scale images to the desired size if needed
            self.inactive_image = pygame.transform.scale(self.inactive_image, (width *4 , height*4))
            self.active_image = pygame.transform.scale(self.active_image, (width*4, height*4))
            
            # You could modify the active image to look different if desired
            # For example, make it brighter when active
            self.active_image.fill((50, 50, 0, 0), special_flags=pygame.BLEND_ADD)
            
        except:
            # Fallback to the original flag drawing if image loading fails
            self.inactive_image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.active_image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            pygame.draw.rect(self.inactive_image, YELLOW, pygame.Rect(width//2-5, 0, 10, height))
            pygame.draw.rect(self.inactive_image, YELLOW, pygame.Rect(0, 0, width, 10))
            
            pygame.draw.rect(self.active_image, LIGHT_YELLOW, pygame.Rect(width//2-5, 0, 10, height))
            pygame.draw.rect(self.active_image, LIGHT_YELLOW, pygame.Rect(0, 0, width, 10))

        self.image = self.inactive_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_active = False
        self.has_triggered = False
    
    def activate(self):
        if not self.is_active and not self.has_triggered:
            self.is_active = True
            self.has_triggered = True
            self.image = self.active_image
            # Call the first-person game function with the existing Bluetooth controller
            from first_person import run_game_with_controller
            # Pass the existing Bluetooth controller to the first-person game
            run_game_with_controller(bt_controller)

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
            self.break_timer = 90  # Break after 90 frames
    
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
    
    # Load level data from file
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            level_data = json.load(f)

        for hazard_data in level_data.get("hazards", []):
            hazard = Hazard(
                hazard_data["x"],
                hazard_data["y"],
                hazard_data.get("size", 50)
            )
            all_sprites.add(hazard)
            hazards.add(hazard)

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

    # Load background image - MODIFIED FOR SCROLLING
    try:
        original_bg = pygame.image.load("sprites/background_wild_west.png").convert()
        
        # Calculate scaled dimensions while maintaining aspect ratio
        bg_ratio = original_bg.get_width() / original_bg.get_height()
        scaled_height = SCREEN_HEIGHT
        scaled_width = int(scaled_height * bg_ratio)
        
        # Scale the background
        background = pygame.transform.scale(original_bg, (scaled_width, scaled_height))
        
        # Scrolling variables
        bg_x = 0
        max_scroll = scaled_width - SCREEN_WIDTH
        scroll_speed = 2
        use_background_image = True
        
    except pygame.error:
        print("Warning: Could not load background image, using solid color")
        use_background_image = False

    # Font setup for UI
    font = pygame.font.SysFont('Arial', 20)

    # Initialize Bluetooth controller
    global bt_controller
    bt_controller = GameController(debug=True)
    bt_controller.start()
    
    # Wait a moment for Bluetooth to initialize
    time.sleep(1)

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

        # Handle keyboard controls (as fallback)
        keys = pygame.key.get_pressed()
        keyboard_input = False
        
        if keys[pygame.K_LEFT]:
            player.move_left()
            keyboard_input = True
        elif keys[pygame.K_RIGHT]:
            player.move_right()
            keyboard_input = True
        
        # Handle Bluetooth controller input
        if bt_controller.is_connected():
            controller_state = bt_controller.update()
            
            # Handle movement based on controller input
            if controller_state['moving_left']:
                player.move_left()
            elif controller_state['moving_right']:
                player.move_right()
            elif not keyboard_input:
                # Only stop if we were moving due to controller input and no keyboard input
                player.stop()
            
            # Handle jumping with Y controller
            if controller_state['jumping']:
                player.jump()
        elif not keyboard_input:
            # If no Bluetooth and no keyboard input, stop the player
            player.stop()

        # Update all sprites
        bounce_pads.update()
        moving_platforms.update()
        breakable_blocks.update()
        player.update(platforms, hazards, bounce_pads, checkpoints, moving_platforms, breakable_blocks)

        # UPDATE BACKGROUND POSITION BASED ON PLAYER MOVEMENT
        if use_background_image:
            # Only scroll when player is moving right and we haven't reached the end
            if player.velocity_x > 0 and bg_x > -max_scroll:
                bg_x -= scroll_speed
            # Clamp the position so we don't show empty space at the end
            bg_x = max(-max_scroll, bg_x)

        # Draw everything
        if use_background_image:
            # Draw the background at the current scroll position
            screen.blit(background, (bg_x, 0))
        else:
            screen.fill(BLACK)
            
        all_sprites.draw(screen)

        # Draw UI text
        # Display Bluetooth connection status
        if bt_controller.is_connected():
            status_text = font.render("Bluetooth Connected", True, GREEN)
        else:
            status_text = font.render("Bluetooth Disconnected", True, RED)
        screen.blit(status_text, (10, 10))

        pygame.display.flip()

    # Clean up Bluetooth controller before exiting
    bt_controller.stop()
    
    pygame.quit()

if __name__ == "__main__":
    main()