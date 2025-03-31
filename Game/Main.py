import pygame
import sys
from pytmx.util_pygame import load_pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 29 * 64
screen_height = 16 * 64

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sustainable Energy Game")

# Define GUI dimensions
gui_width = 400  # Width of the GUI on the left side
gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

# Load the tilemap
tilemap = load_pygame("./Map.tmx")  # Replace with the actual path to your .tmx file

# Function to render the tilemap
def render_tilemap(surface, tilemap, offset_x, offset_y):
    for layer in tilemap.visible_layers:
        if hasattr(layer, "tiles"):
            for x, y, tile in layer.tiles():
                if tile:
                    surface.blit(tile, (x * tilemap.tilewidth + offset_x, y * tilemap.tileheight + offset_y))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color
    screen.fill((0, 0, 0))

    # Draw the GUI area
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)  # Gray background for the GUI

    # Add text or buttons to the GUI (example: a title)
    font = pygame.font.Font(None, 36)
    text = font.render("GUI", True, (255, 255, 255))
    screen.blit(text, (20, 20))  # Position the text inside the GUI

    # Render the tilemap on the right side of the screen
    render_tilemap(screen, tilemap, gui_width, 0)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()