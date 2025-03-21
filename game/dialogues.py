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
    def __init__(self, name, lines, quest_stage_advance=None, money_given=0, story_mode=False, story_lines=None):
        self.name = name
        self.lines = lines
        self.current_line = 0
        self.quest_stage_advance = quest_stage_advance  # What quest stage to advance to
        self.money_given = money_given
        self.has_given_money = False
        self.story_mode = story_mode
        self.story_lines = story_lines if story_mode else []

    def next_line(self):
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.current_line = 0
            return None
        return self.lines[self.current_line]

    def reset(self):
        self.current_line = 0

class Cutscene:
    def __init__(self, sentences, images):
        self.sentences = sentences
        self.images = images

cutscenes = {
    "intro": Cutscene(
        sentences=[
            "It is the morning of October 16th in the year of our Lord 1833. A most terrible and violent storm the night prior has left the mighty Chain Pier in a ruinous state.",
            "The second bridge is hanging down almost touching the sea.",
            "Only the ropes of the third bridge remain.",
            "Work to repair it must be commenced as soon as possible, for without the Pier there would be no way to dock ships!"
        ],
        images=[
            'game/img/cutscene_image_1.png',  # Image _1
            'game/img/cutscene_image_2.png',  # Image _2
            'game/img/cutscene_image_3.png',  # Image _3
            None  # Black screen
        ]
    )
}


# Example dialogues with quest stage advancement and money
dialogues = {
    "donor1": Dialogue("Donor 1", ["Oh no, the pier is broken!", "I can give you 5 gold to help fix it.", "Good luck!"], quest_stage_advance="talked_to_donor1", money_given=5),
    "donor2": Dialogue("Donor 2", ["I heard about the pier.", "Here's 10 gold to help.", "I hope it gets fixed soon!"], quest_stage_advance="talked_to_donor2", money_given=10),
    "donor3": Dialogue("Donor 3", ["The pier is in bad shape.", "I can spare 2 gold.", "Be careful out there!"], quest_stage_advance="talked_to_donor3", money_given=2),
    "donor1_done": Dialogue("Donor 1", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
    "donor2_done": Dialogue("Donor 2", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
    "donor3_done": Dialogue("Donor 3", ["Thanks for helping with the pier!", "I have no more money to give."], money_given=0),
    "story_teller": Dialogue("Story Teller", ["This is the start of a story!"], story_mode=True, story_lines=["This is the first line of the story.", "This is the second line.", "This is the third line."]),
    "pierkeeper": Dialogue("Pierkeeper", [
        "Oh, the Chain Pier! What a terrible sight after last night's storm.",
        "The second bridge is hanging precariously, and the third is gone entirely!",
        "We need to gather funds to repair it. Can you help?",
        "Speak to the donors, they may be able to spare some gold."
    ], quest_stage_advance="talked_to_pierkeeper"),
    "pierkeeper_done": Dialogue("Pierkeeper", ["Thank you for helping to repair the pier!", "I have no more to say."], money_given=0),
    "rude_npc": Dialogue("RudeNPC", ["Go away! I don't have time for you.", "Leave me alone!"]),
}