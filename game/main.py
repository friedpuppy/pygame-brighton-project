import pygame
from sprites import *  # Import everything from sprites.py
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

        self.intro_background = pygame.image.load('./splash.png')

        self.player = None
        self.npcs = pygame.sprite.Group()
        self.dialogues = dialogues
        self.dialogue_box = DialogueBox(self, "", 50, 550)
        self.money = 0
        self.quest_log = {}
        self.create_quests()
        self.collide_objects = pygame.sprite.Group() #added this line
        self.all_sprites = pygame.sprite.LayeredUpdates()

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
        print("createTilemap() called") #added this line
        tmx_data = load_pygame('game/map/brighton_seafront.tmx')
        print(f"createTilemap() tmx_data: {tmx_data}") #added this line
        map_data = pyscroll.data.TiledMapData(tmx_data)
        print(f"createTilemap() map_data: {map_data}") #added this line
        self.map_layer = pyscroll.BufferedRenderer(map_data, (WIN_WIDTH, WIN_HEIGHT))
        self.map_layer.zoom = 2
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)
        self.blocks = pygame.sprite.Group()

        for layer in tmx_data.layers:
            print(f"createTilemap() layer: {layer}") #added this line
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    print(f"createTilemap() x: {x}, y: {y}, surf: {surf}") #added this line
                    pos = (x * 32, y * 32)
                    #tile = Tile(pos=pos, surf=surf, groups=self.group) # Remove this line
                    if layer.name == 'Buildings':
                        #self.blocks.add(tile) # Remove this line
                        block = pygame.sprite.Sprite() #create a sprite for the buildings
                        block.image = surf #set the image to the tile image
                        block.rect = block.image.get_rect(topleft=pos) #set the position
                        self.blocks.add(block) #add it to the blocks group
                        self.group.add(block) #add it to the group, so it is rendered

        for obj in tmx_data.objects:
            print(f"createTilemap() obj: {obj}") #added this line
            if obj.name == 'Player':
                player_start_x = obj.x // TILESIZE
                player_start_y = obj.y // TILESIZE
                self.player = Player(self, player_start_x, player_start_y)
                self.group.add(self.player)
                self.all_sprites.add(self.player) #added this line
            elif obj.type == 'NPC':
                npc_start_x = obj.x // TILESIZE
                npc_start_y = obj.y // TILESIZE
                npc_name = obj.properties.get("npc_name")
                npc_dialogue_key = obj.properties.get("dialogue_key")
                npc_sprite = self.enemy_spritesheet.get_sprite(3, 2, TILESIZE, TILESIZE)
                if npc_name is None:
                    print(f"Error: NPC at ({obj.x}, {obj.y}) is missing the 'npc_name' property!")
                    continue
                if npc_dialogue_key is None:
                    print(f"Error: NPC '{npc_name}' at ({obj.x}, {obj.y}) is missing the 'dialogue_key' property!")
                    continue
                NPC(self, npc_start_x, npc_start_y, npc_name, npc_dialogue_key, npc_sprite)
                self.group.add(self.npcs)
            elif obj.type == 'door': #added this line
                door_id = obj.name #added this line
                door_x = obj.x #added this line
                door_y = obj.y #added this line
                door_dialogue_key = obj.properties.get("dialogue_key") #added this line
                door_name = obj.properties.get("npc_name") #added this line
                door = Door(self, door_id, door_x, door_y, door_dialogue_key, door_name) #added this line
                self.collide_objects.add(door) #added this line
                self.group.add(door) #added this line

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
                    self.check_npc_interaction()

    def update(self):
        self.all_sprites.update()
        self.group.center(self.player.rect.center)

    def draw(self):
        self.screen.fill(BLACK)
        self.group.draw(self.screen)
        self.dialogue_box.draw()
        self.draw_money()
        self.draw_quest_log()

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

        title = self.font.render('Hello World', True, BLACK)
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

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def check_npc_interaction(self):
        print("check_npc_interaction() called") #added this line
        hits = pygame.sprite.spritecollide(self.player, self.npcs, False)
        print(f"check_npc_interaction() hits: {hits}") #added this line
        if hits:
            npc = hits[0]
            npc.interact()
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
        print(f"Quest.get_current_stage_description() called for {self.name}") #added this line
        print(f"Quest.get_current_stage_description() self.current_stage: {self.current_stage}") #added this line
        print(f"Quest.get_current_stage_description() self.stages: {self.stages}") #added this line
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
