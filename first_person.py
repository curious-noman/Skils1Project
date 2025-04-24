import os
import random
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Pokémon-like Battle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Player and enemy stats
# (name, hp, attack, defense, speed)
player = {"name": "player", "hp": 5, "attack": 1, "defense": 0, "speed": 8}
enemy = {"name": "Ratata", "hp": 3, "attack": 1, "defense": 0, "speed": 6}

# Battle state
battle_state = "player_turn"  # "player_turn", "enemy_turn", "won", "lost"
message = "What will you do?"


#heart img 
heart = pygame.image.load('images/heart.png')
heart_image = pygame.transform.scale(heart, (40, 40)) 
def draw_hearts(x, y, hp):
    for i in range(hp):  
        screen.blit(heart_image, (x + i * 45, y)) 


def player_attack():
    global battle_state, message
    
    answer1 =random
    damage = max(1, player["attack"] - enemy["defense"] // 2)
    enemy["hp"] -= damage
    message = f"{player['name']} attacks for {damage} damage!"
    if enemy["hp"] <= 0:
        enemy["hp"] = 0
        battle_state = "won"
    else:
        battle_state = "enemy_turn"

def enemy_turn():
    global battle_state, message
    damage = max(1, enemy["attack"] - player["defense"] // 2)
    player["hp"] -= damage
    message = f"{enemy['name']} attacks for {damage} damage!"
    if player["hp"] <= 0:
        player["hp"] = 0
        battle_state = "lost"
    else:
        battle_state = "player_turn"

def draw_battle():
    screen.fill((0, 0, 50))  # Dark blue background
    
    # Draw player and enemy stats
    draw_text(f"{player['name']}:", (50, 50), (255, 255, 255))
    draw_hearts(150, 40, player["hp"]) 
    
    draw_text(f"{enemy['name']}: ", (1500, 50), (255, 255, 255))
    draw_hearts(1590, 40, enemy["hp"])

    # player turn message (M.Q.)
    draw_text(message, (50, 850), (255, 255, 0))
    
    pygame.draw.rect(screen, (255, 255, 255), (50, 900, 500, 150), 3)  # Out
    pygame.draw.rect(screen, (0, 0, 100), (50, 900, 500, 150))  

 
    
    if battle_state == "player_turn":
        draw_text("[1] Attack                    [2] Defend", (70, 920), (200, 200, 200))
    elif battle_state in ["won", "lost"]:
        draw_text("Press SPACE to continue...", (50, 920), (200, 200, 200))

def draw_text(text, pos, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)
    
    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Player input
        if event.type == pygame.KEYDOWN:
            if battle_state == "player_turn":
                if event.key == pygame.K_1:  # Attack
                    player_attack()
                elif event.key == pygame.K_2:  # Defend (example: reduce damage)
                    player["defense"] += 2  # Temporary boost
                    message = f"{player['name']} defends!"
                    battle_state = "enemy_turn"
              
            if event.key == pygame.K_q:
                running = False # If Q is pressed
                print("Q was pressed!")

            
            elif battle_state in ["won", "lost"]:
                if event.key == pygame.K_SPACE:
                    running = False  # Exit 

    
    # Enemy t
    if battle_state == "enemy_turn":
        if  player["defense"] > 0:
            player["defense"] = 0
        pygame.time.delay(1000)  
        enemy_turn()
    
    draw_battle()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()