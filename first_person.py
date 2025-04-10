import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

player_x, player_y = 100, 100  # Player position
player_angle = 0  # Looking direction (radians)

# Simple 2D grid map (1 = wall, 0 = empty)
game_map = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
]

def cast_rays():
    ray_count = 120
    for ray in range(ray_count):
        ray_angle = (player_angle - math.pi / 6) + (ray / ray_count) * (math.pi / 3)
        
        # Check distance to wall
        distance = 0
        hit_wall = False
        while not hit_wall and distance < 20:
            distance += 0.1
            test_x = int(player_x + distance * math.cos(ray_angle))
            test_y = int(player_y + distance * math.sin(ray_angle))
            
            if test_x < 0 or test_x >= len(game_map[0]) or test_y < 0 or test_y >= len(game_map):
                hit_wall = True
            elif game_map[test_y][test_x] == 1:
                hit_wall = True
        
        # Draw walls (shorter walls = farther away)
        wall_height = min(int(10000 / (distance + 0.0001)), 600)
        pygame.draw.rect(screen, (255, 255, 255), 
                         (ray * (800 // ray_count), 300 - wall_height // 2, 
                          800 // ray_count, wall_height))
        
        
running = True
while running:
    # screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_angle -= 0.1
    if keys[pygame.K_RIGHT]:
        player_angle += 0.1
    if keys[pygame.K_w]:
        player_x += math.cos(player_angle) * 2
        player_y += math.sin(player_angle) * 2
    
    cast_rays()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
        
        
        
        
        