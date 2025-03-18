# dialogues.py
import pygame

class DialogueBox:
    # ... (DialogueBox class remains the same) ...
    def __init__(self, game, text, x, y, width=600, height=200, font_size=30): #changed this line
        self.game = game
        self.text = text
        self.x = x
        self.y = y
        self.width = width #changed this line
        self.height = height #changed this line
        self.font = pygame.font.Font('monofonto rg.otf', font_size)
        self.color = (255, 255, 255)  # White
        self.background_color = (0, 0, 0)  # Black
        self.border_color = (100, 100, 100)  # Dark Gray
        self.border_width = 2
        self.padding = 10
        self.active = False
        self.text_surface = None
        self.text_rect = None
        self.create_text_surface()

    def create_text_surface(self):
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect(topleft=(self.x + self.padding, self.y + self.padding))

    def draw(self):
        if self.active:
            pygame.draw.rect(self.game.screen, self.background_color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(self.game.screen, self.border_color, (self.x, self.y, self.width, self.height), self.border_width)
            self.game.screen.blit(self.text_surface, self.text_rect)

    def toggle(self):
        self.active = not self.active

class Dialogue:
    # ... (Dialogue class remains the same) ...
    def __init__(self, name, lines, quest_stage_advance=None, money_given=0):
        self.name = name
        self.lines = lines
        self.current_line = 0
        self.quest_stage_advance = quest_stage_advance  # What quest stage to advance to
        self.money_given = money_given
        self.has_given_money = False

    def next_line(self):
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.current_line = 0
            return None
        return self.lines[self.current_line]

    def reset(self):
        self.current_line = 0

# Example dialogues with quest stage advancement and money
dialogues = {
    "villager1": Dialogue("Villager 1", ["Oh no, the pier is broken!", "I can give you 5 gold to help fix it.", "Good luck!"], quest_stage_advance="talked_to_villager1", money_given=5),
    "villager2": Dialogue("Villager 2", ["I heard about the pier.", "Here's 10 gold to help.", "I hope it gets fixed soon!"], quest_stage_advance="talked_to_villager2", money_given=10),
    "guard1": Dialogue("Guard 1", ["The pier is in bad shape.", "I can spare 2 gold.", "Be careful out there!"], quest_stage_advance="talked_to_guard1", money_given=2),
    "villager1_done": Dialogue("Villager 1", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
    "villager2_done": Dialogue("Villager 2", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
    "guard1_done": Dialogue("Guard 1", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
}
