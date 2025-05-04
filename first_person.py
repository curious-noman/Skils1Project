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


#veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeriables

Q_time = 45
questions_list = load_questions()  
current_question = None 
player_answer = ""  
choices = []
right_answer = None
buttons = []  
show_abilities_condetion = False

is_shaking = False  
shake_duration = 0
shake_intensity = 0
enemy_position = (1100, 370) 

is_wand_shaking = False
wand_shake_duration = 0
wand_shake_intensity = 0
wand_position = (1300, 650)

 
abilities={
        "Heal": {"uses": 2, "effect": "heal", "amount": 2},
        "Fireball": {"uses": 3, "effect": "damage", "amount": 3},
        "Shield": {"uses": 1, "effect": "defense", "amount": 2}
    }
player = {
    "name": "clu&blu", 
    "hp": 5, 
    "attack": 1, 
    "defense": 0, 
    "speed": 8,
    "abilities": abilities
}
enemy = {"name": "Ratata", "hp": 3, "attack": 1, "defense": 0, "speed": 6}

def update_animations(dt):
    global is_shaking, shake_intensity, shake_duration
    global is_wand_shaking, wand_shake_duration, battle_state
    
    if is_wand_shaking:
        wand_shake_duration -= dt
        if wand_shake_duration <= 0:
            is_wand_shaking = False
            
            is_shaking = True
            shake_duration = 1.1  
    
    if is_shaking:
        shake_duration -= dt
        if shake_duration <= 0:
            is_shaking = False
            
            battle_state = "enemy_turn"
            create_buttons()



class Button:
    def __init__(self, x, y, width, height, text, action=None, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()
            return True
        return False



def create_buttons():
    global buttons
    buttons = []
    
    if battle_state == "player_turn":
        if current_question:
    
            if choices:
                buttons.append(Button(50, 920, 300, 50, f"A: {choices[0]}", lambda: select_answer(0)))
                buttons.append(Button(400, 920, 300, 50, f"B: {choices[1]}", lambda: select_answer(1)))
                buttons.append(Button(50, 980, 300, 50, f"C: {choices[2]}", lambda: select_answer(2)))
                buttons.append(Button(400, 980, 300, 50, f"D: {choices[3]}", lambda: select_answer(3)))
                
        elif  show_abilities_condetion:
            if abilities:
                y_pos = 920  
                for ability, details in player["abilities"].items():
                    if details["uses"] > 0:
                        buttons.append(Button(50, y_pos, 300, 50, 
                                           f"{ability} ({details['uses']})", 
                                           lambda a=ability: use_ability(a)))
                        y_pos += 60
                
                buttons.append(Button(400, 920, 300, 50, "Back", show_abilities))
        else:
                # Show normal action buttons when abilities panel is closed
            buttons.append(Button(50, 920, 300, 50, "Attack", player_attack_init))
            buttons.append(Button(400, 920, 300, 50, "Abilities", show_abilities))
                
    elif battle_state in ["won", "lost"]:
        buttons.append(Button(50, 920, 300, 50, "Continue", end_battle))
        
        
        
def use_ability(ability_name):
    global battle_state, message, show_abilities_condetion, is_wand_shaking, wand_shake_duration
    
    
    if ability_name in player["abilities"] and player["abilities"][ability_name]["uses"] > 0:
        # Start wand shaking
        is_wand_shaking = True
        wand_shake_duration = 1.1  
        
        ability = player["abilities"][ability_name]
        ability["uses"] -= 1
        
        if ability["effect"] == "heal":
            player["hp"] += ability["amount"]
            message = f"{player['name']} used {ability_name}! Healed {ability['amount']} HP!"
        elif ability["effect"] == "damage":
            enemy["hp"] -= ability["amount"]
            message = f"{player['name']} used {ability_name}! Dealt {ability['amount']} damage!"
        elif ability["effect"] == "defense":
            player["defense"] += ability["amount"]
            message = f"{player['name']} used {ability_name}! Defense increased by {ability['amount']}!"
        
        show_abilities_condetion = False
        create_buttons()

def select_answer(index):
    global player_answer
    if 0 <= index < len(choices):
        player_answer = chr(ord('A') + index)
        check_answer()

def player_attack_init():
    global current_question, message
    ask_question()
    create_buttons()  # Recreate buttons for answer selection

def player_defend():
    global battle_state, message
    player["defense"] += 2  # Increase defense
    message = f"{player['name']} defends! Defense increased by 2!"
    battle_state = "enemy_turn"
    create_buttons()

def end_battle():
    global running
    running = False

def ask_question():
    global current_question, message, choices, right_answer 
    if questions_list:
        current_question = random.choice(questions_list)
        message = current_question["question"]
        right_answer = current_question["answer"]
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
    create_buttons()
    
def show_abilities():
    global show_abilities_condetion
    show_abilities_condetion = not show_abilities_condetion 
    print("show_abilities", show_abilities) 
    create_buttons()
def start_shake(intensity, duration):
    global is_shaking, shake_intensity, shake_duration
    is_shaking = True
    shake_intensity = intensity
    shake_duration = duration
        
def check_answer():
    """Check if player's answer is correct before attacking."""
    global battle_state, message, player_answer, right_answer, current_question

    correct = False
    if not player_answer or not current_question:
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
        start_shake(5,  1.2)  # intensity=5, duration=0.3 seconds

    
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
    create_buttons()

    
def player_attack():
    global battle_state, message
    damage = max(1, player["attack"] - enemy["defense"] // 2)
    enemy["hp"] -= damage
    message = f"{player['name']} attacks for {damage} damage!"
    if enemy["hp"] <= 0:
        enemy["hp"] = 0
        battle_state = "won"
    else:
        battle_state = "enemy_turn"
    create_buttons()

def enemy_turn():
    global battle_state, message
    damage = max(1, enemy["attack"] - player["defense"])
    player["hp"] -= damage
    player["defense"] = 0  # Reset defense after each turn
    message = f"{enemy['name']} attacks for {damage} damage!"

    if player["hp"] <= 0:
        player["hp"] = 0
        battle_state = "lost"
    else:
        battle_state = "player_turn"
        
    create_buttons()

# Initialize pygame
pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon-like Battle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Player and enemy data


battle_state = "player_turn"  # "player_turn", "enemy_turn", "won", "lost"
message = "What will you do?"

# Load images
try:
    heart = pygame.image.load('images/heart.png')
    heart_image = pygame.transform.scale(heart, (40, 40)) 
except:
    heart_image = pygame.Surface((40, 40))
    heart_image.fill((255, 0, 0))
    
try:
    oponent = pygame.image.load('images/try_oponent.png')
    oponent_image = pygame.transform.scale(oponent, (160, 240)) 
except:
    # placeholder 
    oponent_image = pygame.Surface((160, 240))
    oponent_image.fill((150, 150, 150))

BP = pygame.image.load('images/background_wild_westF.png')
BP_image = pygame.transform.scale(BP, (SCREEN_WIDTH, SCREEN_HEIGHT)) 

Wand= pygame.image.load('images/maic_wand.png')
wand_image = pygame.transform.scale(Wand, (530, 530)) 



def draw_hearts(x, y, hp):
    for i in range(hp):  
        screen.blit(heart_image, (x + i * 45, y)) 
        
        
def draw_battle():
    screen.blit(BP_image, (0, 0)) 

    wand_x, wand_y = wand_position
    if is_wand_shaking:
        wand_x += random.randint(-15, 15)
        wand_y += random.randint(-15, 15)
    screen.blit(wand_image, (wand_x, wand_y))

    draw_text(f"{player['name']}:", (50, 50), (255, 255, 255))
    draw_hearts(150, 40, player["hp"]) 

    draw_text(f"{enemy['name']}: ", (1500, 50), (255, 255, 255))
    draw_hearts(1590, 40, enemy["hp"])

    # Draw message
    draw_text(message, (50, 850), (255, 255, 0))
    
    # Draw enemy
    draw_x, draw_y = enemy_position
    if is_shaking:
        draw_x += random.randint(-shake_intensity, shake_intensity)
        draw_y += random.randint(-shake_intensity, shake_intensity)
        flash = pygame.Surface(oponent_image.get_size(), pygame.SRCALPHA)
        flash.fill((255, 0, 0, 50))  
        screen.blit(oponent_image, (draw_x, draw_y))
        screen.blit(flash, (draw_x, draw_y))
    else:
        screen.blit(oponent_image, (draw_x, draw_y))
     
    # Draw action box
    pygame.draw.rect(screen, (0, 0, 100), (50, 900, 700, 150))  
    pygame.draw.rect(screen, (255, 255, 255), (50, 900, 700, 150), 3) 
    
    # Draw buttons
    for button in buttons:
        button.draw(screen)

def draw_text(text, pos, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

# Initial button setup
create_buttons()

# Main game loop
def run_game():
    # Initialize game state
    global running, battle_state, message, player, enemy
    running = True
    battle_state = "player_turn"
    message = "What will you do?"
    
    # Reset player and enemy stats
    player = {
    "name": "clu&blu", 
    "hp": 5, 
    "attack": 1, 
    "defense": 0, 
    "speed": 8,
    "abilities": {
        "Heal": {"uses": 2, "effect": "heal", "amount": 2},
        "Fireball": {"uses": 3, "effect": "damage", "amount": 3},
        "Shield": {"uses": 1, "effect": "defense", "amount": 2}
    }
}
    enemy = {"name": "Ratata", "hp": 3, "attack": 1, "defense": 0, "speed": 6}
    
    create_buttons()
    
    # Main game loop
    last_time = pygame.time.get_ticks()
    while running:
        screen.blit(BP_image, (0, 0)) 
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0  # Delta time in seconds
        last_time = current_time
        
        update_animations(dt)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle button hover
            for button in buttons:
                button.check_hover(mouse_pos)
                
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.handle_event(event):
                        break
            
            # Keyboard handling (keeps original functionality)
            if event.type == pygame.KEYDOWN:
                if battle_state == "player_turn":
                    if event.key == pygame.K_1:  # Attack
                        player_attack_init()
                    elif event.key == pygame.K_2:  # Defend
                        player_defend()
                    elif current_question:  # Only if answering a question
                        if event.key == pygame.K_RETURN:  # Submit answer
                            check_answer()
                        elif event.key == pygame.K_BACKSPACE:
                            player_answer = player_answer[:-1]
                        elif event.key in (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d):
                            player_answer = chr(event.key).upper()
                            check_answer()
                        elif event.key not in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                            player_answer += event.unicode

                if event.key == pygame.K_ESCAPE:
                    running = False  
                elif battle_state in ["won", "lost"] and event.key == pygame.K_SPACE:
                    running = False

        # Enemy turn
        if battle_state == "enemy_turn":
            if player["defense"] > 0:
                player["defense"] = 0
            pygame.time.delay(1000)  
            enemy_turn()
        
        draw_battle()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    # Only run if executed directly (not when imported)
    pygame.init()
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  
    font = pygame.font.Font(None, 36)
    run_game()
    pygame.quit()
    sys.exit()