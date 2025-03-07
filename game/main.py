import pygame
from sprites import *
from config import *
import sys
from pytmx.util_pygame import load_pygame

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('monofonto rg.otf', 32)
        self.running = True

        self.character_spritesheet = Spritesheet('game/img/character.png')
        # self.terrain_spritesheet = Spritesheet('game/img/terrain.png') #Removed old terrain spritesheet

        self.intro_background = pygame.image.load('./splash.png')

    def createTilemap(self):
        # Load the TMX map
        tmx_data = load_pygame('game/map/city.tmx')
        
        # Create sprite groups for layers (if needed)
        self.ground_tiles = pygame.sprite.LayeredUpdates()
        self.block_tiles = pygame.sprite.LayeredUpdates()

        #cycle through layers
        sprite_group = pygame.sprite.Group()
        for layer in tmx_data.layers:
           # if layer.name in ('Ground', 'Buildings', 'Windmill', 'Overgrowth', 'Entrances')
            if hasattr(layer,'data'):
                for x,y,surf in layer.tiles():
                    pos = (x * 32, y * 32)
                    Tile(pos = pos, surf = surf, groups = sprite_group)
        
        # find player start position from map 
        for obj in tmx_data.objects:
            if obj.name == 'Player':
                player_start_x = obj.x // TILESIZE
                player_start_y = obj.y // TILESIZE
                self.player = Player(self, player_start_x, player_start_y)
                break

        
        return self.player
                                           

    def new(self):
        # new game start
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()


        self.player = self.createTilemap() # assign returned player to self.player
        self.all_sprites.add(self.player)

    def events(self):
        # game loop events
        for event in pygame.event.get(): #every single event that happens in pygame
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

                
    def update(self):
        # game loop updates
        self.all_sprites.update()



    def draw(self):
        # game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
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
