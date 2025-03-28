import pygame
from config import *

class Door(pygame.sprite.Sprite):
    def __init__(self, game, door_id, x, y, npc_dialogue_key, npc_name):
        super().__init__()
        self.game = game
        self.door_id = door_id
        self.npc_dialogue_key = npc_dialogue_key
        self.npc_name = npc_name
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)  # Temporary color for visualization
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.knocked = False
        self.collision_rect = pygame.Rect(self.rect.x - TILESIZE, self.rect.y, TILESIZE * 2, TILESIZE)

    def knock(self):
        if not self.knocked:
            self.knocked = True
            print(f"Knocking on {self.door_id}!")
            # Simple "Knock Knock" speech bubble for now
            bubble = SpeechBubble(self.game, "Knock Knock", self.rect.centerx, self.rect.top)
            self.game.group.add(bubble, layer=ABOVE_PLAYER_LAYER)
            # Spawn NPC
            npc = NPC(self.game, self.rect.x // TILESIZE, self.rect.y // TILESIZE, self.npc_name, self.npc_dialogue_key, self.game.npc_sprite)
            self.game.npcs.add(npc)
            self.game.group.add(npc, layer=NPC_LAYER)
            self.game.collision_objects.add(npc)
            npc.interact()

    def knock_knock(self):
        print(f"knock_knock() called for door {self.door_id}")


class TransitionSprite(pygame.sprite.Sprite):
    def __init__(self,pos, size, target, groups):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.target = target


class SpeechBubble(pygame.sprite.Sprite):
    def __init__(self, game, text, x, y, duration=120):
        super().__init__()
        self.game = game
        self.text = text
        self.font = pygame.font.Font('monofonto rg.otf', 24)
        self.color = WHITE
        self.background_color = BLACK
        self.duration = duration
        self.timer = 0
        self.create_surface()
        self.rect.center = (x, y - 30)

    def create_surface(self):
        self.image = self.font.render(self.text, True, self.color, self.background_color)
        self.rect = self.image.get_rect()

    def update(self):
        self.timer += 1
        if self.timer > self.duration:
            self.kill()

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        pygame.sprite.Sprite.__init__(self) #changed this line
        self.collide_objects = None
        self.teleport_cooldown = 0
        self.update_cooldown = 0

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'

        self.image = self.game.character_spritesheet.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.game.group.add(self, layer=PLAYER_LAYER)

    def update(self):
        self.movement()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')
        self.x_change = 0
        self.y_change = 0
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.x_change -= PLAYER_SPEED
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
        
    def collide_blocks(self, direction):
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False) #changed this line
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
            hits = pygame.sprite.spritecollide(self, self.collide_objects, False)
            if hits:
                for hit in hits:
                    if isinstance(hit, Door):
                        pass
                    else:
                        if self.x_change > 0:
                            self.rect.x = hit.rect.left - self.rect.width
                        if self.x_change < 0:
                            self.rect.x = hit.rect.right

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False) #changed this line
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
            hits = pygame.sprite.spritecollide(self, self.collide_objects, False)
            if hits:
                for hit in hits:
                    if isinstance(hit, Door):
                        pass
                    else:
                        if self.y_change > 0:
                            self.rect.y = hit.rect.top - self.rect.height
                        if self.y_change < 0:
                            self.rect.y = hit.rect.bottom


    def say(self, text):
        bubble = SpeechBubble(self.game, text, self.rect.centerx, self.rect.top)
        self.game.group.add(bubble, layer=ABOVE_PLAYER_LAYER)

class Button:
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

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width / 2, self.height / 2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False


class Portal(pygame.sprite.Sprite):
    def __init__(self, game, portal_id, x, y): #changed this line
        super().__init__()
        self.game = game
        self.portal_id = portal_id
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def interact(self):
        print(f"Player entered portal: {self.portal_id}")

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name, dialogue_key, sprite):
        print(f"NPC __init__ called for: {name}")
        self.game = game
        pygame.sprite.Sprite.__init__(self) #changed this line

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.name = name
        self.dialogue_key = dialogue_key
        self.dialogue = self.game.dialogues.get(self.dialogue_key)

        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.game.group.add(self, layer=NPC_LAYER)

    def walk_out(self):
        self.rect.x += TILESIZE * 3


    def update(self):
        pass

    def interact(self):
        print(f"NPC {self.name} interact() called")
        if self.dialogue:
            next_line = self.dialogue.next_line()
            if next_line:
                self.game.dialogue_box.text = next_line
                self.game.dialogue_box.create_text_surface()
                self.game.dialogue_box.toggle()
                if self.dialogue.money_given > 0 and not self.dialogue.has_given_money:
                    self.game.add_money(self.dialogue.money_given)
                    self.dialogue.has_given_money = True
            else:
                self.game.dialogue_box.toggle()
                self.dialogue.reset()
                if self.dialogue.quest_stage_advance == "talked_to_pierkeeper":
                    if self.game.quest_log["meet_pierkeeper"].current_stage == 100:
                        self.game.quest_log["repair_pier"].advance_stage(10)
                        self.game.dialogues[self.dialogue_key] = self.game.dialogues["pierkeeper_done"]
                    else:
                        self.game.quest_log["prologue"].complete_stage()
                        self.game.quest_log["meet_pierkeeper"].advance_stage(10)
                        self.game.dialogues[self.dialogue_key] = self.game.dialogues["pierkeeper"]
                elif self.dialogue.quest_stage_advance == "talked_to_donor1":
                    self.game.quest_log["repair_pier"].advance_stage(10)
                    self.game.dialogues[self.dialogue_key] = self.game.dialogues["donor1_done"]
                elif self.dialogue.quest_stage_advance == "talked_to_donor2":
                    self.game.quest_log["repair_pier"].advance_stage(10)
                    self.game.dialogues[self.dialogue_key] = self.game.dialogues["donor2_done"]
                elif self.dialogue.quest_stage_advance == "talked_to_donor3":
                    self.game.quest_log["repair_pier"].complete_stage()
                    self.game.dialogues[self.dialogue_key] = self.game.dialogues["donor3_done"]
