import pygame
import sys
from pytmx.util_pygame import load_pygame
import os

pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'
screen_width = 1200
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Sustainable Energy Game")

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

gui_width = screen_width * 0.3
gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

tilemap = load_pygame("terrain_map.tmx")

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

camera_x = 0
camera_y = 0
dragging = False
last_mouse_pos = None

zoom = 0.3
zoom_step = 0.05
min_zoom = 0.25
max_zoom = 2.0

show_grid = False
placed_blocks = {}

gui_scroll_offset = 0
gui_scroll_speed = 20

global destroy_button_rect
destroy_button_rect = None

selected_building = None
destroy_mode = False

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

battery1_power = 50
battery2_power = 100

lab1_research_per_second = 1
lab2_research_per_second = 10
lab3_research_per_second = 100

wind_turbine_power_per_second = 1
solar_panel_power_per_second = 5
coal_plant_power_per_second = 25
nuclear_plant_power_per_second = 50
fusion_plant_power_per_second = 100

house1_money_per_second = 5
house2_money_per_second = 25
house3_money_per_second = 50

game_clock = pygame.time.Clock()
tick_interval = 1000
last_tick = pygame.time.get_ticks()

global research_button_rect
research_tree_open = True
research_button_rect = None

# Function to render the research tree GUI
def render_research_tree():
    global back_button_rect
    screen.fill((50, 50, 50))
    text("Research Tree", 48, (255, 255, 255), (screen_width // 2 - 150, 50))
    back_button_rect = text("< Back", 30, (255, 255, 255), (screen_width - 1100, 45), True, (100, 40), (100, 100, 100))
    text("Research Points: " + str(research), 24, (255, 255, 255), (20, 150))

# Function to render the tilemap
def render_tilemap(surface, tilemap, offset_x, offset_y, zoom):
    for layer in tilemap.layers:
        if hasattr(layer, "data"):
            for y in range(layer.height):
                for x in range(layer.width):
                    gid = layer.data[y][x]
                    if gid != 0:
                        tile = tilemap.get_tile_image_by_gid(gid)
                        if tile:
                            tile_width = int(tilemap.tilewidth * zoom)
                            tile_height = int(tilemap.tileheight * zoom)
                            scaled_tile = pygame.transform.scale(tile, (tile_width, tile_height))
                            surface.blit(scaled_tile, (x * tile_width + offset_x, y * tile_height + offset_y))

# Function to render the grid only on tiles with a specific gid in the tilemap
def render_grid(surface, tilemap, offset_x, offset_y, zoom, valid_tiles):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    for layer in tilemap.visible_layers:
        if hasattr(layer, "data"):
            for y in range(layer.height):
                for x in range(layer.width):
                    gid = layer.data[y][x]
                    if gid == 5:
                        grid_x = x * tile_width + offset_x
                        grid_y = y * tile_height + offset_y

                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x + tile_width, grid_y))
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y), (grid_x, grid_y + tile_height))
                        pygame.draw.line(surface, (200, 200, 200), (grid_x + tile_width, grid_y), (grid_x + tile_width, grid_y + tile_height))
                        pygame.draw.line(surface, (200, 200, 200), (grid_x, grid_y + tile_height), (grid_x + tile_width, grid_y + tile_height))

                        valid_tiles.add((x, y))

# Function to render placed blocks with hover effect in destroy mode
def render_placed_blocks(surface, placed_blocks, offset_x, offset_y, zoom, mouse_pos):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    for (grid_x, grid_y), block_image in placed_blocks.items():
        block_x = grid_x * tile_width + offset_x
        block_y = grid_y * tile_height + offset_y
        scaled_image = pygame.transform.scale(block_image, (tile_width, tile_height))

        if destroy_mode and block_x <= mouse_pos[0] < block_x + tile_width and block_y <= mouse_pos[1] < block_y + tile_height:
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
        text_x = button_rect.x + (button_rect.width - display_text.get_width()) // 2
        text_y = button_rect.y + (button_rect.height - display_text.get_height()) // 2
        screen.blit(display_text, (text_x, text_y))
        return button_rect
    else:
        screen.blit(display_text, position)
        return None

def can_place_building(grid_x, grid_y):
    if 0 <= grid_x < tilemap.width and 0 <= grid_y < tilemap.height:
        gid_layer2 = tilemap.layers[1].data[grid_y][grid_x]
        return gid_layer2 == 0
    return False

# Update max_power dynamically based on placed batteries
def update_max_power():
    global max_power
    max_power = 50
    for (grid_x, grid_y), block_image in placed_blocks.items():
        if block_image == battery_images[0]:
            max_power += battery1_power
        elif block_image == battery_images[1]:
            max_power += battery2_power

# Function to update research points based on placed labs
def update_research():
    global research, research_pm
    added_research = 0
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[0]) * lab1_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[1]) * lab2_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[2]) * lab3_research_per_second
    research += added_research
    research_pm = round(added_research * 60, 2)

# Function to update power points based on placed power plants
def update_power():
    global power, power_pm
    added_power = 0
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[0]) * wind_turbine_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[1]) * solar_panel_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[2]) * coal_plant_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[3]) * nuclear_plant_power_per_second
    added_power += sum(1 for block_image in placed_blocks.values() if block_image == power_plant_images[4]) * fusion_plant_power_per_second
    power += added_power
    power_pm = round(added_power * 60, 2)
    power = min(power, max_power)

# Function to convert power into money based on placed houses
def update_money():
    global money, money_pm, power
    required_power = 0
    earned_money = 0

    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[0]) * house1_money_per_second
    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[1]) * house2_money_per_second
    required_power += sum(1 for block_image in placed_blocks.values() if block_image == house_images[2]) * house3_money_per_second

    if power >= required_power:
        earned_money += required_power
        power -= required_power
    else:
        earned_money += power
        power = 0

    money += earned_money
    money_pm = round(earned_money * 60, 2)

# Adjust GUI rendering to account for scrolling
def render_gui():
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)

    global destroy_button_rect
    global research_button_rect
    
    if money_pm == 0:
        text(f"Money: ${money}", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))
    else:
        text(f"Money: ${money} + {money_pm}/pm", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))

    if power_pm == 0:
        text(f"Power: {power} MW / {max_power} MW", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))
    else:
        text(f"Power: {power} MW / {max_power} MW + {power_pm}/pm", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))

    if research_pm == 0:
        text(f"Research: {research} RP", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))
    else:
        text(f"Research: {research} RP + {research_pm}/pm", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))

    if heat_pm == 0:
        text(f"Heat: {heat} / {max_heat}", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))
    else:
        text(f"Heat: {heat} / {max_heat} + {heat_pm}/pm", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))

    research_button_rect = text("Research", 24, (255, 255, 255), (20, 180 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    destroy_button_rect = text("Destroy: ON" if destroy_mode else "Destroy: OFF", 24, (255, 255, 255), (20, 220 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    text("Buildings", 30, (255, 255, 255), (20, 280 - gui_scroll_offset))
    text("- Power plants", 24, (200, 200, 200), (40, 320 - gui_scroll_offset))
    text("- Labs", 24, (200, 200, 200), (40, 400 - gui_scroll_offset))
    text("- Houses", 24, (200, 200, 200), (40, 480 - gui_scroll_offset))
    text("- Batterys", 24, (200, 200, 200), (40, 560 - gui_scroll_offset))

    global power_plant_buttons, lab_buttons, house_buttons, battery_buttons

    power_plant_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 340 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(5)]
    lab_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 420 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    house_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 500 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    battery_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 580 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(2)]

    for i, img in enumerate(power_plant_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 340 + 10 - gui_scroll_offset))

    for i, img in enumerate(lab_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 420 + 10 - gui_scroll_offset))

    for i, img in enumerate(house_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 500 + 10 - gui_scroll_offset))

    for i, img in enumerate(battery_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 580 + 10 - gui_scroll_offset))

# Main game loop
running = True
valid_tiles = set()
while running:
    # Check for screen resizing and adjust dimensions
    info = pygame.display.Info()

    if screen_width != info.current_w or screen_height != info.current_h:
        
        screen_width = info.current_w
        screen_height = info.current_h

        gui_width = screen_width * 0.3
        gui_rect = pygame.Rect(0, 0, gui_width, screen_height)

    # Clear the screen with a background color
    screen.fill((92, 105, 160))

    # Render the tilemap with the current camera and zoom settings
    render_tilemap(screen, tilemap, gui_width + camera_x, camera_y, zoom)

    if show_grid:
        # Clear and render the grid if enabled
        valid_tiles.clear()
        render_grid(screen, tilemap, gui_width + camera_x, camera_y, zoom, valid_tiles)

    # Render placed blocks and handle hover effects in destroy mode
    render_placed_blocks(screen, placed_blocks, gui_width + camera_x, camera_y, zoom, pygame.mouse.get_pos())

    if show_grid and not destroy_mode and selected_building:
        # Highlight valid placement tiles for the selected building
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
        grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

        if (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks:
            tile_width = int(tilemap.tilewidth * zoom)
            tile_height = int(tilemap.tileheight * zoom)
            block_x = grid_x * tile_width + gui_width + camera_x
            block_y = grid_y * tile_height + camera_y

            greyed_out_image = pygame.transform.scale(selected_building, (tile_width, tile_height)).copy()
            greyed_out_image.fill((128, 128, 128, 150), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(greyed_out_image, (block_x, block_y))

    # Render the GUI elements
    render_gui()

    for event in pygame.event.get():
        # Handle quitting the game
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse button down events
            mouse_x, mouse_y = event.pos

            if destroy_button_rect and destroy_button_rect.collidepoint((mouse_x, mouse_y)):
                # Toggle destroy mode
                destroy_mode = not destroy_mode
                if destroy_mode:
                    show_grid = True
                    selected_building = None
                else:
                    show_grid = False

            if research_button_rect and research_button_rect.collidepoint((mouse_x, mouse_y)):
                # Toggle research tree visibility
                research_tree_open = not research_tree_open
            
            if back_button_rect and back_button_rect.collidepoint((mouse_x, mouse_y)):
                # Close the research tree
                research_tree_open = False

            elif gui_rect.collidepoint(mouse_x, mouse_y):
                # Handle GUI button clicks
                for i, rect in enumerate(power_plant_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        # Select or deselect a power plant
                        if selected_building == power_plant_images[i]:
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = power_plant_images[i]
                            show_grid = True
                            destroy_mode = False

                for i, rect in enumerate(lab_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        # Select or deselect a lab
                        if selected_building == lab_images[i]:
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = lab_images[i]
                            show_grid = True
                            destroy_mode = False

                for i, rect in enumerate(house_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        # Select or deselect a house
                        if selected_building == house_images[i]:
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = house_images[i]
                            show_grid = True
                            destroy_mode = False

                for i, rect in enumerate(battery_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        # Select or deselect a battery
                        if selected_building == battery_images[i]:
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = battery_images[i]
                            show_grid = True
                            destroy_mode = False

            elif show_grid and destroy_mode:
                # Handle block destruction in destroy mode
                grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in valid_tiles:
                    if event.button == 1:
                        if (grid_x, grid_y) in placed_blocks:
                            block_image = placed_blocks[(grid_x, grid_y)]
                            building_name = building_mapping[block_image]
                            building_cost = building_prices[building_name]
                            money += building_cost
                            del placed_blocks[(grid_x, grid_y)]
                            update_max_power()

            elif show_grid and not destroy_mode:
                # Handle block placement
                grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks and can_place_building(grid_x, grid_y):
                    if event.button == 1 and selected_building:
                        building_name = building_mapping[selected_building]
                        building_cost = building_prices[building_name]

                        if money >= building_cost:
                            money -= building_cost
                            placed_blocks[(grid_x, grid_y)] = selected_building
                            update_max_power()

            if event.button == 3:
                # Start dragging the map
                dragging = True
                last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging the map
            if event.button == 3:
                dragging = False
                last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            # Handle map dragging
            if dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_x += dx
                camera_y += dy
                last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            # Handle zooming and GUI scrolling
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if gui_rect.collidepoint(mouse_x, mouse_y):
                # Scroll the GUI
                gui_scroll_offset = max(0, gui_scroll_offset - event.y * gui_scroll_speed)
            else:
                # Zoom the map
                map_mouse_x = (mouse_x - gui_width - camera_x) / zoom
                map_mouse_y = (mouse_y - camera_y) / zoom

                if event.y > 0:
                    new_zoom = min(zoom + zoom_step, max_zoom)
                elif event.y < 0:
                    new_zoom = max(zoom - zoom_step, min_zoom)

                camera_x -= int((map_mouse_x * (new_zoom - zoom)))
                camera_y -= int((map_mouse_y * (new_zoom - zoom)))

                zoom = new_zoom

    if research_tree_open:
        # Render the research tree if open
        render_research_tree()
        pygame.display.flip()
        continue

    # Update game state at regular intervals
    current_time = pygame.time.get_ticks()
    if current_time - last_tick >= tick_interval:
        last_tick = current_time
        update_research()
        update_power()
        update_money()

    pygame.display.flip()

pygame.quit()
sys.exit()