import pygame, sys
from button import Button
from first_person import run_game
pygame.init()
from question_maker import Qmaker

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
half_width = SCREEN_WIDTH // 2
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu")

pg = pygame.image.load("assets/Background.png")
BG =pygame.transform.scale(pg, (SCREEN_WIDTH, SCREEN_HEIGHT)) 
def get_font(size): 
    return pygame.font.Font("assets/font.ttf", size)

def show_instructions():
    showing = True
    while showing:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        instructions = [
            "for the platform:",
            "This is the PLAY screen.",
            "Move left and right with the arrow keys",
            "jump with space",
            "for the question answering:",
            "you have a wand and choose an action"
        ]

        start_y = 200  # starting vertical position
        line_spacing = 40  # vertical space between lines

        for i, line in enumerate(instructions):
            line_surf = get_font(20).render(line, True, "White")
            line_rect = line_surf.get_rect(center=(half_width, start_y + i * line_spacing))
            SCREEN.blit(line_surf, line_rect)

        PLAY_BACK = Button(image=None, pos=(1700, 860), 
                            text_input="START", font=get_font(35), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    showing = False  # Leave instruction screen
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    showing = False  # Start game

        pygame.display.update()

def play():
    show_instructions()  # Show instructions first
    result = run_game()  # Run the game
    
    # After game ends (won/lost/quit), return to main menu
    if result == "game_over":
        main_menu()  # Automatically return to main menu
    elif result == "quit":
        pygame.quit()
        sys.exit()
        
def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(half_width, 150))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(half_width, 450), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(half_width, 600), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QMAKER_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(half_width, 750), 
                            text_input="Q.MAKER", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(half_width, 900),
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QMAKER_BUTTON,QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QMAKER_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Qmaker()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()