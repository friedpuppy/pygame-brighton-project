import pygame
import pytmx
import os

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32  # Adjust if your tile size is different
PLAYER_SPEED = 200 # Pixels per second
PLAYER_SIZE = (28, 28) # Slightly smaller than tile size for easier movement

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0
        self.vy = 0
        self.speed = PLAYER_SPEED

    def update(self, dt, walls):
        keys = pygame.key.get_pressed()
        self.vx, self.vy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.speed

        # Normalize diagonal movement (optional, but good practice)
        if self.vx != 0 and self.vy != 0:
            self.vx /= 1.414 # sqrt(2)
            self.vy /= 1.414

        # Move and check collisions separately for x and y
        self.rect.x += self.vx * dt
        self.collide_with_walls(self.vx, 0, walls)

        self.rect.y += self.vy * dt
        self.collide_with_walls(0, self.vy, walls)

    def collide_with_walls(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: # Moving right; hit left side of wall
                    self.rect.right = wall.left
                if dx < 0: # Moving left; hit right side of wall
                    self.rect.left = wall.right
                if dy > 0: # Moving down; hit top side of wall
                    self.rect.bottom = wall.top
                if dy < 0: # Moving up; hit bottom side of wall
                    self.rect.top = wall.bottom

# --- Camera Class ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target, map_width_px, map_height_px):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to map size
        x = min(0, x)  # Don't scroll left past map edge
        y = min(0, y)  # Don't scroll up past map edge
        x = max(-(map_width_px - SCREEN_WIDTH), x) # Don't scroll right past map edge
        y = max(-(map_height_px - SCREEN_HEIGHT), y) # Don't scroll down past map edge

        self.camera = pygame.Rect(x, y, self.width, self.height)


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TMX Map Transition Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0 # Delta time

        self.tiled_map = None
        self.map_renderer = None
        self.map_rect = None
        self.walls = []
        self.transitions = []
        self.spawn_points = {}

        self.player = None
        self.all_sprites = pygame.sprite.Group()

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT) # Initial camera size

        self.load_map("mayor_brighton_seafront.tmx", "start") # Load initial map and spawn point

    def load_map(self, filename, spawn_point_name):
        """Loads a TMX map and positions the player."""
        filepath = os.path.join(os.path.dirname(__file__), filename) # Look in same folder as script
        try:
            self.tiled_map = pytmx.load_pygame(filepath)
            print(f"Loaded map: {filename}")
        except FileNotFoundError:
            print(f"Error: Map file '{filename}' not found at '{filepath}'.")
            self.running = False
            return
        except Exception as e:
            print(f"Error loading map '{filename}': {e}")
            self.running = False
            return

        self.map_width_px = self.tiled_map.width * self.tiled_map.tilewidth
        self.map_height_px = self.tiled_map.height * self.tiled_map.tileheight
        self.map_rect = pygame.Rect(0, 0, self.map_width_px, self.map_height_px)
        self.camera.width = self.map_width_px # Update camera based on map size
        self.camera.height = self.map_height_px

        # --- Process Objects ---
        self.walls = []
        self.transitions = []
        self.spawn_points = {}

        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                # Collision Objects
                if layer.name == "Collision":
                    for obj in layer:
                        if obj.visible:
                           self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                    print(f"  - Found {len(self.walls)} collision objects.")

                # Transition Objects (Doors)
                elif layer.name == "Transitions":
                    for obj in layer:
                        if obj.visible and 'target_map' in obj.properties and 'target_spawn' in obj.properties:
                            self.transitions.append({
                                'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                                'target_map': obj.properties['target_map'],
                                'target_spawn': obj.properties['target_spawn']
                            })
                    print(f"  - Found {len(self.transitions)} transition objects.")

                # Spawn Points
                elif layer.name == "Spawns":
                    for obj in layer:
                         if obj.visible and 'name' in obj.properties:
                            spawn_name = obj.properties['name']
                            self.spawn_points[spawn_name] = (obj.x, obj.y) # Use top-left for consistency
                    print(f"  - Found {len(self.spawn_points)} spawn points: {list(self.spawn_points.keys())}")


        # --- Position Player ---
        if spawn_point_name in self.spawn_points:
            spawn_x, spawn_y = self.spawn_points[spawn_point_name]
            if self.player is None:
                self.player = Player(spawn_x, spawn_y)
                self.all_sprites.add(self.player)
            else:
                # Reposition existing player
                self.player.rect.topleft = (spawn_x, spawn_y)
                # Ensure player sprite group is correct if needed (usually fine)
                if self.player not in self.all_sprites:
                    self.all_sprites.add(self.player)
            print(f"  - Player spawned at '{spawn_point_name}' ({spawn_x}, {spawn_y})")
        else:
            print(f"Error: Spawn point '{spawn_point_name}' not found in map '{filename}'. Defaulting to (0,0).")
            if self.player is None:
                self.player = Player(0, 0)
                self.all_sprites.add(self.player)
            else:
                self.player.rect.topleft = (0, 0)

        # Ensure the camera updates immediately after loading/spawning
        self.camera.update(self.player, self.map_width_px, self.map_height_px)


    def run(self):
        """Main game loop."""
        while self.running:
            # Delta time calculation (for frame-rate independent movement)
            self.dt = self.clock.tick(60) / 1000.0 # seconds

            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

    def handle_events(self):
        """Process input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Optional: Add key press for interaction if desired
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_e:
            #         self.check_transitions(interact_key_pressed=True)


    def update(self):
        """Update game state."""
        if not self.running: return # Don't update if map loading failed

        self.all_sprites.update(self.dt, self.walls)
        self.camera.update(self.player, self.map_width_px, self.map_height_px)

        # Check for transitions (trigger on collision)
        self.check_transitions()

    def check_transitions(self, interact_key_pressed=False):
        """Checks if player collides with any transition object."""
        # If using an interact key, add 'and interact_key_pressed' to the condition
        if self.player:
            for transition in self.transitions:
                if self.player.rect.colliderect(transition['rect']):
                    print(f"Transition triggered! Loading map: {transition['target_map']}, Spawn: {transition['target_spawn']}")
                    self.load_map(transition['target_map'], transition['target_spawn'])
                    # Important: break after triggering one transition to avoid issues
                    # if multiple transitions overlap or player is on border
                    break

    def draw_tile(self, surface, ti, tx, ty):
         """Draws a single tile with camera offset."""
         # Get the image for the tile GID 'ti'
         image = self.tiled_map.get_tile_image_by_gid(ti)
         if image:
             # Calculate screen position using camera offset
             screen_pos = self.camera.apply_rect(pygame.Rect(tx * self.tiled_map.tilewidth,
                                                             ty * self.tiled_map.tileheight,
                                                             self.tiled_map.tilewidth,
                                                             self.tiled_map.tileheight))
             surface.blit(image, screen_pos)


    def draw(self):
        """Render everything to the screen."""
        if not self.running: return # Don't draw if map loading failed

        self.screen.fill(BLACK) # Background color if map doesn't cover screen

        # --- Draw Tile Layers respecting Camera ---
        # Render layers below the player
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name != "Above_Player":
                for x, y, gid in layer:
                    self.draw_tile(self.screen, gid, x, y)

        # --- Draw Sprites (Player) ---
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # --- Draw Layers Above Player ---
        for layer in self.tiled_map.visible_layers:
             if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Above_Player":
                for x, y, gid in layer:
                    self.draw_tile(self.screen, gid, x, y)

        # --- Draw Debug Info (Optional) ---
        # Draw collision boxes
        # for wall in self.walls:
        #     pygame.draw.rect(self.screen, (0, 0, 255), self.camera.apply_rect(wall), 1)
        # # Draw transition zones
        # for trans in self.transitions:
        #      pygame.draw.rect(self.screen, (0, 255, 0), self.camera.apply_rect(trans['rect']), 1)
        # # Draw spawn points
        # for name, pos in self.spawn_points.items():
        #     spawn_rect = pygame.Rect(pos[0]-2, pos[1]-2, 4, 4)
        #     pygame.draw.rect(self.screen, (255, 255, 0), self.camera.apply_rect(spawn_rect), 0)

        pygame.display.flip()


# --- Run the Game ---
if __name__ == '__main__':
    game = Game()
    game.run()