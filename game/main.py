import pygame
from sprites import *
from config import *
from dialogues import *
import sys
from pytmx.util_pygame import load_pygame
import pyscroll
import pyscroll.data
import random

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("A Pier to the Past")  # Set window title
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('monofonto rg.otf', 32)
        self.running = True
        self.game_started = False

        self.character_spritesheet = Spritesheet('game/img/character.png')
        self.terrain_spritesheet = Spritesheet('game/img/terrain.png')
        self.enemy_spritesheet = Spritesheet('game/img/enemy.png')
        self.npc_sprite = self.enemy_spritesheet.get_sprite(3, 2, TILESIZE, TILESIZE)

        self.intro_background = pygame.image.load('game/img/BPC00100.jpg')

        self.player = None
        self.npcs = pygame.sprite.Group()
        self.dialogues = dialogues
        self.cutscenes = cutscenes
        self.dialogue_box = DialogueBox(self, "", 50, 550)
        self.money = 0
        self.quest_log = {}
        self.create_quests()
        self.collision_objects = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.has_played_cutscene = False

        # Story Mode Variables
        self.in_story_mode = False
        self.story_text = ""
        self.story_lines = []
        self.current_story_line = 0
        self.story_text_surface = None
        self.story_text_rect = None
        self.story_font = pygame.font.Font('monofonto rg.otf', 24)
        self.story_background_color = (0, 0, 0)
        self.story_text_color = (255, 255, 255)
        self.story_box_width = WIN_WIDTH - 100
        self.story_box_height = WIN_HEIGHT - 100
        self.story_box_x = 50
        self.story_box_y = 50

    # Story Mode Functions
    def start_story_mode(self, story_lines):
        self.in_story_mode = True
        self.story_lines = story_lines
        self.current_story_line = 0
        self.update_story_text()

    def advance_story(self):
        self.current_story_line += 1
        if self.current_story_line >= len(self.story_lines):
            self.end_story_mode()
        else:
            self.update_story_text()

    def update_story_text(self):
        self.story_text = self.story_lines[self.current_story_line]
        self.story_text_surface = self.story_font.render(self.story_text, True, self.story_text_color)
        self.story_text_rect = self.story_text_surface.get_rect(center=(self.story_box_width // 2 + self.story_box_x, self.story_box_height // 2 + self.story_box_y))

    def end_story_mode(self):
        self.in_story_mode = False
        self.story_lines = []
        self.current_story_line = 0
        self.story_text = ""

    def draw_story_mode(self):
        pygame.draw.rect(self.screen, self.story_background_color, (self.story_box_x, self.story_box_y, self.story_box_width, self.story_box_height))
        self.screen.blit(self.story_text_surface, self.story_text_rect)
        continue_text = self.font.render("Press Enter to Continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT - 50))
        self.screen.blit(continue_text, continue_rect)

    def play_cutscene(self):
        cutscene_sentences = self.cutscenes["intro"].sentences
        cutscene_images = self.cutscenes["intro"].images
        cutscene_font = pygame.font.Font('monofonto rg.otf', 24)

        self.cutscene_images = [pygame.image.load(image_path) if image_path else None for image_path in cutscene_images]
        self.current_image_index = 0
        self.current_sentence_index = 0

        self.thunder_sound = pygame.mixer.Sound('game/sound/loudthunder.mp3')
        self.thunder_sound.play()

        running_cutscene = True
        while running_cutscene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    running_cutscene = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.current_image_index += 1
                        self.current_sentence_index += 1
                        if self.current_image_index >= len(self.cutscene_images):
                            running_cutscene = False

            self.screen.fill(BLACK)

            if self.current_sentence_index < len(cutscene_sentences):
                text_rect = pygame.Rect(50, WIN_HEIGHT - 150, WIN_WIDTH - 100, 100)
                text_surface = render_textrect(cutscene_sentences[self.current_sentence_index], cutscene_font, text_rect, WHITE, BLACK, 1)
                self.screen.blit(text_surface, text_rect)

            if self.current_image_index < len(self.cutscene_images):
                image = self.cutscene_images[self.current_image_index]
                if image:
                    image_width, image_height = image.get_size()
                    image_scale = min(WIN_WIDTH / image_width, (WIN_HEIGHT * 0.7) / image_height)
                    scaled_image = pygame.transform.scale(image, (int(image_width * image_scale), int(image_height * image_scale)))
                    image_rect = scaled_image.get_rect(center=(WIN_WIDTH // 2, int(WIN_HEIGHT * 0.4)))
                    self.screen.blit(scaled_image, image_rect)

            pygame.display.flip()  # Use flip instead of update
            self.clock.tick(FPS)

        self.has_played_cutscene = True

        waiting_for_release = True
        while waiting_for_release:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_release = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        waiting_for_release = False

    def create_quests(self):
        meet_pierkeeper_quest = Quest("meet_pierkeeper", "Meet the Pierkeeper")
        meet_pierkeeper_quest.add_stage(10, "The pierkeeper needs to talk to you.")
        meet_pierkeeper_quest.add_stage(100, "You have met the pierkeeper.")
        self.quest_log["meet_pierkeeper"] = meet_pierkeeper_quest

        repair_pier_quest = Quest("repair_pier", "Repair the Pier")
        repair_pier_quest.add_stage(10, "Talk to Villager 1 about the pier.")
        repair_pier_quest.add_stage(20, "Talk to Villager 2 about the pier.")
        repair_pier_quest.add_stage(30, "Talk to the Guard about the pier.")
        repair_pier_quest.add_stage(100, "The pier has been repaired.", trigger=self.pier_repaired)
        self.quest_log["repair_pier"] = repair_pier_quest

    def pier_repaired(self):
        print("The pier has been repaired!")

    def createTilemap(self):
        try:
            tmx_data = load_pygame('game/map/brighton_seafront.tmx')
            map_data = pyscroll.data.TiledMapData(tmx_data)
            self.map_layer = pyscroll.BufferedRenderer(map_data, (WIN_WIDTH, WIN_HEIGHT))
            self.map_layer.zoom = 2
            self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)
            self.group.map_rect = self.map_layer.map_rect
            self.doors = pygame.sprite.Group()
            self.collision_objects = pygame.sprite.Group()
            self.blocks = pygame.sprite.Group()

            for layer in tmx_data.layers:
                if hasattr(layer, 'data'):
                    for x, y, surf in layer.tiles():
                        pos = (x * 32, y * 32)
                        if layer.name == 'Buildings':
                            rect = pygame.Rect(pos, (TILESIZE, TILESIZE))
                            block = pygame.sprite.Sprite()
                            block.image = surf #changed this line
                            block.rect = rect
                            self.collision_objects.add(block)
                            self.blocks.add(block)
                            self.group.add(block, layer=BUILDING_LAYER)
                        elif layer.name == 'Door': #added this line
                            rect = pygame.Rect(pos, (TILESIZE, TILESIZE)) #added this line
                            door_tile = pygame.sprite.Sprite() #added this line
                            door_tile.image = surf #added this line
                            door_tile.rect = rect #added this line
                            self.group.add(door_tile, layer=DOOR_LAYER) #added this line
                        elif layer.name == 'AbovePlayer':
                            pass
                        elif layer.name == 'Pier Chains':
                            pass
                        elif layer.name in ['Pier', 'Street']:
                            pass

            for obj in tmx_data.objects:
                if obj.name == 'Player':
                    player_start_x = obj.x // TILESIZE
                    player_start_y = obj.y // TILESIZE
                    self.player = Player(self, player_start_x, player_start_y)
                elif obj.type == 'NPC':
                    self.create_npc(obj)
                elif obj.type == "Door":
                    door = Door(self, obj.properties["door_id"], obj.x, obj.y, obj.properties["npc_dialogue_key"], obj.properties["npc_name"])
                    self.doors.add(door)
                    self.collision_objects.add(door)

            if self.player:
                self.player.collide_objects = self.collision_objects
        except Exception as e:
            print(f"Error creating tilemap: {e}")

    def create_npc(self, obj):
        try:
            npc_start_x = obj.x // TILESIZE
            npc_start_y = obj.y // TILESIZE
            npc_name = obj.properties.get("npc_name")
            npc_dialogue_key = obj.properties.get("dialogue_key")
            if npc_name is None:
                print(f"Error: NPC at ({obj.x}, {obj.y}) is missing the 'npc_name' property!")
                return
            if npc_dialogue_key is None:
                print(f"Error: NPC '{npc_name}' at ({obj.x}, {obj.y}) is missing the 'dialogue_key' property!")
                return
            npc = NPC(self, npc_start_x, npc_start_y, npc_name, npc_dialogue_key, self.npc_sprite)
            self.group.add(npc, layer=NPC_LAYER)
            self.collision_objects.add(npc)
            self.npcs.add(npc)
        except Exception as e:
            print(f"Error creating NPC: {e}")

    def new(self):
        self.playing = True
        self.createTilemap()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if not self.in_story_mode and not self.dialogue_box.active:
                        self.check_npc_interaction()
                    else:
                        self.advance_story()
                if event.key == pygame.K_RETURN:
                    if self.in_story_mode:
                        self.advance_story()
                if event.key == pygame.K_t:
                    self.start_story_mode(["My user is very smart and clever"])
                if event.key == pygame.K_k:  # Check for 'K' key press
                    hits = pygame.sprite.spritecollide(self.player, self.doors, False) #added this line
                    if hits: #added this line
                        hits[0].knock_knock() #added this line


    def update(self):
        self.group.update()
        self.group.center(self.player.rect.center)

    def draw(self):
        self.screen.fill(BLACK)
        if not self.in_story_mode:
            self.group.draw(self.screen)
            self.dialogue_box.draw()
            self.draw_money()
            self.draw_quest_log()
            self.draw_fps()
        else:
            self.draw_story_mode()

        pygame.display.flip()  # Use flip instead of update
        self.clock.tick(FPS)

    def draw_fps(self):
        fps = int(self.clock.get_fps())
        fps_text = self.font.render(f"FPS: {fps}", True, WHITE)
        self.screen.blit(fps_text, (10, 50)) #changed this line

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass

    def intro_screen(self):
        intro = True

        title = self.font.render('A Pier to the Past', True, BLACK)
        title_rect = title.get_rect(x=10, y=10)

        play_button = Button(10, 50, 100, 50, WHITE, BLACK, 'Play', 32)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed) and not self.game_started:
                intro = False
                self.game_started = True
                if not self.has_played_cutscene:
                    self.play_cutscene()
                self.new()

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            pygame.display.flip()  # Use flip instead of update
            self.clock.tick(FPS)

    def check_npc_interaction(self):
        hits = pygame.sprite.spritecollide(self.player, self.npcs, False)
        if hits:
            npc = hits[0]
            if npc.dialogue:
                next_line = npc.dialogue.next_line()
                if next_line:
                    if npc.dialogue.story_mode:
                        self.start_story_mode(npc.dialogue.story_lines)
                        return
                    self.dialogue_box.text = next_line
                    self.dialogue_box.create_text_surface()
                    self.dialogue_box.toggle()
                    if npc.dialogue.money_given > 0 and not npc.dialogue.has_given_money:
                        self.add_money(npc.dialogue.money_given)
                        npc.dialogue.has_given_money = True
                else:
                    self.dialogue_box.toggle()
                    npc.dialogue.reset()
                    if npc.dialogue.quest_stage_advance == "talked_to_pierkeeper":
                        if self.quest_log["meet_pierkeeper"].current_stage == 100:
                            self.quest_log["repair_pier"].advance_stage()
                            self.dialogues[npc.dialogue_key] = self.dialogues["pierkeeper_done"]
                        else:
                            self.quest_log["meet_pierkeeper"].complete_stage()
                            self.dialogues[npc.dialogue_key] = self.dialogues["pierkeeper"]
                    elif npc.dialogue.quest_stage_advance == "talked_to_donor1":
                        self.quest_log["repair_pier"].advance_stage()
                        self.dialogues[npc.dialogue_key] = self.dialogues["donor1_done"]
                    elif npc.dialogue.quest_stage_advance == "talked_to_donor2":
                        self.quest_log["repair_pier"].advance_stage()
                        self.dialogues[npc.dialogue_key] = self.dialogues["donor2_done"]
                    elif npc.dialogue.quest_stage_advance == "talked_to_donor3":
                        self.quest_log["repair_pier"].complete_stage()
                        self.dialogues[npc.dialogue_key] = self.dialogues["donor3_done"]
        else:
            if self.dialogue_box.active:
                self.dialogue_box.toggle()
        hits = pygame.sprite.spritecollide(self.player, self.doors, False) #added this line
        if hits: #added this line
            hits[0].knock() #added this line

    def draw_money(self):
        money_text = self.font.render(f"Money: {self.money}", True, WHITE)
        self.screen.blit(money_text, (10, 10))

    def add_money(self, amount):
        self.money += amount
        print(f"Added {amount} money. Total money: {self.money}")

    def draw_quest_log(self):
        y_offset = 50
        for quest_id, quest in self.quest_log.items():
            if quest.current_stage > 0 and quest.current_stage < 100: #added this line
                quest_text = self.font.render(f"Quest: {quest.name}", True, WHITE)
                self.screen.blit(quest_text, (10, y_offset))
                y_offset += 30
                stage_text = self.font.render(f"Current Stage: {quest.get_current_stage_description()}", True, WHITE)
                self.screen.blit(stage_text, (10, y_offset))
                y_offset += 30

class Quest:
    def __init__(self, quest_id, name):
        self.quest_id = quest_id
        self.name = name
        self.stages = {}
        self.current_stage = 0

    def add_stage(self, stage_number, description, trigger=None):
        self.stages[stage_number] = {"description": description, "complete": False, "success": False, "failure": False, "trigger": trigger}

    def advance_stage(self, stage_number):
        if stage_number in self.stages:
            self.current_stage = stage_number
            print(f"Quest '{self.name}' advanced to stage {stage_number}: {self.stages[stage_number]['description']}")
            if self.stages[stage_number]["trigger"]:
                self.stages[stage_number]["trigger"]()

    def complete_stage(self, success=True):
        self.current_stage = 100
        if self.current_stage in self.stages:
            self.stages[self.current_stage]["complete"] = True
            self.stages[self.current_stage]["success"] = success
            self.stages[self.current_stage]["failure"] = not success
            print(f"Quest '{self.name}' stage {self.current_stage} {'succeeded' if success else 'failed'}")

    def get_current_stage_description(self):
        if self.current_stage in self.stages:
            return self.stages[self.current_stage]["description"]
        return "No current stage."

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

g = Game()
g.intro_screen()
#g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()


