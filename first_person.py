import random
import pygame
import sys
import json

def load_questions():
    """Load questions from JSON file."""
    try:
        with open("questions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return [] 

questions_list = load_questions()  
current_question = None 
player_answer = ""  
choices = []
right_answer=None
def ask_question():

    global current_question, message, choices, right_answer 
    if questions_list:
        current_question = random.choice(questions_list)
        message = current_question["question"]
        right_answer = current_question["answer"]  #glooooble vr
        choices = [
            current_question["answer"], 
            current_question["wrong_choice1"],
            current_question["wrong_choice2"],
            current_question["wrong_choice3"]
        ]
        random.shuffle(choices)
    else:
        message = "No questions available!"
        battle_state = "enemy_turn"
        
def check_answer():
    """Check if player's answer is correct before attacking."""
    global battle_state, message, player_answer, right_answer, current_question

    correct = False
    if not player_answer or not current_question:  # Check if we have a question
        return

    # Check multiple choice answers
    if player_answer.upper() in ("A", "B", "C", "D"):
        index = ord(player_answer.upper()) - ord('A')  # A->0, B->1, etc.
        if index < len(choices) and choices[index].lower() == right_answer.lower():
            correct = True
    # Check direct answer
    elif player_answer.lower() == right_answer.lower():
        correct = True
        
    if correct:
        damage = current_question["attackPower"]
        enemy["hp"] -= damage
        message = f"✅ Correct! {player['name']} attacks for {damage} damage!"
        
        if enemy["hp"] <= 0:
            enemy["hp"] = 0
            battle_state = "won"
        else:
            battle_state = "enemy_turn"
    else:
        message = "❌ Wrong answer! No attack this turn."
        battle_state = "enemy_turn"

    player_answer = ""
    current_question = None
    
    
    
pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon-like Battle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


#playeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeers
player = {"name": "clu&blu", "hp": 5, "attack": 1, "defense": 0, "speed": 8}
enemy = {"name": "Ratata", "hp": 3, "attack": 1, "defense": 0, "speed": 6}


battle_state = "player_turn"  # "player_turn", "enemy_turn", "won", "lost"
message = "What will you do?"


#heart img 
heart = pygame.image.load('images/heart.png')
heart_image = pygame.transform.scale(heart, (40, 40)) 
def draw_hearts(x, y, hp):
    for i in range(hp):  
        screen.blit(heart_image, (x + i * 45, y)) 

def ability():
    global message
    message = "do you wanna use an ability" 
    draw_text("No", (70, 920), (200, 200, 200))
    draw_text("Yes", (400, 920), (200, 200, 200))
    
    
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

    draw_text(f"{player['name']}:", (50, 50), (255, 255, 255))
    draw_hearts(150, 40, player["hp"]) 

    draw_text(f"{enemy['name']}: ", (1500, 50), (255, 255, 255))
    draw_hearts(1590, 40, enemy["hp"])

    draw_text(message, (50, 850), (255, 255, 0))

     
    pygame.draw.rect(screen, (0, 0, 100), (50, 900, 700, 150))  
    pygame.draw.rect(screen, (255, 255, 255), (50, 900, 700, 150), 3) 

    # Show typed answer if there's a question
    if current_question:
        draw_text(player_answer, (70, 950), (255, 255, 255))  # Player's input
        
        # Draw multiple choice options
        if 'choices' in globals() and choices:
            draw_text(f"A: {choices[0]}", (70, 920), (200, 200, 200))
            draw_text(f"B: {choices[1]}", (400, 920), (200, 200, 200))
            draw_text(f"C: {choices[2]}", (70, 970), (200, 200, 200))
            draw_text(f"D: {choices[3]}", (400, 970), (200, 200, 200))

    elif battle_state == "player_turn":
        
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

        if event.type == pygame.KEYDOWN:
            if battle_state == "player_turn":
                if event.key == pygame.K_1:  # Attack
                    ability()  # Ask if the player wants to use an ability
                    ask_question()  # Ask a question first
                elif event.key == pygame.K_2:  # Defend
                    player["defense"] += 2  
                    message = f"{player['name']} defends!"
                    battle_state = "enemy_turn"
                
                # Handle answer input
                elif current_question:  # Only if we're answering a question
                    if event.key == pygame.K_RETURN:  # Submit answer
                        check_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        player_answer = player_answer[:-1]
                    elif event.key in (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d):
                        # Convert key to A/B/C/D
                        player_answer = chr(event.key).upper()
                        check_answer()  # Immediately check
                        break
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        # Ignore number keys while answering
                        pass
                    else:
                        # For typing full answers
                        player_answer += event.unicode

            if event.key == pygame.K_ESCAPE:
                running = False  

            elif battle_state in ["won", "lost"] and event.key == pygame.K_SPACE:
                running = False

    
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