import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 896
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Grid-based Building System")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Grid settings
GRID_SIZE = 64
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Define tile class
class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        self.building = None

    def draw(self, surface):
        # Draw the grid tile (empty or occupied)
        pygame.draw.rect(surface, WHITE, self.rect, 1)
        if self.building:
            pygame.draw.rect(surface, GREEN, self.rect)

# Create grid
grid = [[Tile(x, y) for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]

# Main game loop
def main():
    selected_tile = None
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle mouse click to place a building
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE
                selected_tile = grid[grid_x][grid_y]
                if selected_tile.building is None:
                    selected_tile.building = "Building"  # Just a placeholder

        # Clear the screen
        screen.fill(BLACK)

        # Draw grid
        for row in grid:
            for tile in row:
                tile.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()