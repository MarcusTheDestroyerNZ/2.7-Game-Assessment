import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 29*64
screen_height = 16*64

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sustanable Energy Game")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color
    screen.fill((0, 0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()