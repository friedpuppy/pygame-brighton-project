import pygame
from sprites import *
from config import *
import sys

import pytmx
#tmxdata = pytmx.TiledMap("game\city1.tmx")

from pytmx.util_pygame import load_pygame
tmxdata = pytmx.TiledMap('game/city1.tmx')

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('monofonto rg.otf', 32)
        self.running = True

        self.character_spritesheet = Spritesheet('game/img/character.png')
        self.terrain_spritesheet = Spritesheet('game/img/terrain.png')

        self.intro_background = pygame.image.load('./splash.png')

    def createTilemap(self):
            for i, row in enumerate(overworld):
                for j, column in enumerate(row):
                    Ground(self, j, i) #draws the grass background here
                    if column == "B":
                        Block(self, j, i)
                    if column== "P":
                        self.player = Player(self, j, i)
                    if column== "R":
                        Road(self, j, i)
                    if column == "N":  # 'N' represents an NPC in the overworld map
                        NPC(self, j, i, "npc_1")  # Reference dialogue by key
            return self.player
                                           

    def new(self):
        # new game start
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.npcs = pygame.sprite.LayeredUpdates()  # New group for NPCs
        self.talking_npc = None
        self.player_interacting = False

        self.player = self.createTilemap() # assign returned player to self.player

    def events(self):
        # game loop events
        for event in pygame.event.get(): #every single event that happens in pygame
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.player_interacting:
                        if self.talking_npc:
                            self.talking_npc.talk()
                    else:
                        hits = pygame.sprite.spritecollide(self.player, self.npcs, False)
                        if hits:
                            self.player_interacting = True
                            self.talking_npc = hits[0]
                            self.talking_npc.talk() #starts the conversation
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                   if self.talking_npc:
                        if not self.talking_npc.talking:
                             self.player_interacting = False
                             self.talking_npc = None
                
    def update(self):
        # game loop updates
        self.all_sprites.update()
        if not pygame.sprite.spritecollide(self.player, self.npcs, False):
            if not self.player_interacting:
                self.talking_npc = None #clear dialogue if there are no hits.


    def draw(self):
        # game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)

        # Display dialogue if an NPC is talking
        if self.talking_npc: #only draw the text if there is an NPC collision
            pygame.draw.rect(self.screen, WHITE, (50, WIN_HEIGHT - 100, WIN_WIDTH - 100, 50))
            text = self.font.render(self.talking_npc.dialogue[self.talking_npc.dialogue_index], True, BLACK)
            self.screen.blit(text, (60, WIN_HEIGHT - 85))

        self.clock.tick(FPS)
        pygame.display.update() #update the screen

    def main(self):
        # game loop
        while self.playing:
            self.events()
            self.update() #so that the game isn't a static image
            self.draw() #displays sprites
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

            self.screen.blit(self.intro_background, (0,0))
            self.screen.blit (title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()
        

g = Game() #converts class into object
g.intro_screen()#creates game object and runs intro_screen method. skips for now
g.new() #creates sprite groups and player objects
while g.running:
    g.main() #game loop
    g.game_over() #doesn't do anything currently but will do later

pygame.quit()
sys.exit()
