import pygame
from config import *
import math
import random


class Camera:
    def __init__(self, width, height):
        self.width = width  # Map width in pixels
        self.height = height  # Map height in pixels
        self.zoom_level = 2.0
        self.state = pygame.Rect(0, 0, WIN_WIDTH, WIN_HEIGHT)

    def apply(self, entity):
        # Calculate the scaled position of the entity
        scaled_x = entity.rect.x * self.zoom_level
        scaled_y = entity.rect.y * self.zoom_level
        
        # Create a new rect with the scaled position and size
        scaled_rect = pygame.Rect(scaled_x, scaled_y, entity.rect.width * self.zoom_level, entity.rect.height * self.zoom_level)
        
        # Move the scaled rect by the camera's offset
        return scaled_rect.move(self.state.topleft)

    def apply_rect(self, rect):
        return rect.move(self.state.topleft)

    def update(self, target):
        # Adjust camera movement based on zoom level
        x = -target.rect.centerx * self.zoom_level + int(WIN_WIDTH / 2)
        y = -target.rect.centery * self.zoom_level + int(WIN_HEIGHT / 2)

        # Limit scrolling to map size (adjusted for zoom)
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width * self.zoom_level - WIN_WIDTH), x)  # Right
        y = max(-(self.height * self.zoom_level - WIN_HEIGHT), y)  # Bottom

        self.state = pygame.Rect(x, y, WIN_WIDTH, WIN_HEIGHT)


class Spritesheet:
    # ... (Spritesheet class remains the same) ...
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))  # cuts out the needed sprite from the spritesheet
        sprite.set_colorkey(BLACK)  # makes the specified colour transparent
        return sprite


class Player(pygame.sprite.Sprite):
    # ... (Player class remains the same) ...
    def __init__(self, game, x, y):  # the game is passed in as an object

        self.game = game
        self._layer = ROAD_LAYER + 1
        self.groups = self.game.all_sprites  # this adds the player to the all_sprites group
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0  # temporary variables that store the change in movement during one loop
        self.y_change = 0

        self.facing = 'down'  # is character facing up left or down etc

        self.image = self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height)  # x, y, width, height

                                                                
        self.rect = self.image.get_rect()
        self.rect.x = self.x  # tells pygame the coordinates of our rectangle
        self.rect.y = self.y

    def update(self):
        self.movement()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')
        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()  # list of every key pressed on keyboard stored in 'keys'
        if keys[pygame.K_a]:
            self.x_change -= PLAYER_SPEED  # referenced in config.py
            self.facing = 'left'
        if keys[pygame.K_d]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_w]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_s]:
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

    def collide_blocks(self, direction):  # collision function
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0: #moving right
                    self.rect.x = hits[0].rect.left - self.rect.width #move to the left of the block
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0: #moving up
                    self.rect.y = hits[0].rect.bottom

class Button:
    # ... (Button class remains the same) ...
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font('monofonto rg.otf', fontsize)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)  # 'True' is for antialiasing turned on
        self.text_rect = self.text.get_rect(center=(self.width / 2, self.height / 2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False

class Tile(pygame.sprite.Sprite):
    # ... (Tile class remains the same) ...
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name, dialogue_key, sprite): #added sprite
        self.game = game
        self._layer = ROAD_LAYER + 1
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.name = name
        self.dialogue_key = dialogue_key
        self.dialogue = self.game.dialogues.get(self.dialogue_key)

        self.image = sprite #changed this line
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        pass

    def interact(self):
        if self.dialogue:
            next_line = self.dialogue.next_line()
            if next_line:
                self.game.dialogue_box.text = next_line
                self.game.dialogue_box.create_text_surface()
                self.game.dialogue_box.toggle()
            else:
                self.game.dialogue_box.toggle()
                self.dialogue.reset()
