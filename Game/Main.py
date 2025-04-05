import pygame
import sys
from pytmx.util_pygame import load_pygame
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window on the screen
screen_width = 1200
screen_height = 800

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Sustainable Energy Game")

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Define GUI dimensions
gui_width = screen_width * 0.3  # Width of the GUI on the left side
gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

# Load the tilemap
tilemap = load_pygame("Map.tmx")

# Load the solar panel image
solar_panel_image = pygame.image.load("Assets/Mountain.png")
solar_panel_image = pygame.transform.scale(solar_panel_image, (tilemap.tilewidth, tilemap.tileheight))

# Reorder power plant images for the GUI
power_plant_images = [
    pygame.image.load("Assets/wind_turbine.png"),
    pygame.image.load("Assets/solar_panel.png"),
    pygame.image.load("Assets/coal_plant.png"),
    pygame.image.load("Assets/nuclear_plant.png"),
    pygame.image.load("Assets/fusion_plant.png")
]

lab_images = [
    pygame.image.load("Assets/lab1.png"),
    pygame.image.load("Assets/lab2.png"),
    pygame.image.load("Assets/lab3.png")
]

house_images = [
    pygame.image.load("Assets/house1.png"),
    pygame.image.load("Assets/house2.png"),
    pygame.image.load("Assets/house3.png")
]

battery_images = [
    pygame.image.load("Assets/battery1.png"),
    pygame.image.load("Assets/battery2.png")
]

# Prices for all buildings
building_prices = {
    "wind_turbine": 10,
    "solar_panel": 50,
    "coal_plant": 500,
    "nuclear_plant": 1000,
    "fusion_plant": 2000,
    "lab1": 100,
    "lab2": 500,
    "lab3": 1500,
    "house1": 10,
    "house2": 100,
    "house3": 750,
    "battery1": 50,
    "battery2": 500
}

# Map images to their corresponding building names
building_mapping = {
    power_plant_images[0]: "wind_turbine",
    power_plant_images[1]: "solar_panel",
    power_plant_images[2]: "coal_plant",
    power_plant_images[3]: "nuclear_plant",
    power_plant_images[4]: "fusion_plant",
    lab_images[0]: "lab1",
    lab_images[1]: "lab2",
    lab_images[2]: "lab3",
    house_images[0]: "house1",
    house_images[1]: "house2",
    house_images[2]: "house3",
    battery_images[0]: "battery1",
    battery_images[1]: "battery2"
}

# Camera offsets
camera_x = 0
camera_y = 0

# Variables for mouse dragging
dragging = False
last_mouse_pos = None

# Zoom variables
zoom = 0.3  # Initial zoom level
zoom_step = 0.05  # Step for zooming in/out
min_zoom = 0.25  # Minimum zoom level
max_zoom = 2.0  # Maximum zoom level

# Add a button to toggle the grid system
show_grid = False

# Add a dictionary to track placed blocks
placed_blocks = {}

# Variables for scrolling
gui_scroll_offset = 0
gui_scroll_speed = 20

# Ensure button_rect is defined globally and accessible
global button_rect
button_rect = None

# Add a variable to track the selected building type
selected_building = None

# Add a variable to track destroy mode
destroy_mode = False

# Variables for money, power, research and heat
global money, money_pm, power, max_power, power_pm, research, research_pm, heat, max_heat, heat_pm
money = 20
money_pm = 0
power = 0
max_power = 50
power_pm = 0
research = 0
research_pm = 0
heat = 0
max_heat = 0
heat_pm = 0

# Variables for power contribution per building
battery1_power = 50
battery2_power = 100

# Variables for research contribution per building
lab1_research_per_second = 1
lab2_research_per_second = 10
lab3_research_per_second = 100

# Variables for power contribution per power plant
wind_turbine_power_per_second = 1
solar_panel_power_per_second = 5
coal_plant_power_per_second = 25
nuclear_plant_power_per_second = 50
fusion_plant_power_per_second = 100

# Variables for money contribution per house
house1_money_per_second = 5
house2_money_per_second = 25
house3_money_per_second = 50

# Add a clock for managing the game tick
game_clock = pygame.time.Clock()
tick_interval = 1000  # 1 second in milliseconds
last_tick = pygame.time.get_ticks()

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
def render_grid(surface, tilemap, offset_x, offset_y, zoom, valid_tiles):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    # Iterate through the layers and tiles
    for layer in tilemap.visible_layers:
        if hasattr(layer, "data"):  # Use layer.data to access tile GIDs
            for y in range(layer.height):  # Iterate over rows
                for x in range(layer.width):  # Iterate over columns
                    gid = layer.data[y][x]  # Get the gid of the tile
                    if gid == 5:  # Only draw the grid for tiles with gid 5
                        # Calculate the position of the tile
                        grid_x = x * tile_width + offset_x
                        grid_y = y * tile_height + offset_y

                        # Draw the grid lines around the tile
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x + tile_width, grid_y))  # Top
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x, grid_y + tile_height))  # Left
                        pygame.draw.line(surface, (200, 200, 200), (grid_x + tile_width, grid_y), (grid_x + tile_width, grid_y + tile_height))  # Right
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y + tile_height), (grid_x + tile_width, grid_y + tile_height))  # Bottom

                        # Mark this tile as valid for building
                        valid_tiles.add((x, y))

# Function to render placed blocks with hover effect in destroy mode
def render_placed_blocks(surface, placed_blocks, offset_x, offset_y, zoom, mouse_pos):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    for (grid_x, grid_y), block_image in placed_blocks.items():
        block_x = grid_x * tile_width + offset_x
        block_y = grid_y * tile_height + offset_y
        # Scale the block image based on the zoom level
        scaled_image = pygame.transform.scale(block_image, (tile_width, tile_height))

        # Check if the mouse is hovering over this block in destroy mode
        if destroy_mode and block_x <= mouse_pos[0] < block_x + tile_width and block_y <= mouse_pos[1] < block_y + tile_height:
            # Apply a red tint to the block
            tinted_image = scaled_image.copy()
            tinted_image.fill((255, 0, 0, 205), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted_image, (block_x, block_y))
        else:
            surface.blit(scaled_image, (block_x, block_y))

# Function to make text display
def text(text, size, color, position, button=False, button_size=(0, 0), button_color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    display_text = font.render(text, True, color)
    if button:
        button_rect = pygame.Rect(position, button_size)
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(display_text, (button_rect.x + 10, button_rect.y + 10))
        return button_rect  # Return the button's rectangle for collision detection
    else:
        screen.blit(display_text, position)
        return None

def can_place_building(grid_x, grid_y):
    # Check if a building can be placed on the given grid coordinates
    if 0 <= grid_x < tilemap.width and 0 <= grid_y < tilemap.height:
        gid = tilemap.data[grid_y][grid_x]  # Assuming the first layer is used for grid validation
        return gid == 5  # Only allow placement on tiles with gid 5
    return False

# Update max_power dynamically based on placed batteries
def update_max_power():
    global max_power
    max_power = 50  # Reset max power to 0
    for (grid_x, grid_y), block_image in placed_blocks.items():
        if block_image == battery_images[0]:  # battery1
            max_power += battery1_power
        elif block_image == battery_images[1]:  # battery2
            max_power += battery2_power

# Function to update research points based on placed labs
def update_research():
    global research, research_pm
    added_research = 0  # Reset added research for this tick
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[0]) * lab1_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[1]) * lab2_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[2]) * lab3_research_per_second
    research += added_research
    research_pm = round(added_research * 60, 2)  # Convert to per minute

# Function to update power points based on placed power plants
def update_power():
    global power, power_pm
    added_power = 0  # Reset added power for this tick
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[0]) * wind_turbine_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[1]) * solar_panel_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[2]) * coal_plant_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[3]) * nuclear_plant_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[4]) * fusion_plant_power_per_second
    power += added_power
    power_pm = round(added_power * 60, 2)  # Convert to per minute
    # Ensure power does not exceed max_power
    power = min(power, max_power)

# Function to convert power into money based on placed houses
def update_money():
    global money, money_pm, power
    required_power = 0
    earned_money = 0

    # Calculate required power and earned money based on houses
    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[0]) * house1_money_per_second
    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[1]) * house2_money_per_second
    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[2]) * house3_money_per_second

    # Only convert power to money if enough power is available
    if power >= required_power:
        earned_money += required_power
        power -= required_power
    else:
        earned_money += power
        power = 0

    money += earned_money
    money_pm = round(earned_money * 60, 2)  # Convert to per minute

# Adjust GUI rendering to account for scrolling
def render_gui():
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)  # Gray background for the GUI

    # Render GUI content with scroll offset
    global button_rect
    
    # Display money with or without money_per_min based on its value
    if money_pm == 0:
        text(f"Money: ${money}", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))
    else:
        text(f"Money: ${money} + {money_pm}/pm", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))

    # Display power with or without power_per_min based on its value
    if power_pm == 0:
        text(f"Power: {power} MW / {max_power} MW", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))
    else:
        text(f"Power: {power} MW / {max_power} MW + {power_pm}/pm", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))

    # Display research with or without research_per_min based on its value
    if research_pm == 0:
        text(f"Research: {research} RP", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))
    else:
        text(f"Research: {research} RP + {research_pm}/pm", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))

    # Display heat with or without heat_per_min based on its value
    if heat_pm == 0:
        text(f"Heat: {heat} / {max_heat}", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))
    else:
        text(f"Heat: {heat} / {max_heat} + {heat_pm}/pm", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))
        
    button_rect = text("Destroy: ON" if destroy_mode else "Destroy: OFF", 24, (255, 255, 255), (20, 180 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    text("Buildings", 30, (255, 255, 255), (20, 240 - gui_scroll_offset))
    text("- Power plants", 24, (200, 200, 200), (40, 280 - gui_scroll_offset))
    text("- Labs", 24, (200, 200, 200), (40, 360 - gui_scroll_offset))
    text("- Houses", 24, (200, 200, 200), (40, 440 - gui_scroll_offset))
    text("- Batterys", 24, (200, 200, 200), (40, 520 - gui_scroll_offset))

    # Define button lists globally to ensure accessibility
    global power_plant_buttons, lab_buttons, house_buttons, battery_buttons

    power_plant_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 300 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(5)]
    lab_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 380 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    house_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 460 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    battery_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 540 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(2)]

    # Render images with scroll offset
    for i, img in enumerate(power_plant_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 300 + 10 - gui_scroll_offset))

    for i, img in enumerate(lab_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 380 + 10 - gui_scroll_offset))

    for i, img in enumerate(house_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 460 + 10 - gui_scroll_offset))

    for i, img in enumerate(battery_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 540 + 10 - gui_scroll_offset))

# Main game loop
running = True
valid_tiles = set()  # Set to store valid tiles for building
while running:
    info = pygame.display.Info()

    if screen_width != info.current_w or screen_height != info.current_h:
        
        screen_width = info.current_w
        screen_height = info.current_h

        gui_width = screen_width * 0.3  # Width of the GUI on the left side
        gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

    # Fill the screen with a color
    screen.fill((92, 105, 160))

    # Render the tilemap on the right side of the screen with camera offsets and zoom
    render_tilemap(screen, tilemap, gui_width + camera_x, camera_y, zoom)

    # Render the grid and update valid tiles
    if show_grid:
        valid_tiles.clear()  # Clear the set before updating
        render_grid(screen, tilemap, gui_width + camera_x, camera_y, zoom, valid_tiles)

    # Render placed blocks
    render_placed_blocks(screen, placed_blocks, gui_width + camera_x, camera_y, zoom, pygame.mouse.get_pos())

    # Render a greyed-out version of the selected building when hovering over a valid placement area
    if show_grid and not destroy_mode and selected_building:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
        grid_y = (mouse_y - camera_y) // int(tilemap.tileheight * zoom)

        if (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks:
            tile_width = int(tilemap.tilewidth * zoom)
            tile_height = int(tilemap.tileheight * zoom)
            block_x = grid_x * tile_width + gui_width + camera_x
            block_y = grid_y * tile_height + camera_y

            # Create a greyed-out version of the selected building
            greyed_out_image = pygame.transform.scale(selected_building, (tile_width, tile_height)).copy()
            greyed_out_image.fill((128, 128, 128, 150), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(greyed_out_image, (block_x, block_y))

    # Call render_gui instead of directly rendering GUI content
    render_gui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check if the button was clicked
            if button_rect and button_rect.collidepoint((mouse_x, mouse_y)):
                destroy_mode = not destroy_mode  # Toggle destroy mode
                if destroy_mode:
                    show_grid = True
                    selected_building = None  # Turn off build mode
                else:
                    show_grid = False  # Turn off grid when destroy mode is disabled

            elif gui_rect.collidepoint(mouse_x, mouse_y):
                # Check clicks on power plant buttons
                for i, rect in enumerate(power_plant_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == power_plant_images[i]:
                            selected_building = None
                            show_grid = False  # Disable build mode
                        else:
                            selected_building = power_plant_images[i]
                            show_grid = True  # Enable build mode
                            destroy_mode = False  # Turn off destroy mode

                # Check clicks on lab buttons
                for i, rect in enumerate(lab_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == lab_images[i]:
                            selected_building = None
                            show_grid = False  # Disable build mode
                        else:
                            selected_building = lab_images[i]
                            show_grid = True  # Enable build mode
                            destroy_mode = False  # Turn off destroy mode

                # Check clicks on house buttons
                for i, rect in enumerate(house_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == house_images[i]:
                            selected_building = None
                            show_grid = False  # Disable build mode
                        else:
                            selected_building = house_images[i]
                            show_grid = True  # Enable build mode
                            destroy_mode = False  # Turn off destroy mode

                # Check clicks on battery buttons
                for i, rect in enumerate(battery_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == battery_images[i]:
                            selected_building = None
                            show_grid = False  # Disable build mode
                        else:
                            selected_building = battery_images[i]
                            show_grid = True  # Enable build mode
                            destroy_mode = False  # Turn off destroy mode

            elif show_grid and destroy_mode:  # Only allow removing blocks in destroy mode
                grid_x = (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
                grid_y = (mouse_y - camera_y) // int(tilemap.tileheight * zoom)

                if (grid_x, grid_y) in valid_tiles:  # Check if the tile is valid for building
                    if event.button == 1:  # Left mouse button for removing blocks
                        if (grid_x, grid_y) in placed_blocks:
                            del placed_blocks[(grid_x, grid_y)]
                            update_max_power()  # Update max power after removing a block

            elif show_grid and not destroy_mode:  # Allow placing blocks only in build mode
                grid_x = (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
                grid_y = (mouse_y - camera_y) // int(tilemap.tileheight * zoom)

                if (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks:  # Check if the tile is valid and not already occupied
                    if event.button == 1 and selected_building:  # Left mouse button for placing blocks
                        building_name = building_mapping[selected_building]
                        building_cost = building_prices[building_name]

                        if money >= building_cost:  # Check if the player has enough money
                            money -= building_cost  # Deduct the cost
                            placed_blocks[(grid_x, grid_y)] = selected_building
                            update_max_power()  # Update max power after placing a block

            # Start dragging if right mouse button is pressed
            if event.button == 3:
                dragging = True
                last_mouse_pos = event.pos

        # Handle mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right mouse button
                dragging = False
                last_mouse_pos = None

        # Handle mouse motion
        elif event.type == pygame.MOUSEMOTION:
            if dragging:  # Only move the camera if dragging is active
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_x += dx
                camera_y += dy
                last_mouse_pos = event.pos

        # Handle mouse wheel for scrolling
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if the mouse is over the GUI
            if gui_rect.collidepoint(mouse_x, mouse_y):
                gui_scroll_offset = max(0, gui_scroll_offset - event.y * gui_scroll_speed)
            else:  # Otherwise, scroll the map
                map_mouse_x = (mouse_x - gui_width - camera_x) / zoom
                map_mouse_y = (mouse_y - camera_y) / zoom

                if event.y > 0:  # Scroll up
                    new_zoom = min(zoom + zoom_step, max_zoom)
                elif event.y < 0:  # Scroll down
                    new_zoom = max(zoom - zoom_step, min_zoom)

                camera_x -= int((map_mouse_x * (new_zoom - zoom)))
                camera_y -= int((map_mouse_y * (new_zoom - zoom)))

                zoom = new_zoom

    # Handle game tick
    current_time = pygame.time.get_ticks()
    if current_time - last_tick >= tick_interval:
        last_tick = current_time
        update_research()  # Update research points every tick
        update_power()  # Update power every tick
        update_money()  # Update money every tick

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()