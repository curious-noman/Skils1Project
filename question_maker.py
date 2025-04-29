
import json
import pygame


pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Question Maker")
font = pygame.font.SysFont("Arial", 24)
def load_questions():
    """Load existing questions from the file (if available)."""
    try:
        with open("questions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # If file doesn't exist, start fresh

def save_questions(questions):
    """Save questions to a file."""
    with open("questions.json", "w") as file:
        json.dump(questions, file, indent=4)

# def add_question():
#     """Allow the teacher to create a new question."""
#     questions = load_questions()

#     question = input("Enter the question: ")
#     answer = input("Enter the correct answer: ")
#     wrong_choice1=  input("Enter the wrong answers (comma separated): ")
#     wrong_choice2=  input("Enter the wrong answers (comma separated): ")
#     wrong_choice3=  input("Enter the wrong answers (comma separated): ")
#     attack_power = int(input("Enter the attack power (1-5): "))

#     # Save new question
#     questions.append({
#         "question": question,
#         "answer": answer.lower(),  
#         "attackPower": attack_power,
#         "wrong_choice1": wrong_choice1,
#         "wrong_choice2": wrong_choice2,
#         "wrong_choice3": wrong_choice3
#     })

    save_questions(questions)
    print("✅ Question added successfully!")

# Run the question maker
# while True:
#     add_question()
#     cont = input("Add another question? (yes/no): ").strip().lower()
#     if cont != "yes":
#         break
class InputBox:
    input_img = pygame.image.load('images/input.png')  # Using your uploaded image

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return False

    def draw(self, screen):
        # Draw the input image
        screen.blit(pygame.transform.scale(self.input_img, (self.rect.width, self.rect.height)), (self.rect.x, self.rect.y))
        
        # Draw the text
        text_surface = font.render(self.text, True, pygame.Color('black'))
        screen.blit(text_surface, (self.rect.x + 30, self.rect.y + 17))


def main():
    question_box = InputBox(700, 200, 700, 90)
    attack_box = InputBox(700, 300, 700, 90)
    answer_box = InputBox(700, 400, 700, 90)
    choice_box1 = InputBox(700, 500, 700, 90)
    choice_box2 = InputBox(700, 600, 700, 90)
    choice_box3 = InputBox(700, 700, 700, 90)
    

    save_image = pygame.image.load('images/save.png')
    
    save_image = pygame.transform.scale(save_image, (120, 50))

    save_button = pygame.Rect(890, 800, 200, 50)

    labels = [
        {"text": "Question:", "position": (700, 170)},
        {"text": "Attack Power (1-5):", "position": (700, 270)},
        {"text": "Correct Answer:", "position": (700, 370)},
        {"text": "Wrong Choice 1:", "position": (700, 470)},
        {"text": "Wrong Choice 2:", "position": (700, 570)},
        {"text": "Wrong Choice 3:", "position": (700, 670)}
    ]

    running = True
    while running:
        screen.fill((103, 99, 201))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  
            question_box.handle_event(event)
            answer_box.handle_event(event)
            attack_box.handle_event(event)
            choice_box1.handle_event(event)
            choice_box2.handle_event(event)
            choice_box3.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos):
                    new_question = {
                        "question": question_box.text,
                        "answer": answer_box.text.lower(),
                        "attackPower": int(attack_box.text),
                        "wrong_choice1": choice_box1.text,
                        "wrong_choice2": choice_box2.text,
                        "wrong_choice3": choice_box3.text
                    }
                    questions = load_questions()
                    questions.append(new_question)
                    save_questions(questions)
                    print("✅ Saved!")
        
        # Draw everything
        # Draw the labels
        for label in labels:
            label_surface = font.render(label["text"], True, pygame.Color('black'))
            screen.blit(label_surface, label["position"])
            
        question_box.draw(screen)
        answer_box.draw(screen)
        attack_box.draw(screen)
        choice_box1.draw(screen)
        choice_box2.draw(screen)
        choice_box3.draw(screen)

        screen.blit(save_image, (save_button.x + 20, save_button.y + 15))
        
        pygame.display.flip()
if __name__ == "__main__":
    main()