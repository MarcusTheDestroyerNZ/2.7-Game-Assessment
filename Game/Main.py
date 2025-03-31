import pygame
import sys
from pytmx.util_pygame import load_pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 32 * 64
screen_height = 16 * 64

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sustainable Energy Game")

# Define GUI dimensions
gui_width = 400  # Width of the GUI on the left side
gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

# Load the tilemap
tilemap = load_pygame("Map.tmx")

# Camera offsets
camera_x = 0
camera_y = 0

# Variables for mouse dragging
dragging = False
last_mouse_pos = None

# Zoom variables
zoom = 1.0  # Initial zoom level
zoom_step = 0.1  # Step for zooming in/out
min_zoom = 0.5  # Minimum zoom level
max_zoom = 2.0  # Maximum zoom level

# Function to render the tilemap
def render_tilemap(surface, tilemap, offset_x, offset_y, zoom):
    for layer in tilemap.visible_layers:
        if hasattr(layer, "tiles"):
            for x, y, tile in layer.tiles():
                if tile:
                    # Scale the tile based on the zoom level
                    tile_width = int(tilemap.tilewidth * zoom)
                    tile_height = int(tilemap.tileheight * zoom)
                    scaled_tile = pygame.transform.scale(tile, (tile_width, tile_height))
                    # Adjust position based on zoom
                    surface.blit(scaled_tile, (x * tile_width + offset_x, y * tile_height + offset_y))

# Function to render the grid only on tiles with a specific gid in the tilemap
def render_grid(surface, tilemap, offset_x, offset_y, zoom):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    # Iterate through the layers and tiles
    for layer in tilemap.visible_layers:
        if hasattr(layer, "data"):  # Use layer.data to access tile GIDs
            for y in range(layer.height):  # Iterate over rows
                for x in range(layer.width):  # Iterate over columns
                    gid = layer.data[y][x]  # Get the gid of the tile
                    if gid == 5:  # Only draw the grid for tiles with gid 135
                        # Calculate the position of the tile
                        grid_x = x * tile_width + offset_x
                        grid_y = y * tile_height + offset_y

                        # Draw the grid lines around the tile
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x + tile_width, grid_y))  # Top
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x, grid_y + tile_height))  # Left
                        pygame.draw.line(surface, (200, 200, 200), (grid_x + tile_width, grid_y), (grid_x + tile_width, grid_y + tile_height))  # Right
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y + tile_height), (grid_x + tile_width, grid_y + tile_height))  # Bottom

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                dragging = True
                last_mouse_pos = event.pos

        # Handle mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging = False
                last_mouse_pos = None

        # Handle mouse motion
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                dx = mouse_x - last_mouse_pos[0]
                dy = mouse_y - last_mouse_pos[1]
                camera_x += dx
                camera_y += dy
                last_mouse_pos = event.pos

        # Handle mouse wheel for zooming
        elif event.type == pygame.MOUSEWHEEL:
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Calculate the position of the mouse relative to the map
            map_mouse_x = (mouse_x - gui_width - camera_x) / zoom
            map_mouse_y = (mouse_y - camera_y) / zoom

            # Adjust zoom level
            if event.y > 0:  # Scroll up
                new_zoom = min(zoom + zoom_step, max_zoom)
            elif event.y < 0:  # Scroll down
                new_zoom = max(zoom - zoom_step, min_zoom)

            # Adjust camera offsets to zoom into the mouse position
            camera_x -= int((map_mouse_x * (new_zoom - zoom)))
            camera_y -= int((map_mouse_y * (new_zoom - zoom)))

            # Update the zoom level
            zoom = new_zoom

    # Fill the screen with a color
    screen.fill((92, 105, 160))

    # Render the tilemap on the right side of the screen with camera offsets and zoom
    render_tilemap(screen, tilemap, gui_width + camera_x, camera_y, zoom)

    # Render the grid on top of the tilemap
    render_grid(screen, tilemap, gui_width + camera_x, camera_y, zoom)

    # Draw the GUI area (ensures it appears on top)
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)  # Gray background for the GUI

    # Add text or buttons to the GUI (example: a title)
    font = pygame.font.Font(None, 36)
    text = font.render("GUI", True, (255, 255, 255))
    screen.blit(text, (20, 20))  # Position the text inside the GUI

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()