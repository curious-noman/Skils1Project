import random
import pygame
import sys
import json
import time
from BluetoothV2.game_controller import GameController

def load_questions():
    """Load questions from JSON file."""
    try:
        with open("questions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return [] 

def load_enemies():

    """Load questions from JSON file."""
    try:
        with open("charecter.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return [] 

#veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeriables

Q_time = 45
time_remaining = 0
timer_active = False
timer_start = 0

questions_list = load_questions()
charecter_list = load_enemies()

charecter_list=charecter_list[random.randint(0, len(charecter_list)-1)]

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
        "Heal": {"uses": 1, "effect": "heal", "amount": 2},
        "Fireball": {"uses": 2, "effect": "damage", "amount": 3},
        "Spear": {"uses": 1, "effect": "defense", "amount": 2}
    }
player = {
    "name": "clu&blu", 
    "hp": 5, 
    "attack": 1, 
    "defense": 0, 
    "speed": 8,
    "abilities": abilities
}
enemy = {"name": charecter_list["name"], "hp":charecter_list["hp"],
         "attack": charecter_list["attack"], "defense": charecter_list["defense"], "speed": charecter_list["speed"]}
print("enemy", enemy)
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


def start_timer():
    global timer_active, timer_start, time_remaining
    timer_active = True
    timer_start = pygame.time.get_ticks()
    time_remaining = Q_time
    
def update_timer():
    global time_remaining, timer_active, battle_state
    if timer_active:
        elapsed = (pygame.time.get_ticks() - timer_start) // 1000
        time_remaining = max(0, Q_time - elapsed)
        if time_remaining <= 0:
            timer_active = False
            # Handle time running out - treat as wrong answer
            if battle_state == "player_turn" and current_question:
                global message
                message = "Time's up! No attack this turn!"
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
        self.is_selected = False  # For controller navigation
        
    def draw(self, screen):
        # Use hover color if hovered by mouse or selected by controller
        color = self.hover_color if (self.is_hovered or self.is_selected) else self.color
        pygame.draw.rect(screen, color, self.rect)
        # Draw a thicker border if selected by controller
        border_width = 4 if self.is_selected else 2
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_width)
        
        text_surface = medium_font.render(self.text, True, (255, 255, 255))
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

def continue_battle():
    global battle_state
    if enemy["hp"] <= 0:
        battle_state = "won"
    else:
        battle_state = "player_turn" if correct else "enemy_turn"
    create_buttons()

    
def create_buttons():
    global buttons, selected_button_index
    buttons = []
    selected_button_index = 0  # Reset selected button index when creating new buttons
    
    if battle_state == "showing_explanation":
        buttons.append(Button(SCREEN_WIDTH//2 - 150, 950, 300, 50, "Continue", continue_battle))
    elif battle_state == "player_turn":
        if current_question:
    
            if choices:
                buttons.append(Button(80, 920, 300, 50, f"A: {choices[0]}", lambda: select_answer(0)))
                buttons.append(Button(430, 920, 300, 50, f"B: {choices[1]}", lambda: select_answer(1)))
                buttons.append(Button(80, 980, 300, 50, f"C: {choices[2]}", lambda: select_answer(2)))
                buttons.append(Button(430, 980, 300, 50, f"D: {choices[3]}", lambda: select_answer(3)))
                
        elif  show_abilities_condetion:
            if abilities:
                # Ability buttons grid layout
                start_x = 80
                start_y = 890
                button_width = 300
                button_height = 50
                horizontal_spacing = 50
                vertical_spacing = 60
                max_per_row = 2
                
                row, col = 0, 0
                for ability, details in player["abilities"].items():
                    if details["uses"] > 0:
                        x = start_x + col * (button_width + horizontal_spacing)
                        y = start_y + row * vertical_spacing
                        buttons.append(Button(
                            x, y, button_width, button_height,
                            f"{ability} ({details['uses']})", 
                            lambda a=ability: use_ability(a)
                        ))
                        col += 1
                        if col >= max_per_row:
                            col = 0
                            row += 1
                
                # Position Back button below the ability grid
                back_button_y = start_y + (row + 1) * vertical_spacing -60
                buttons.append(Button(
                    430, back_button_y, 300, 50, "Back", show_abilities
            ))
            
        else:
            # Normal action buttons
            buttons.append(Button(80, 920, 300, 50, "Attack", player_attack_init))
            buttons.append(Button(430, 920, 300, 50, "Abilities", show_abilities))
                    

        
        
        
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
        start_timer() 
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
    global battle_state, message, player_answer, right_answer, current_question, showing_explanation

    correct = False
    if not player_answer or not current_question:
        return

    # Check multiple choice answers
    if player_answer.upper() in ("A", "B", "C", "D"):
        index = ord(player_answer.upper()) - ord('A')
        if index < len(choices) and choices[index].lower() == right_answer.lower():
            correct = True
    elif player_answer.lower() == right_answer.lower():
        correct = True
        
    if correct:
        damage = current_question["attackPower"]
        enemy["hp"] -= damage
        message = f"Correct! {player['name']} attacks for {damage} damage!\n\nExplanation: {current_question.get('explanation', 'No explanation available.')}"
        start_shake(5, 1.2)
    else:
        message = f"Wrong answer! No attack this turn.\n\nExplanation: {current_question.get('explanation', 'No explanation available.')}"
    
    # Set state to show explanation
    battle_state = "showing_explanation"
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


#fooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooont


try:
    small_font = pygame.font.Font('fonts/Pokemon-Classic.ttf', 16)
    medium_font = pygame.font.Font('fonts/Pokemon-Classic.ttf', 24)
    large_font = pygame.font.Font('fonts/Pokemon-Classic.ttf', 32)
except:
    font = pygame.font.SysFont('arial', 24)
    

    
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
    heart_image = pygame.transform.scale(heart, (60, 60)) 
except:
    heart_image = pygame.Surface((40, 40))
    heart_image.fill((255, 0, 0))
    
try:
    oponent = pygame.image.load(charecter_list['image'])
    oponent_image = pygame.transform.scale(oponent, (400, 390)) 
except:
    # placeholder 
    oponent_image = pygame.Surface((160, 240))
    oponent_image.fill((150, 150, 150))

BP = pygame.image.load('images/background_wild_westF.png')
BP_image = pygame.transform.scale(BP, (SCREEN_WIDTH, SCREEN_HEIGHT)) 

Wand= pygame.image.load('images/maic_wand.png')
wand_image = pygame.transform.scale(Wand, (530, 530)) 
box= pygame.image.load('images/box.png')
box_image = pygame.transform.scale(box, (750, 240)) 

small_box= pygame.image.load('images/box.png')
small_box_image = pygame.transform.scale(small_box, (170, 70))



def draw_hearts(x, y, hp):
    for i in range(hp):  
        screen.blit(heart_image, (x + i * 65, y)) 
        
        
def draw_battle():
    screen.blit(BP_image, (0, 0)) 
        # Draw action box
    screen.blit(box_image, (30, 820))
    screen.blit(small_box_image, (930, 30))

    wand_x, wand_y = wand_position
    if is_wand_shaking:
        wand_x += random.randint(-15, 15)
        wand_y += random.randint(-15, 15)
    screen.blit(wand_image, (wand_x, wand_y))

    draw_text(f"{player['name']}:", (50, 50), (255, 255, 255), medium_font)
    draw_hearts(250, 40, player["hp"]) 

    draw_text(f"{enemy['name']}: ", (1510-len(enemy['name'])*6, 50), (255, 255, 255), medium_font)
    draw_hearts(1690, 40, enemy["hp"])

    # Draw message
    draw_text(message, (50, 850), (100, 0, 255), medium_font)
    
    if current_question and timer_active:
        timer_text = f"Time: {time_remaining}s"
        draw_text(timer_text, (SCREEN_WIDTH/2, 50), (155, 55, 255), small_font)
        
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
     

    
    # Draw buttons
    for button in buttons:
        button.draw(screen)

def draw_text(text, pos, color=(255, 255, 255), font_obj=None):
    """Draw text with optional custom font, supports multi-line text"""
    if font_obj is None:
        font_obj = medium_font
        
    # Split text into lines
    lines = text.split('\n')
    x, y = pos
    
    for line in lines:
        if line:  # Only render non-empty lines
            text_surface = font_obj.render(line, False, color)
            screen.blit(text_surface, (x, y))
        y += font_obj.get_height() + 5 

# Initial button setup
create_buttons()

# Main game loop
def run_game(create_new_controller=True):
    global screen, clock, battle_state, message, current_question, choices, right_answer, running, bt_controller, selected_button_index
    
    # Initialize Bluetooth controller only if we need to create a new one
    if create_new_controller:
        bt_controller = GameController(debug=True)
        bt_controller.start()
        
        # Wait a moment for Bluetooth to initialize
        time.sleep(1)
    
    running = True
    battle_state = "player_turn"
    message = "What will you do?"
    current_question = None
    selected_button_index = 0  # Track which button is selected by controller
    
    # Reset player and enemy stats
    player = {
    "name": "clu&blu", 
    "hp": 5, 
    "attack": 1, 
    "defense": 0, 
    "speed": 8,
    "abilities": {
        "Heal": {"uses": 2, "effect": "heal", "amount": 2},
        "Double Damege": {"uses": 3, "effect": "damage", "amount": 3},
        "Shield": {"uses": 1, "effect": "defense", "amount": 2}
    }
}
    enemy = {"name": charecter_list["name"], "hp":charecter_list["hp"],
         "attack": charecter_list["attack"], "defense": charecter_list["defense"], "speed": charecter_list["speed"]}
    
    create_buttons()
    
    # Main game loop
    last_time = pygame.time.get_ticks()
    controller_cooldown = 0  # Cooldown for controller input to prevent rapid navigation
    controller_cooldown_time = 0.2  # Seconds between controller inputs
    
    while running:
        screen.blit(BP_image, (0, 0)) 
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0  # Delta time in seconds
        last_time = current_time
        
        update_animations(dt)
        update_timer() 
        mouse_pos = pygame.mouse.get_pos()
        
        # Update controller cooldown
        if controller_cooldown > 0:
            controller_cooldown -= dt
        
        # Handle Bluetooth controller input
        if bt_controller.is_connected() and controller_cooldown <= 0:
            controller_state = bt_controller.update()
            
            # Reset all button selections first
            for button in buttons:
                button.is_selected = False
            
            # Navigate between buttons with X-axis controller
            if len(buttons) > 0:
                # Handle horizontal navigation (left/right)
                if controller_state['moving_left']:
                    selected_button_index = (selected_button_index - 1) % len(buttons)
                    controller_cooldown = controller_cooldown_time
                elif controller_state['moving_right']:
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                    controller_cooldown = controller_cooldown_time
                
                # Select the current button
                if 0 <= selected_button_index < len(buttons):
                    buttons[selected_button_index].is_selected = True
                
                # Activate button with Y controller jump or button press
                if controller_state['jumping'] or controller_state['button_pressed']:
                    if 0 <= selected_button_index < len(buttons) and buttons[selected_button_index].action:
                        buttons[selected_button_index].action()
                        controller_cooldown = controller_cooldown_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle button hover with mouse (still keep mouse functionality)
            for button in buttons:
                button.check_hover(mouse_pos)
                
            # Handle button clicks with mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.handle_event(event):
                        break
            if battle_state == "showing_explanation":
                # Wait for player to press continue
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        if enemy["hp"] <= 0:
                            battle_state = "won"
                        else:
                            battle_state = "player_turn" if correct else "enemy_turn"
                        create_buttons()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
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

    # Clean up Bluetooth controller before exiting, but only if we created it
    if create_new_controller:
        bt_controller.stop()

# Function to run the game with an existing controller (called from platformer)
def run_game_with_controller(existing_controller):
    global bt_controller
    # Use the existing controller instead of creating a new one
    bt_controller = existing_controller
    run_game(create_new_controller=False)
    # Don't stop the controller when exiting, as it's still needed by the platformer

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