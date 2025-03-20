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
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('monofonto rg.otf', 32)
        self.running = True

        self.character_spritesheet = Spritesheet('game/img/character.png')
        self.terrain_spritesheet = Spritesheet('game/img/terrain.png')
        self.enemy_spritesheet = Spritesheet('game/img/enemy.png')

        self.intro_background = pygame.image.load('game/img/BPC00100.jpg')

        self.player = None
        self.npcs = pygame.sprite.Group()
        self.dialogues = dialogues
        self.cutscenes = cutscenes  # Added this line
        self.dialogue_box = DialogueBox(self, "", 50, 550)
        self.money = 0
        self.quest_log = {}
        self.create_quests()
        self.collision_objects = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.has_played_cutscene = False  # Added this line

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
        print("Playing cutscene")
        cutscene_text = self.cutscenes["intro"].text
        cutscene_font = pygame.font.Font('monofonto rg.otf', 24)
        text_surface = cutscene_font.render(cutscene_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))

        running_cutscene = True
        while running_cutscene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    running_cutscene = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running_cutscene = False

            self.screen.fill(BLACK)
            self.screen.blit(text_surface, text_rect)
            pygame.display.update()
        self.has_played_cutscene = True

    def create_quests(self):
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
            self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=GROUND_LAYER)
            self.group.map_rect = self.map_layer.map_rect

            for layer in tmx_data.layers:
                if hasattr(layer, 'data'):
                    for x, y, surf in layer.tiles():
                        pos = (x * 32, y * 32)
                        if layer.name == 'Buildings':
                            tile = Tile(pos=pos, surf=surf, groups=[self.group, self.blocks, self.collision_objects])
                        else:
                            tile = Tile(pos=pos, surf=surf, groups=[self.group])
                        self.group.add(tile, layer=tile.layer)

            for obj in tmx_data.objects:
                if obj.name == 'Player':
                    player_start_x = obj.x // TILESIZE
                    player_start_y = obj.y // TILESIZE
                    self.player = Player(self, player_start_x, player_start_y)
                    self.group.add(self.player, layer=PLAYER_LAYER)
                elif obj.type == 'NPC':
                    self.create_npc(obj)
            
            # Move this line here, after the player is created
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
            npc_sprite = self.enemy_spritesheet.get_sprite(3, 2, TILESIZE, TILESIZE)
            if npc_name is None:
                print(f"Error: NPC at ({obj.x}, {obj.y}) is missing the 'npc_name' property!")
                return
            if npc_dialogue_key is None:
                print(f"Error: NPC '{npc_name}' at ({obj.x}, {obj.y}) is missing the 'dialogue_key' property!")
                return
            npc = NPC(self, npc_start_x, npc_start_y, npc_name, npc_dialogue_key, npc_sprite)
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
                    if not self.in_story_mode:
                        self.check_npc_interaction()
                    else:
                        self.advance_story()
                if event.key == pygame.K_RETURN:
                    if self.in_story_mode:
                        self.advance_story()
                if event.key == pygame.K_t:  # Check for the "T" key press
                    self.start_story_mode(["My user is very smart and clever"])  # Start story mode with placeholder text  

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
        else:
            self.draw_story_mode()

        self.clock.tick(FPS)
        pygame.display.update()

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

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
                if not self.has_played_cutscene:
                    self.play_cutscene()
                self.new()

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

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
                    if npc.dialogue.quest_stage_advance == "talked_to_villager1":
                        self.quest_log["repair_pier"].advance_stage(20)
                        self.dialogues[npc.dialogue_key] = self.dialogues["villager1_done"]
                    elif npc.dialogue.quest_stage_advance == "talked_to_villager2":
                        self.quest_log["repair_pier"].advance_stage(30)
                        self.dialogues[npc.dialogue_key] = self.dialogues["villager2_done"]
                    elif npc.dialogue.quest_stage_advance == "talked_to_guard1":
                        self.quest_log["repair_pier"].advance_stage(100)
                        self.dialogues[npc.dialogue_key] = self.dialogues["guard1_done"]
        else:
            if self.dialogue_box.active:
                self.dialogue_box.toggle()

    def draw_money(self):
        money_text = self.font.render(f"Money: {self.money}", True, WHITE)
        self.screen.blit(money_text, (10, 10))

    def add_money(self, amount):
        self.money += amount
        print(f"Added {amount} money. Total money: {self.money}")

    def draw_quest_log(self):
        y_offset = 50
        for quest_id, quest in self.quest_log.items():
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

    def complete_stage(self, stage_number, success=True):
        if stage_number in self.stages:
            self.stages[stage_number]["complete"] = True
            self.stages[stage_number]["success"] = success
            self.stages[stage_number]["failure"] = not success
            print(f"Quest '{self.name}' stage {stage_number} {'succeeded' if success else 'failed'}")

    def get_current_stage_description(self):
        if self.current_stage in self.stages:
            return self.stages[self.current_stage]["description"]
        return "No current stage."

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()


