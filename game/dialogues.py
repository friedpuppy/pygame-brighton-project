import pygame
from config import *
from sprites import *

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """
    Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapped as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect object that the text will be drawn into.
    text_color - a color tuple (ex (255, 0, 0) for red)
    background_color - a color tuple (ex (0, 0, 0) for black)
    justification - 0 (default) left-justified
                    1 centered
                    2 right-justified

    Returns
        Surface object with the text drawn onto it.
    """

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException(
                        "The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException("Invalid justification argument: " + str(justification))
        accumulated_height += font.size(line)[1]

    return surface

class DialogueBox(pygame.sprite.Sprite):
    def __init__(self, game, text, x, y, width=600, height=200, font_size=30):
        super().__init__()
        self.game = game
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font('monofonto rg.otf', font_size)
        self.color = (255, 255, 255)  # White
        self.background_color = (0, 0, 0)  # Black
        self.border_color = (100, 100, 100)  # Dark Gray
        self.border_width = 2
        self.padding = 10
        self.active = False
        self.create_surface()
        self.rect.x = x
        self.rect.y = y
        self.text_surface = None
        self.text_rect = None
        #self.create_text_surface() #removed this line

    def create_surface(self):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()

    def create_text_surface(self):
        text_rect = pygame.Rect(0, 0, self.width - (self.padding * 2), self.height - (self.padding * 2)) #changed this line
        try:
            self.text_surface = render_textrect(self.text, self.font, text_rect, self.color, self.background_color, 0) #changed this line
            self.text_rect = self.text_surface.get_rect(topleft=(self.padding, self.padding)) #changed this line
        except TextRectException as e:
            print(f"Error rendering text: {e}")
            self.text_surface = self.font.render("Error: Text too long", True, self.color)
            self.text_rect = self.text_surface.get_rect(topleft=(self.padding, self.padding))

    def draw(self):
        if self.active:
            pygame.draw.rect(self.game.screen, self.background_color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(self.game.screen, self.border_color, (self.x, self.y, self.width, self.height), self.border_width)
            self.game.screen.blit(self.text_surface, self.text_rect.topleft) #changed this line

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
    "door_1_npc": Dialogue("Door1NPC", ["Hello! I live here."]),
    "donor1": Dialogue("Donor 1", ["Oh no, the pier is broken!", "I really hope this money helps.", "Good luck!"], quest_stage_advance="talked_to_donor1", money_given=5),
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
        "Speak to the townsfolk, they may be able to pledge monetary support."
    ], quest_stage_advance="talked_to_pierkeeper"),
    "pierkeeper_intro": Dialogue("Pierkeeper", ["Hello there, I need to talk to you about the pier."], quest_stage_advance="talked_to_pierkeeper"), #added this line
    "pierkeeper_done": Dialogue("Pierkeeper", ["Thank you for helping to repair the pier!", "I have no more to say."], money_given=0),
    "rude_npc": Dialogue("RudeNPC", ["Go away! I don't have time for you.", "Leave me alone!"]),
}
