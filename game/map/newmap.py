import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Player Settings ---
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_COLOR = (255, 150, 0) # Orange

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)      # Map 1 color
BLUE = (0, 0, 150)       # Map 2 color
YELLOW = (255, 255, 0)   # Transition zone color

# --- 1. Define Map Representations (with Transition Zones) ---
# Now, each map includes a list of 'transitions'.
# Each transition has a 'rect' (the zone), 'target_map_id',
# and 'target_spawn_point' (where player appears on the new map).
MAP_DATA = {
    "map1": {
        "bg_color": GREEN,
        "name": "Forest Clearing (Map 1)",
        "transitions": [
            {
                # Zone on the right edge of Map 1
                "rect": pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 50, 50, 100),
                "target_map_id": "map2",
                # Spawn player just inside the left edge of Map 2
                "target_spawn_point": (PLAYER_SIZE // 2 + 10, SCREEN_HEIGHT // 2)
            }
            # Add more transition zones for map1 here if needed
        ]
    },
    "map2": {
        "bg_color": BLUE,
        "name": "Ocean Shore (Map 2)",
        "transitions": [
            {
                # Zone on the left edge of Map 2
                "rect": pygame.Rect(0, SCREEN_HEIGHT // 2 - 50, 50, 100),
                "target_map_id": "map1",
                # Spawn player just inside the right edge of Map 1
                "target_spawn_point": (SCREEN_WIDTH - PLAYER_SIZE // 2 - 10, SCREEN_HEIGHT // 2)
            }
            # Add more transition zones for map2 here
        ]
    }
}

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Transition Zone Map Switching")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Player Setup ---
player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
# Start player near the center, slightly offset to avoid immediate transitions if zones are there
player_rect.center = (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2)

# --- 2. Manage Game States ---
current_map_id = "map1"  # Start with map1
# No timer needed anymore
# last_switch_time = pygame.time.get_ticks() # REMOVED

# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Player Movement (Input Handling) ---
    keys = pygame.key.get_pressed()
    move_x, move_y = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_x += PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_y += PLAYER_SPEED

    # Move player
    player_rect.x += move_x
    player_rect.y += move_y

    # --- Keep Player On Screen ---
    player_rect.clamp_ip(screen.get_rect())

    # --- 3. Handle Transitions (Collision-Based Switching) ---
    # Get the data for the currently active map
    active_map_data = MAP_DATA[current_map_id]

    # Check for collisions with transition zones *on the current map*
    for transition in active_map_data.get("transitions", []): # Use .get for safety
        transition_rect = transition["rect"]
        if player_rect.colliderect(transition_rect):
            # Collision detected! Time to switch maps.

            # --- 4. Load/Unload Maps (Switch State) ---
            target_map = transition["target_map_id"]
            spawn_point = transition["target_spawn_point"]

            print(f"Transitioning from {active_map_data['name']} to {MAP_DATA[target_map]['name']} via zone collision.")

            # Change the current map ID
            current_map_id = target_map

            # Move the player to the spawn point on the new map
            player_rect.center = spawn_point

            # Update active_map_data for drawing this frame on the new map
            active_map_data = MAP_DATA[current_map_id]

            # Important: Break out of the transition check loop
            # Prevents accidentally triggering multiple transitions in one frame
            # if zones somehow overlapped or player moved very fast.
            break


    # --- Drawing ---
    # 1. Fill background based on (potentially updated) current map
    screen.fill(active_map_data["bg_color"])

    # 2. Draw transition zones for the current map (for visualization)
    for transition in active_map_data.get("transitions", []):
        pygame.draw.rect(screen, YELLOW, transition["rect"], 3) # Draw yellow outline

    # 3. Draw map name
    map_text_surface = font.render(active_map_data["name"], True, WHITE)
    map_text_rect = map_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
    screen.blit(map_text_surface, map_text_rect)

    # 4. Draw the player
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # 5. Timer info removed

    # --- Update Display ---
    pygame.display.flip()

    # --- Control Framerate ---
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()