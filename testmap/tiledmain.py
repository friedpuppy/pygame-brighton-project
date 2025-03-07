import pygame, sys
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

pygame.init()
screen = pygame.display.set_mode((1280,720))
tmx_data = load_pygame('testmap/city.tmx')
sprite_group = pygame.sprite.Group()

#cycle through layers
for layer in tmx_data.layers:
   # if layer.name in ('Ground', 'Buildings', 'Windmill', 'Overgrowth', 'Entrances')
    if hasattr(layer,'data'):
        for x,y,surf in layer.tiles():
            pos = (x * 32, y * 32)
            Tile(pos = pos, surf = surf, groups = sprite_group)



# print(tmx_data.layers)
# for layer in tmx_data.visible_layers:
#     print(layer)

# print(tmx_data.layernames)

# print(tmx_data.get_layer_by_name('Ground'))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    sprite_group.draw(screen)
    pygame.display.update()