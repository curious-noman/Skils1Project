import pygame
import sys
import json
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_SIZE = 40
FPS = 60

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2D Platformer Level Builder")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont('Arial', 20)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border

        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class TileSelector:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.tiles = [
            {"name": "Platform", "color": GREEN, "type": "platform"},
            {"name": "Small Platform", "color": DARK_GREEN, "type": "small_platform"},
            {"name": "Hazard", "color": GRAY, "type": "hazard"},
            {"name": "Bounce Pad", "color": ORANGE, "type": "bounce"},
            {"name": "Checkpoint", "color": YELLOW, "type": "checkpoint"},
            {"name": "Moving Platform", "color": PURPLE, "type": "moving_platform"},
            {"name": "Breakable Block", "color": BROWN, "type": "breakable"},
            {"name": "Player Start", "color": BLUE, "type": "player"}
        ]
        self.selected_tile = None
        self.tile_rects = []

        # Create tile buttons
        tile_height = 60
        spacing = 5
        for i, tile in enumerate(self.tiles):
            tile_rect = pygame.Rect(
                x + 10,
                y + 10 + i * (tile_height + spacing),
                width - 20,
                tile_height
            )
            self.tile_rects.append({"rect": tile_rect, "tile": tile})

    def draw(self, surface):
        # Draw panel background
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Draw tile buttons
        for tile_data in self.tile_rects:
            rect = tile_data["rect"]
            tile = tile_data["tile"]

            # Button background
            pygame.draw.rect(surface, WHITE, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)

            # Tile preview
            preview_rect = pygame.Rect(rect.x + 10, rect.y + 10, 40, 40)

            if tile["type"] == "platform":
                pygame.draw.rect(surface, tile["color"], preview_rect)
            elif tile["type"] == "small_platform":
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.x, preview_rect.y + 20, 40, 20))
            elif tile["type"] == "hazard":
                pygame.draw.polygon(surface, tile["color"],
                                    [(preview_rect.centerx, preview_rect.y),
                                     (preview_rect.x, preview_rect.bottom),
                                     (preview_rect.right, preview_rect.bottom)])
            elif tile["type"] == "bounce":
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.x, preview_rect.y + 30, 40, 10))
                # Draw arrow
                pygame.draw.polygon(surface, WHITE,
                                    [(preview_rect.centerx, preview_rect.y),
                                     (preview_rect.centerx - 10, preview_rect.y + 15),
                                     (preview_rect.centerx + 10, preview_rect.y + 15)])
            elif tile["type"] == "checkpoint":
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.centerx - 5, preview_rect.y, 10, 40))
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.x, preview_rect.y, 40, 10))
            elif tile["type"] == "moving_platform":
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.x, preview_rect.y + 20, 40, 20))
                # Draw movement arrows
                pygame.draw.line(surface, BLACK,
                                 (preview_rect.x + 10, preview_rect.y + 15),
                                 (preview_rect.x + 30, preview_rect.y + 15), 2)
                pygame.draw.polygon(surface, BLACK,
                                    [(preview_rect.x + 10, preview_rect.y + 10),
                                     (preview_rect.x, preview_rect.y + 15),
                                     (preview_rect.x + 10, preview_rect.y + 20)])
                pygame.draw.polygon(surface, BLACK,
                                    [(preview_rect.x + 30, preview_rect.y + 10),
                                     (preview_rect.x + 40, preview_rect.y + 15),
                                     (preview_rect.x + 30, preview_rect.y + 20)])
            elif tile["type"] == "breakable":
                pygame.draw.rect(surface, tile["color"], preview_rect)
                # Draw crack lines
                pygame.draw.line(surface, BLACK,
                                 (preview_rect.x, preview_rect.y),
                                 (preview_rect.x + 20, preview_rect.y + 20), 2)
                pygame.draw.line(surface, BLACK,
                                 (preview_rect.x + 40, preview_rect.y),
                                 (preview_rect.x + 20, preview_rect.y + 20), 2)
                pygame.draw.line(surface, BLACK,
                                 (preview_rect.x + 20, preview_rect.y + 20),
                                 (preview_rect.x + 20, preview_rect.y + 40), 2)
            elif tile["type"] == "player":
                pygame.draw.rect(surface, tile["color"],
                                 pygame.Rect(preview_rect.x + 5, preview_rect.y, 30, 40))

            # Highlight selected
            if self.selected_tile == tile:
                pygame.draw.rect(surface, YELLOW, rect, 3)

            # Label
            text_surf = font.render(tile["name"], True, BLACK)
            text_rect = text_surf.get_rect(
                midleft=(preview_rect.right + 10, preview_rect.centery)
            )
            surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        for tile_data in self.tile_rects:
            if tile_data["rect"].collidepoint(pos):
                self.selected_tile = tile_data["tile"]
                return True
        return False


class Grid:
    def __init__(self, x, y, width, height, grid_size):
        self.rect = pygame.Rect(x, y, width, height)
        self.grid_size = grid_size
        self.cells = {}  # (x, y) -> {"type": type, "color": color}
        self.grid_width = width // grid_size
        self.grid_height = height // grid_size
        self.player_pos = None
        # For scrolling - make the actual grid larger than visible area
        self.total_width = self.grid_width * 3  # 3x wider than visible
        self.total_height = self.grid_height * 3  # 3x taller than visible
        self.camera_offset = pygame.Vector2(0, 0)

    def draw(self, surface):
        # Draw grid background
        pygame.draw.rect(surface, WHITE, self.rect)

        # Calculate visible range based on camera offset
        start_x = int(self.camera_offset.x // self.grid_size)
        start_y = int(self.camera_offset.y // self.grid_size)
        end_x = start_x + self.grid_width + 1
        end_y = start_y + self.grid_height + 1

        # Draw grid lines adjusted for camera offset
        for x in range(start_x, end_x):
            screen_x = self.rect.x + (x * self.grid_size) - self.camera_offset.x
            pygame.draw.line(
                surface,
                LIGHT_GRAY,
                (screen_x, self.rect.y),
                (screen_x, self.rect.y + self.rect.height)
            )

        for y in range(start_y, end_y):
            screen_y = self.rect.y + (y * self.grid_size) - self.camera_offset.y
            pygame.draw.line(
                surface,
                LIGHT_GRAY,
                (self.rect.x, screen_y),
                (self.rect.x + self.rect.width, screen_y)
            )

        # Draw placed tiles adjusted for camera offset
        for pos, cell in self.cells.items():
            grid_x, grid_y = pos
            x = self.rect.x + (grid_x * self.grid_size) - self.camera_offset.x
            y = self.rect.y + (grid_y * self.grid_size) - self.camera_offset.y

            # Skip tiles that are outside the visible area
            if (x + self.grid_size < self.rect.x or x > self.rect.right or
                    y + self.grid_size < self.rect.y or y > self.rect.bottom):
                continue

            if cell["type"] == "platform":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y, self.grid_size, self.grid_size)
                )
            elif cell["type"] == "small_platform":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y + self.grid_size // 2, self.grid_size, self.grid_size // 2)
                )
            elif cell["type"] == "hazard":
                pygame.draw.polygon(
                    surface,
                    cell["color"],
                    [(x + self.grid_size // 2, y),
                     (x, y + self.grid_size),
                     (x + self.grid_size, y + self.grid_size)]
                )
            elif cell["type"] == "bounce":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y + 3 * self.grid_size // 4, self.grid_size, self.grid_size // 4)
                )
                # Draw arrow
                pygame.draw.polygon(
                    surface,
                    WHITE,
                    [(x + self.grid_size // 2, y + self.grid_size // 4),
                     (x + self.grid_size // 4, y + self.grid_size // 2),
                     (x + 3 * self.grid_size // 4, y + self.grid_size // 2)]
                )
            elif cell["type"] == "checkpoint":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x + self.grid_size // 2 - 5, y, 10, self.grid_size)
                )
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y, 10, self.grid_size)
                )
            elif cell["type"] == "moving_platform":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y + self.grid_size // 2, self.grid_size, self.grid_size // 2)
                )
                # Draw movement arrows
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x + self.grid_size // 4, y + self.grid_size // 3),
                    (x + 3 * self.grid_size // 4, y + self.grid_size // 3),
                    2
                )
                pygame.draw.polygon(
                    surface,
                    BLACK,
                    [(x + self.grid_size // 4, y + self.grid_size // 4),
                     (x + self.grid_size // 8, y + self.grid_size // 3),
                     (x + self.grid_size // 4, y + 5 * self.grid_size // 12)]
                )
                pygame.draw.polygon(
                    surface,
                    BLACK,
                    [(x + 3 * self.grid_size // 4, y + self.grid_size // 4),
                     (x + 7 * self.grid_size // 8, y + self.grid_size // 3),
                     (x + 3 * self.grid_size // 4, y + 5 * self.grid_size // 12)]
                )
            elif cell["type"] == "breakable":
                pygame.draw.rect(
                    surface,
                    cell["color"],
                    pygame.Rect(x, y, self.grid_size, self.grid_size)
                )
                # Draw crack lines
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x, y),
                    (x + self.grid_size // 2, y + self.grid_size // 2),
                    2
                )
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x + self.grid_size, y),
                    (x + self.grid_size // 2, y + self.grid_size // 2),
                    2
                )
                pygame.draw.line(
                    surface,
                    BLACK,
                    (x + self.grid_size // 2, y + self.grid_size // 2),
                    (x + self.grid_size // 2, y + self.grid_size),
                    2
                )
            elif cell["type"] == "player":
                player_rect = pygame.Rect(
                    x + (self.grid_size - 30) // 2,
                    y,
                    30,
                    50
                )
                pygame.draw.rect(surface, cell["color"], player_rect)

    def get_grid_pos(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return None

        rel_x = mouse_pos[0] - self.rect.x
        rel_y = mouse_pos[1] - self.rect.y

        # Adjust for camera offset
        grid_x = int((rel_x + self.camera_offset.x) // self.grid_size)
        grid_y = int((rel_y + self.camera_offset.y) // self.grid_size)

        if 0 <= grid_x < self.total_width and 0 <= grid_y < self.total_height:
            return (grid_x, grid_y)
        return None

    def place_tile(self, grid_pos, tile_type, color):
        if grid_pos and tile_type:
            # If placing player, remove old player position
            if tile_type == "player":
                for pos in list(self.cells.keys()):
                    if self.cells[pos]["type"] == "player":
                        del self.cells[pos]
                self.player_pos = grid_pos

            # Store tile
            self.cells[grid_pos] = {
                "type": tile_type,
                "color": color
            }

    def remove_tile(self, grid_pos):
        if grid_pos in self.cells:
            # If removing player, clear player position
            if self.cells[grid_pos]["type"] == "player":
                self.player_pos = None
            del self.cells[grid_pos]

    def clear(self):
        self.cells = {}
        self.player_pos = None


class LevelBuilder:
    def __init__(self):
        # UI elements
        sidebar_width = 200
        self.camera_offset = pygame.Vector2(0, 0)
        self.dragging_grid = False
        self.last_mouse_pos = None
        self.scroll_speed = 15  # Speed of scrolling
        
        self.grid = Grid(
            sidebar_width + 10,
            10,
            SCREEN_WIDTH - sidebar_width - 20,
            SCREEN_HEIGHT - 80,
            GRID_SIZE
        )
        
        # Scrollbar dimensions
        self.h_scrollbar = pygame.Rect(
            sidebar_width + 10, 
            SCREEN_HEIGHT - 70,
            SCREEN_WIDTH - sidebar_width - 20, 
            20
        )
        self.v_scrollbar = pygame.Rect(
            SCREEN_WIDTH - 20, 
            10,
            20, 
            SCREEN_HEIGHT - 80
        )
        
        self.h_scroll_thumb = pygame.Rect(
            sidebar_width + 10,
            SCREEN_HEIGHT - 70,
            100,  # Will be calculated properly
            20
        )
        self.v_scroll_thumb = pygame.Rect(
            SCREEN_WIDTH - 20,
            10,
            20,
            60  # Will be calculated properly
        )
        
        self.dragging_h_thumb = False
        self.dragging_v_thumb = False

        self.tile_selector = TileSelector(
            10,
            10,
            sidebar_width - 20,
            300
        )

        button_y = SCREEN_HEIGHT - 60
        button_width = 150
        button_height = 40

        self.save_button = Button(
            10,
            button_y,
            button_width,
            button_height,
            "Save Level",
            GREEN,
            DARK_GREEN
        )

        self.load_button = Button(
            10 + button_width + 10,
            button_y,
            button_width,
            button_height,
            "Load Level",
            BLUE,
            (0, 0, 150)
        )

        self.clear_button = Button(
            SCREEN_WIDTH - button_width - 10,
            button_y,
            button_width,
            button_height,
            "Clear Grid",
            RED,
            (150, 0, 0)
        )

        self.play_button = Button(
            SCREEN_WIDTH - 2 * button_width - 20,
            button_y,
            button_width,
            button_height,
            "Play Level",
            YELLOW,
            (150, 150, 0)
        )

        # State
        self.is_dragging = False
        self.current_filename = "untitled"
        self.level_dir = "levels"

        # Create levels directory if it doesn't exist
        if not os.path.exists(self.level_dir):
            os.makedirs(self.level_dir)

    def draw(self, surface):
        surface.fill(BLACK)

        # Draw grid
        self.grid.draw(surface)
        
        # Update scroll thumb positions based on camera offset
        self._update_scroll_thumbs()
        
        # Draw scrollbars
        pygame.draw.rect(surface, GRAY, self.h_scrollbar)
        pygame.draw.rect(surface, GRAY, self.v_scrollbar)
        pygame.draw.rect(surface, WHITE, self.h_scroll_thumb)
        pygame.draw.rect(surface, WHITE, self.v_scroll_thumb)

        # Draw UI elements
        self.tile_selector.draw(surface)
        self.save_button.draw(surface)
        self.load_button.draw(surface)
        self.clear_button.draw(surface)
        self.play_button.draw(surface)

        # Draw current filename
        text_surf = font.render(f"File: {self.current_filename}", True, WHITE)
        surface.blit(text_surf, (10, SCREEN_HEIGHT - 90))

    def _update_scroll_thumbs(self):
        # Calculate horizontal thumb size and position
        visible_width_ratio = self.grid.grid_width / self.grid.total_width
        h_thumb_width = max(40, int(visible_width_ratio * self.h_scrollbar.width))
        
        # Calculate position based on camera offset
        max_h_offset = (self.grid.total_width - self.grid.grid_width) * self.grid.grid_size
        h_thumb_x = self.h_scrollbar.x
        if max_h_offset > 0:
            h_offset_ratio = self.grid.camera_offset.x / max_h_offset
            h_thumb_x += int(h_offset_ratio * (self.h_scrollbar.width - h_thumb_width))
        
        self.h_scroll_thumb = pygame.Rect(
            h_thumb_x,
            self.h_scrollbar.y,
            h_thumb_width,
            self.h_scrollbar.height
        )
        
        # Calculate vertical thumb size and position
        visible_height_ratio = self.grid.grid_height / self.grid.total_height
        v_thumb_height = max(40, int(visible_height_ratio * self.v_scrollbar.height))
        
        # Calculate position based on camera offset
        max_v_offset = (self.grid.total_height - self.grid.grid_height) * self.grid.grid_size
        v_thumb_y = self.v_scrollbar.y
        if max_v_offset > 0:
            v_offset_ratio = self.grid.camera_offset.y / max_v_offset
            v_thumb_y += int(v_offset_ratio * (self.v_scrollbar.height - v_thumb_height))
        
        self.v_scroll_thumb = pygame.Rect(
            self.v_scrollbar.x,
            v_thumb_y,
            self.v_scrollbar.width,
            v_thumb_height
        )

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        current_mouse_pos = pygame.mouse.get_pos()

        # Check button hover states
        self.save_button.check_hover(mouse_pos)
        self.load_button.check_hover(mouse_pos)
        self.clear_button.check_hover(mouse_pos)
        self.play_button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # Handle mouse button down
            if event.type == MOUSEBUTTONDOWN:
                # Middle mouse button for drag scrolling
                if event.button == 2 and self.grid.rect.collidepoint(mouse_pos):
                    self.dragging_grid = True
                    self.last_mouse_pos = mouse_pos
                
                # Check for scrollbar dragging
                elif event.button == 1:
                    # Check if clicked on horizontal scrollbar thumb
                    if self.h_scroll_thumb.collidepoint(mouse_pos):
                        self.dragging_h_thumb = True
                        self.last_mouse_pos = mouse_pos
                    
                    # Check if clicked on vertical scrollbar thumb
                    elif self.v_scroll_thumb.collidepoint(mouse_pos):
                        self.dragging_v_thumb = True
                        self.last_mouse_pos = mouse_pos
                    
                    # Check if clicked on horizontal scrollbar (not on thumb)
                    elif self.h_scrollbar.collidepoint(mouse_pos):
                        # Click to the left or right of thumb for page scroll
                        if mouse_pos[0] < self.h_scroll_thumb.x:
                            self.grid.camera_offset.x = max(0, self.grid.camera_offset.x - self.grid.rect.width)
                        else:
                            max_h_offset = (self.grid.total_width - self.grid.grid_width) * self.grid.grid_size
                            self.grid.camera_offset.x = min(max_h_offset, self.grid.camera_offset.x + self.grid.rect.width)
                    
                    # Check if clicked on vertical scrollbar (not on thumb)
                    elif self.v_scrollbar.collidepoint(mouse_pos):
                        # Click above or below thumb for page scroll
                        if mouse_pos[1] < self.v_scroll_thumb.y:
                            self.grid.camera_offset.y = max(0, self.grid.camera_offset.y - self.grid.rect.height)
                        else:
                            max_v_offset = (self.grid.total_height - self.grid.grid_height) * self.grid.grid_size
                            self.grid.camera_offset.y = min(max_v_offset, self.grid.camera_offset.y + self.grid.rect.height)
                    
                    # Check if clicked on tile selector
                    elif self.tile_selector.handle_click(mouse_pos):
                        pass
                    
                    # Check if clicked on grid
                    elif self.grid.rect.collidepoint(mouse_pos):
                        grid_pos = self.grid.get_grid_pos(mouse_pos)

                        # Left click to place tile
                        if self.tile_selector.selected_tile:
                            self.is_dragging = True
                            tile = self.tile_selector.selected_tile
                            self.grid.place_tile(grid_pos, tile["type"], tile["color"])
                
                # Right click to remove tile
                elif event.button == 3 and self.grid.rect.collidepoint(mouse_pos):
                    self.is_dragging = "remove"
                    grid_pos = self.grid.get_grid_pos(mouse_pos)
                    self.grid.remove_tile(grid_pos)
                
                # Mouse wheel for scrolling
                elif event.button == 4:  # Scroll Up
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Horizontal scroll with Shift+Wheel
                        self.grid.camera_offset.x = max(0, self.grid.camera_offset.x - self.scroll_speed)
                    else:
                        # Vertical scroll
                        self.grid.camera_offset.y = max(0, self.grid.camera_offset.y - self.scroll_speed)
                
                elif event.button == 5:  # Scroll Down
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Horizontal scroll with Shift+Wheel
                        max_h_offset = (self.grid.total_width - self.grid.grid_width) * self.grid.grid_size
                        self.grid.camera_offset.x = min(max_h_offset, self.grid.camera_offset.x + self.scroll_speed)
                    else:
                        # Vertical scroll
                        max_v_offset = (self.grid.total_height - self.grid.grid_height) * self.grid.grid_size
                        self.grid.camera_offset.y = min(max_v_offset, self.grid.camera_offset.y + self.scroll_speed)

                # Check if clicked on buttons
                if self.save_button.is_clicked(mouse_pos, event):
                    self.save_level()
                elif self.load_button.is_clicked(mouse_pos, event):
                    self.load_level()
                elif self.clear_button.is_clicked(mouse_pos, event):
                    self.grid.clear()
                elif self.play_button.is_clicked(mouse_pos, event):
                    self.play_level()

            # Handle mouse button up
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
                    self.dragging_h_thumb = False
                    self.dragging_v_thumb = False
                elif event.button == 2:
                    self.dragging_grid = False

            # Handle mouse motion
            elif event.type == MOUSEMOTION:
                # Handle grid dragging with middle mouse button
                if self.dragging_grid and self.last_mouse_pos:
                    dx = self.last_mouse_pos[0] - current_mouse_pos[0]
                    dy = self.last_mouse_pos[1] - current_mouse_pos[1]
                    
                    # Update camera offset
                    self.grid.camera_offset.x = max(0, min((self.grid.total_width - self.grid.grid_width) * self.grid.grid_size, 
                                                         self.grid.camera_offset.x + dx))
                    self.grid.camera_offset.y = max(0, min((self.grid.total_height - self.grid.grid_height) * self.grid.grid_size, 
                                                         self.grid.camera_offset.y + dy))
                    
                    self.last_mouse_pos = current_mouse_pos
                
                # Handle horizontal scroll thumb dragging
                elif self.dragging_h_thumb and self.last_mouse_pos:
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    self.last_mouse_pos = current_mouse_pos
                    
                    # Calculate how far the thumb can move
                    thumb_travel = self.h_scrollbar.width - self.h_scroll_thumb.width
                    if thumb_travel > 0:
                        # Calculate what percentage of the travel we've moved
                        thumb_pos_ratio = (self.h_scroll_thumb.x - self.h_scrollbar.x + dx) / thumb_travel
                        thumb_pos_ratio = max(0, min(1, thumb_pos_ratio))
                        
                        # Apply to camera offset
                        max_h_offset = (self.grid.total_width - self.grid.grid_width) * self.grid.grid_size
                        self.grid.camera_offset.x = thumb_pos_ratio * max_h_offset
                
                # Handle vertical scroll thumb dragging
                elif self.dragging_v_thumb and self.last_mouse_pos:
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]
                    self.last_mouse_pos = current_mouse_pos
                    
                    # Calculate how far the thumb can move
                    thumb_travel = self.v_scrollbar.height - self.v_scroll_thumb.height
                    if thumb_travel > 0:
                        # Calculate what percentage of the travel we've moved
                        thumb_pos_ratio = (self.v_scroll_thumb.y - self.v_scrollbar.y + dy) / thumb_travel
                        thumb_pos_ratio = max(0, min(1, thumb_pos_ratio))
                        
                        # Apply to camera offset
                        max_v_offset = (self.grid.total_height - self.grid.grid_height) * self.grid.grid_size
                        self.grid.camera_offset.y = thumb_pos_ratio * max_v_offset
                
                # Handle dragging to place/remove tiles
                elif self.is_dragging and self.grid.rect.collidepoint(current_mouse_pos):
                    grid_pos = self.grid.get_grid_pos(current_mouse_pos)
                    
                    if grid_pos:
                        if self.is_dragging == "remove":
                            self.grid.remove_tile(grid_pos)
                        else:
                            tile = self.tile_selector.selected_tile
                            self.grid.place_tile(grid_pos, tile["type"], tile["color"])

        return True

    def save_level(self):
        # Create level data
        level_data = {
            "platforms": [],
            "small_platforms": [],
            "hazards": [],
            "bounce_pads": [],
            "checkpoints": [],
            "moving_platforms": [],
            "breakable_blocks": [],
            "player_start": None
        }

        for pos, cell in self.grid.cells.items():
            grid_x, grid_y = pos
            # Convert grid positions to world coordinates
            x = grid_x * self.grid.grid_size
            y = grid_y * self.grid.grid_size

            if cell["type"] == "platform":
                level_data["platforms"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "small_platform":
                level_data["small_platforms"].append({
                    "x": x,
                    "y": y + self.grid.grid_size // 2,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 2
                })
            elif cell["type"] == "hazard":
                level_data["hazards"].append({
                    "x": x,
                    "y": y,
                    "size": self.grid.grid_size
                })
            elif cell["type"] == "bounce":
                level_data["bounce_pads"].append({
                    "x": x,
                    "y": y + 3 * self.grid.grid_size // 4,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 4
                })
            elif cell["type"] == "checkpoint":
                level_data["checkpoints"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "moving_platform":
                level_data["moving_platforms"].append({
                    "x": x,
                    "y": y + self.grid.grid_size // 2,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 2,
                    "move_distance": 120,  # Default movement distance
                    "move_speed": 2  # Default movement speed
                })
            elif cell["type"] == "breakable":
                level_data["breakable_blocks"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "player":
                level_data["player_start"] = {
                    "x": x + self.grid.grid_size // 2,
                    "y": y + self.grid.grid_size
                }

        # Check if player start position exists
        if not level_data["player_start"]:
            print("Warning: No player start position set!")
            return

        # Get filename from user
        filename = self.get_text_input("Enter filename to save:", self.current_filename)
        if not filename:
            return

        # Add .json extension if missing
        if not filename.endswith(".json"):
            filename += ".json"

        self.current_filename = filename

        # Save to file
        filepath = os.path.join(self.level_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(level_data, f)

        print(f"Level saved to {filepath}")

    def load_level(self):
        # List available level files
        levels = [f for f in os.listdir(self.level_dir) if f.endswith(".json")]

        if not levels:
            print("No level files found!")
            return

        print("Available levels:")
        for i, level in enumerate(levels):
            print(f"{i + 1}. {level}")

        # Get filename from user
        selected = self.get_text_input("Enter level number or filename:")
        if not selected:
            return

        # Try to parse as number
        try:
            index = int(selected) - 1
            if 0 <= index < len(levels):
                filename = levels[index]
            else:
                print("Invalid level number!")
                return
        except ValueError:
            # Treat as filename
            filename = selected
            if not filename.endswith(".json"):
                filename += ".json"

            if filename not in levels:
                print(f"Level file '{filename}' not found!")
                return

        self.current_filename = filename

        # Load from file
        filepath = os.path.join(self.level_dir, filename)
        with open(filepath, 'r') as f:
            level_data = json.load(f)

        # Clear grid
        self.grid.clear()

        # Convert coordinates to grid positions and place tiles
        for platform in level_data["platforms"]:
            grid_x = platform["x"] // self.grid.grid_size
            grid_y = platform["y"] // self.grid.grid_size

            self.grid.place_tile((grid_x, grid_y), "platform", GREEN)

        for hazard in level_data["hazards"]:
            grid_x = hazard["x"] // self.grid.grid_size
            grid_y = hazard["y"] // self.grid.grid_size

            self.grid.place_tile((grid_x, grid_y), "hazard", GRAY)

        if level_data["player_start"]:
            start = level_data["player_start"]
            grid_x = (start["x"] - self.grid.grid_size // 2) // self.grid.grid_size
            grid_y = (start["y"] - self.grid.grid_size) // self.grid.grid_size

            self.grid.place_tile((grid_x, grid_y), "player", BLUE)

        print(f"Level loaded from {filepath}")

    def play_level(self):
        # Check if player start position exists
        if not self.grid.player_pos:
            print("Cannot play: No player start position set!")
            return

        # Save level to a temporary file
        temp_level = os.path.join(self.level_dir, "_temp_level.json")
        level_data = {
            "platforms": [],
            "small_platforms": [],
            "hazards": [],
            "bounce_pads": [],
            "checkpoints": [],
            "moving_platforms": [],
            "breakable_blocks": [],
            "player_start": None
        }

        for pos, cell in self.grid.cells.items():
            grid_x, grid_y = pos
            x = self.grid.rect.x + grid_x * self.grid.grid_size
            y = self.grid.rect.y + grid_y * self.grid.grid_size

            if cell["type"] == "platform":
                level_data["platforms"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "small_platform":
                level_data["small_platforms"].append({
                    "x": x,
                    "y": y + self.grid.grid_size // 2,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 2
                })
            elif cell["type"] == "hazard":
                level_data["hazards"].append({
                    "x": x,
                    "y": y,
                    "size": self.grid.grid_size
                })
            elif cell["type"] == "bounce":
                level_data["bounce_pads"].append({
                    "x": x,
                    "y": y + 3 * self.grid.grid_size // 4,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 4
                })
            elif cell["type"] == "checkpoint":
                level_data["checkpoints"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "moving_platform":
                level_data["moving_platforms"].append({
                    "x": x,
                    "y": y + self.grid.grid_size // 2,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size // 2,
                    "move_distance": 120,  # Default movement distance
                    "move_speed": 2,  # Default movement speed
                    "move_axis": "horizontal"  # Default movement axis
                })
            elif cell["type"] == "breakable":
                level_data["breakable_blocks"].append({
                    "x": x,
                    "y": y,
                    "width": self.grid.grid_size,
                    "height": self.grid.grid_size
                })
            elif cell["type"] == "player":
                level_data["player_start"] = {
                    "x": x + self.grid.grid_size // 2,
                    "y": y + self.grid.grid_size
                }

        with open(temp_level, 'w') as f:
            json.dump(level_data, f)

        # Launch the game with the level
        print("Launching game...")
        import subprocess
        try:
            subprocess.Popen(["python", "play_level.py", temp_level])
        except Exception as e:
            print(f"Error launching game: {e}")

    def get_text_input(self, prompt, default_text=""):
        # Setup text input
        input_text = default_text
        input_active = True

        while input_active:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        input_active = False
                    elif event.key == K_ESCAPE:
                        return None
                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            # Draw input box
            screen.fill(BLACK)

            # Prompt text
            prompt_surf = font.render(prompt, True, WHITE)
            screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 60))

            # Input box
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20, 400, 40)
            pygame.draw.rect(screen, WHITE, input_box)

            # Input text
            text_surf = font.render(input_text, True, BLACK)
            screen.blit(text_surf, (input_box.x + 10, input_box.y + 10))

            # Instructions
            instructions = font.render("Press ENTER to confirm, ESC to cancel", True, WHITE)
            screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

            pygame.display.flip()
            clock.tick(FPS)

        return input_text

    def run(self):
        running = True
        while running:
            running = self.handle_input()

            self.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    builder = LevelBuilder()
    builder.run()