import pygame
from sprites import *
from config import *
import sys
from pytmx.util_pygame import load_pygame
import time

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, animation_frames=None):
        super().__init__(groups)
        self.animation_frames = animation_frames
        if animation_frames:
            self.is_animated = True
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            self.animation_speed = animation_frames[0].duration
            self.image = animation_frames[0].image
        else:
            self.is_animated = False
            self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        if self.is_animated:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.image = self.animation_frames[self.current_frame].image

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
        self.image_layers = []

        self.player = None
        self.roof_tiles = pygame.sprite.Group()
        self.windmill_tiles = pygame.sprite.Group()
        self.animated_objects = pygame.sprite.Group()

    def createTilemap(self):
        tmx_data = load_pygame('game/map/city.tmx')
        
        self.blocks = pygame.sprite.LayeredUpdates()
        sprite_group = pygame.sprite.Group()
        for layer in tmx_data.layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 32, y * 32)
                    tile_id = tmx_data.get_tile_gid(x, y, layer.id)
                    animation_frames = tmx_data.get_tile_animation_frames(tile_id)
                    if animation_frames:
                        tile = Tile(pos=pos, surf=None, groups=sprite_group, animation_frames=animation_frames)
                    else:
                        tile = Tile(pos=pos, surf=surf, groups=sprite_group)

                    if layer.name == 'Buildings':
                        self.blocks.add(tile)
                    elif layer.name == 'Roof':
                        self.roof_tiles.add(tile)
                    elif layer.name == 'Windmill':
                        self.windmill_tiles.add(tile)
            elif hasattr(layer, 'objects'):
                 for obj in layer:
                        if obj.name == 'Player':
                                player_start_x = obj.x // TILESIZE
                                player_start_y = obj.y // TILESIZE
                                self.player = Player(self, player_start_x, player_start_y)
                        elif layer.name == "WindmillAnimated":
                             tile_id = obj.gid
                             pos = (obj.x, obj.y)
                             animation_frames = tmx_data.get_tile_animation_frames(tile_id)
                             tile = Tile(pos = pos, surf = None, groups = self.animated_objects, animation_frames = animation_frames)
            elif hasattr(layer, 'image'):
                  self.image_layers.append(layer)
        self.all_sprites.add(sprite_group)
        return self.player

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.player = self.createTilemap()
        if self.player is not None:
            self.all_sprites.add(self.player)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        self.all_sprites.update()
        self.windmill_tiles.update()
        self.animated_objects.update()

    def draw(self):
        self.screen.fill(BLACK)
        for layer in self.image_layers:
           self.screen.blit(layer.image, (layer.offsetx, layer.offsety))
        self.all_sprites.draw(self.screen)
        self.roof_tiles.draw(self.screen)
        self.windmill_tiles.draw(self.screen)
        self.animated_objects.draw(self.screen)
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

            self.screen.blit(self.intro_background, (0,0))
            self.screen.blit (title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()
        

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()
