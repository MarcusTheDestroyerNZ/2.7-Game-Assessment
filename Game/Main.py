import pygame
import sys
from pytmx.util_pygame import load_pygame
import os

pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'
screen_width = 1200
screen_height = 600

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
    "wind_turbine": 1,
    "solar_panel": 200,
    "coal_plant": 3500,
    "nuclear_plant": 25000,
    "fusion_plant": 250000,
    "lab1": 100,
    "lab2": 1000,
    "lab3": 35000,
    "house1": 50,
    "house2": 500,
    "house3": 10000,
    "battery1": 100,
    "battery2": 1000
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

global money, money_ps, power, max_power, power_ps, research, research_ps, heat, max_heat, heat_pm
money = 1000000000
money_ps = 0
power = 0
max_power = 50
power_ps = 0
research = 0
research_ps = 0
pollution = 0
max_pollution = 1000
pollution_ps = 0

battery1_power = 100
battery2_power = 500

lab1_research_per_second = 1
lab2_research_per_second = 25
lab3_research_per_second = 100

wind_turbine_power_per_second = 0.15
solar_panel_power_per_second = 3
coal_plant_power_per_second = 200
nuclear_plant_power_per_second = 500
fusion_plant_power_per_second = 10000

house1_money_per_second = 5
house2_money_per_second = 250
house3_money_per_second = 5000

game_clock = pygame.time.Clock()
tick_interval = 1000
last_tick = pygame.time.get_ticks()

global research_button_rect
research_tree_open = False
research_button_rect = None

global sell_power_button_rect
sell_power_button_rect = None

# Add tick limits for power plants
power_plant_ticks = {
    "wind_turbine": 10,
    "solar_panel": 100,
    "coal_plant": 300,
    "nuclear_plant": 800,
    "fusion_plant": 1200
}

# Track remaining ticks for each placed power plant
placed_power_plant_ticks = {}

# Initialize the auto-repair flag
auto_repair_wind_turbines = False

# Percentage of the building cost returned when selling
sell_percentage = 0.5
repair_cost_percentage = 0.25

# Define locked tiles for each region (manually assign tiles here)
locked_tiles = {
    "Stewart Island": {
        "tiles": {
            (6, 26),
            (5, 27), (6, 27),
        },
        "locked": True,
        "price": 0
    },
    "Southland": {
        "tiles": {
            (8, 16), (9, 16),
            (7, 17), (8, 17), (9, 17),
            (6, 18), (7, 18), (8, 18), (9, 18), (10, 18),
            (5, 19), (6, 19), (7, 19), (8, 19), (9, 19), (10, 19),
            (4, 20), (5, 20), (6, 20), (7, 20), (8, 20), (9, 20), (10, 20),
            (4, 21), (5, 21), (6, 21), (7, 21), (8, 21), (9, 21), (10, 21),
            (5, 22), (6, 22), (7, 22), (8, 22), (9, 22), (10, 22), (11, 22),
            (8, 23), (9, 23), (10, 23), (11, 23),
            (11, 24)
        },
        "locked": True,
        "price": 5
    },
    "Otago": {
        "tiles": {
            (14, 15), (15, 15), (16, 15),
            (13, 16), (14, 16), (15, 16), (16, 16),
            (12, 17), (13, 17), (14, 17), (15, 17), (16, 17),
            (11, 18), (12, 18), (13, 18), (14, 18), (15, 18),
            (11, 19), (12, 19), (13, 19), (14, 19), (15, 19),
            (11, 20), (12, 20), (13, 20), (14, 20), (15, 20),
            (11, 21), (12, 21), (13, 21), (14, 21), (15, 21),
            (12, 22), (13, 22), (14, 22),
            (12, 23), (13, 23),
            (12, 24)
        }, 
        "locked": True, 
        "price": 1000
    },
    "West Coast": {
        "tiles": {
            (18, 5),
            (17, 6), (18, 6), (19, 6),
            (17, 7), (18, 7), (19, 7),
            (17, 8), (18, 8), 
            (16, 9), (17, 9), (18, 9),
            (15, 10), (16, 10), (17, 10),
            (14, 11), (15, 11), (16, 11),
            (13, 12), (14, 12), (15, 12),
            (11, 13), (12, 13), (13, 13), (14, 13),
            (10, 14), (11, 14), (12, 14), (13, 14), (14, 14),
            (9, 15), (10, 15), (11, 15), (12, 15), (13, 15),
            (10, 16), (11, 16), (12, 16),
            (10, 17), (11, 17),
        }, 
        "locked": True, 
        "price": 5000
    },
    "Canterbury": {
        "tiles": {
            (19, 8), (20, 8), (21, 8), (22, 8), (23, 8),
            (19, 9), (20, 9), (21, 9), (22, 9),
            (18, 10), (19, 10), (20, 10), (21, 10), (22, 10),
            (17, 11), (18, 11), (19, 11), (20, 11),
            (16, 12), (17, 12), (18, 12), (19, 12), (20, 12),
            (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13), (21, 13),
            (15, 14), (16, 14), (17, 14), (18, 14),
        }, 
        "locked": True, 
        "price": 15000
    },
    "Marlborough and Nelson": {
        "tiles": {
            (20, 2),
            (19, 3), (20, 3), (21, 3), (24, 3),
            (19, 4), (20, 4), (21, 4), (22, 4), (23, 4), (24, 4),
            (19, 5), (20, 5), (21, 5), (22, 5), (23, 5), (24, 5),
            (20, 6), (21, 6), (22, 6), (23, 6), (24, 6),
            (20, 7), (21, 7), (22, 7), (23, 7), (24, 7),
        }, 
        "locked": True, 
        "price": 7500
    },
}

# Define research upgrades
research_upgrades = [
    {
        "name": "Double Wind Turbine Ticks",
        "cost": 15,  
        "currency": "money",  
        "effect": lambda: double_wind_turbine_ticks(),
        "purchased": False
    },
    {
        "name": "Double Wind Turbine Efficiency",
        "cost": 50,  
        "currency": "research",  
        "effect": lambda: double_wind_turbine_efficiency(),
        "purchased": False
    },
    {
        "name": "Unlock Research Lab 1",
        "cost": 250,  
        "currency": "money",  
        "effect": lambda: Unlock_research_lab_1(),
        "purchased": False
    },
    {
        "name": "Automaticly repair Wind Turbines",
        "cost": 100,  
        "currency": "research",  
        "effect": lambda: automaticly_repair_wind_turbines(),
        "purchased": False
    }
]

# Function to double wind turbine ticks
def double_wind_turbine_ticks():
    global power_plant_ticks
    power_plant_ticks["wind_turbine"] *= 2

# Function to increase solar panel efficiency
def double_wind_turbine_efficiency():
    global wind_turbine_power_per_second
    wind_turbine_power_per_second *= 2

def Unlock_research_lab_1():
    global Unlock_lab_1
    Unlock_lab_1 = True

# Function to automatically repair wind turbines
def automaticly_repair_wind_turbines():
    global auto_repair_wind_turbines
    auto_repair_wind_turbines = True

# Variables for research tree movement and zoom
research_tree_offset_x = 0
research_tree_offset_y = 0
research_tree_dragging = False
last_research_mouse_pos = None
research_tree_zoom = 1.0
research_tree_zoom_step = 0.1
min_research_tree_zoom = 0.5
max_research_tree_zoom = 2.0

# Function to render the research tree GUI
def render_research_tree():
    global back_button_rect
    screen.fill((50, 50, 50))

    # Draw a fixed background for the title, back button, and resource displays
    header_rect = pygame.Rect(0, 0, screen_width, 200)
    pygame.draw.rect(screen, (30, 30, 30), header_rect)

    # Render title, back button, and resource displays
    text("Research Tree", 48, (255, 255, 255), (screen_width // 2 - 150, 50))
    back_button_rect = text("< Back", 30, (255, 255, 255), (screen_width - 1100, 45), True, (100, 40), (100, 100, 100))
    text(f"Research Points: {research}", 24, (255, 255, 255), (20, 150))
    text(f"Money: ${money}", 24, (255, 255, 255), (20, 180))

    # Define research tree layout with multiple upgrades per tier
    tree_layout = [
        # Tier 1
        [
            {"name": "Double Wind Turbine Ticks", "x": 150, "y": 300, "image": power_plant_images[0]},
            {"name": "Double Solar Panel Efficiency", "x": 400, "y": 300, "image": power_plant_images[1]},
        ],
        # Tier 2
        [
            {"name": "Unlock Research Lab 1", "x": 150, "y": 500, "image": lab_images[0]},
            {"name": "Unlock Research Lab 2", "x": 400, "y": 500, "image": lab_images[1]},
        ],
        # Tier 3
        [
            {"name": "Automatically Repair Wind Turbines", "x": 150, "y": 700, "image": power_plant_images[0]},
            {"name": "Increase Coal Plant Efficiency", "x": 400, "y": 700, "image": power_plant_images[2]},
        ],
    ]

    # Draw connections between nodes
    for i in range(len(tree_layout) - 1):
        for node in tree_layout[i]:
            for next_node in tree_layout[i + 1]:
                # Ensure connections are drawn correctly between nodes
                pygame.draw.line(
                    screen,
                    (0, 255, 0),
                    (
                        node["x"] * research_tree_zoom + 50 + research_tree_offset_x,
                        node["y"] * research_tree_zoom + 50 + research_tree_offset_y,
                    ),
                    (
                        next_node["x"] * research_tree_zoom + 50 + research_tree_offset_x,
                        next_node["y"] * research_tree_zoom + 50 + research_tree_offset_y,
                    ),
                    3,
                )

    # Draw research nodes with images
    for tier in tree_layout:
        for node in tier:
            upgrade = next((u for u in research_upgrades if u["name"] == node["name"]), None)
            if upgrade:
                affordable = (money >= upgrade["cost"] if upgrade["currency"] == "money" else research >= upgrade["cost"])
                button_color = (0, 255, 0) if affordable and not upgrade["purchased"] else (100, 100, 100)
                node["button_rect"] = pygame.Rect(
                    node["x"] * research_tree_zoom + research_tree_offset_x,
                    node["y"] * research_tree_zoom + research_tree_offset_y,
                    100 * research_tree_zoom,
                    100 * research_tree_zoom,
                )
                pygame.draw.rect(screen, button_color, node["button_rect"])

                # Draw the corresponding image
                if "image" in node:
                    scaled_image = pygame.transform.scale(
                        node["image"], (int(80 * research_tree_zoom), int(80 * research_tree_zoom))
                    )
                    screen.blit(
                        scaled_image,
                        (
                            node["x"] * research_tree_zoom + 10 + research_tree_offset_x,
                            node["y"] * research_tree_zoom + 10 + research_tree_offset_y,
                        ),
                    )

                # Display cost below the button
                text(
                    f"Cost: {upgrade['cost']} {'$' if upgrade['currency'] == 'money' else 'RP'}",
                    int(20 * research_tree_zoom),
                    (255, 255, 255),
                    (
                        node["x"] * research_tree_zoom + research_tree_offset_x,
                        node["y"] * research_tree_zoom + 110 * research_tree_zoom + research_tree_offset_y,
                    ),
                )
            else:
                node["button_rect"] = None

# Function to handle research tree interactions
def handle_research_tree_click(mouse_pos):
    global research, money, research_tree_open, research_tree_dragging, last_research_mouse_pos
    for upgrade in research_upgrades:
        if upgrade.get("button_rect") and upgrade["button_rect"].collidepoint(mouse_pos):
            if not upgrade["purchased"]:
                if upgrade["currency"] == "money" and money >= upgrade["cost"]:
                    money -= upgrade["cost"]
                    upgrade["purchased"] = True
                    upgrade["effect"]()
                elif upgrade["currency"] == "research" and research >= upgrade["cost"]:
                    research -= upgrade["cost"]
                    upgrade["purchased"] = True
                    upgrade["effect"]()
                return  # Stop further processing once a button is clicked

    # Handle back button click
    if back_button_rect and back_button_rect.collidepoint(mouse_pos):
        research_tree_open = False

    # Start dragging the research tree
    if not research_tree_dragging:
        research_tree_dragging = True
        last_research_mouse_pos = mouse_pos

# Function to handle research tree dragging
def handle_research_tree_drag(mouse_pos):
    global research_tree_offset_x, research_tree_offset_y, last_research_mouse_pos
    if research_tree_dragging and last_research_mouse_pos:
        dx = mouse_pos[0] - last_research_mouse_pos[0]
        dy = mouse_pos[1] - last_research_mouse_pos[1]
        research_tree_offset_x += dx
        research_tree_offset_y += dy
        last_research_mouse_pos = mouse_pos

# Function to stop dragging the research tree
def stop_research_tree_drag():
    global research_tree_dragging, last_research_mouse_pos
    research_tree_dragging = False
    last_research_mouse_pos = None

# Function to handle research tree zooming
def handle_research_tree_zoom(event):
    global research_tree_zoom, research_tree_offset_x, research_tree_offset_y
    if event.y > 0:
        new_zoom = min(research_tree_zoom + research_tree_zoom_step, max_research_tree_zoom)
    elif event.y < 0:
        new_zoom = max(research_tree_zoom - research_tree_zoom_step, min_research_tree_zoom)
    else:
        return

    # Adjust offsets to zoom around the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    offset_x = (mouse_x - research_tree_offset_x) / research_tree_zoom
    offset_y = (mouse_y - research_tree_offset_y) / research_tree_zoom
    research_tree_offset_x -= int(offset_x * (new_zoom - research_tree_zoom))
    research_tree_offset_y -= int(offset_y * (new_zoom - research_tree_zoom))
    research_tree_zoom = new_zoom

# Function to render locked tiles with a grey overlay and tooltips
def render_locked_tiles_with_tooltips(surface, offset_x, offset_y, zoom, mouse_pos):
    tooltip_data = None  # Store tooltip data to render it last

    if destroy_mode or selected_building:  # Disable tooltips and purchasing in build or destroy mode
        for region_name, region_data in locked_tiles.items():
            if region_data["locked"]:
                for grid_x, grid_y in region_data["tiles"]:
                    tile_x = grid_x * int(tilemap.tilewidth * zoom) + offset_x
                    tile_y = grid_y * int(tilemap.tileheight * zoom) + offset_y
                    grey_overlay = pygame.Surface((int(tilemap.tilewidth * zoom), int(tilemap.tileheight * zoom)), pygame.SRCALPHA)
                    grey_overlay.fill((50, 50, 50, 150)) 
                    surface.blit(grey_overlay, (tile_x, tile_y))
        return

    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    for region_name, region_data in locked_tiles.items():
        if region_data["locked"]:  # Only render locked tiles for locked regions
            # Determine if the mouse is hovering over any tile in the region
            hovering = False
            for grid_x, grid_y in region_data["tiles"]:
                tile_x = grid_x * tile_width + offset_x
                tile_y = grid_y * tile_height + offset_y
                tile_rect = pygame.Rect(tile_x, tile_y, tile_width, tile_height)
                if tile_rect.collidepoint(mouse_pos):
                    hovering = True
                    break

            # Highlight locked tiles with a different color if hovering
            for grid_x, grid_y in region_data["tiles"]:
                tile_x = grid_x * tile_width + offset_x
                tile_y = grid_y * tile_height + offset_y
                grey_overlay = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                if hovering:
                    grey_overlay.fill((100, 100, 255, 150))  # Blue overlay for hovering
                else:
                    grey_overlay.fill((50, 50, 50, 150)) 
                surface.blit(grey_overlay, (tile_x, tile_y))

            # Store tooltip data if hovering
            if hovering:
                tooltip_data = {
                    "region_name": region_name,
                    "mouse_pos": mouse_pos,
                    "price": region_data["price"]
                }

    # Render the tooltip last to ensure it appears on top
    if tooltip_data:
        render_tooltip(
            tooltip_data["region_name"],
            (tooltip_data["mouse_pos"][0] + 15, tooltip_data["mouse_pos"][1] + 15),  # Tooltip follows the mouse
            show_cost=False,
            additional_lines=[(f"Price: ${tooltip_data['price']}", (255, 255, 0))] 
        )

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
    # Ensure locked tiles and their tooltips are rendered last
    render_locked_tiles_with_tooltips(surface, offset_x, offset_y, zoom, pygame.mouse.get_pos())

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

# Function to render placed blocks with hover effect in destroy mode and tooltips
def render_placed_blocks(surface, placed_blocks, offset_x, offset_y, zoom, mouse_pos):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)
    tooltip_data = None  # Store tooltip data to render it last

    for (grid_x, grid_y), block_image in placed_blocks.items():
        block_x = grid_x * tile_width + offset_x
        block_y = grid_y * tile_height + offset_y
        scaled_image = pygame.transform.scale(block_image, (tile_width, tile_height))

        # Grey out the block if it's out of ticks
        building_name = building_mapping.get(block_image)
        if building_name in power_plant_ticks and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0:
            greyed_out_image = scaled_image.copy()
            greyed_out_image.fill((128, 128, 128, 150), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(greyed_out_image, (block_x, block_y))
        else:
            surface.blit(scaled_image, (block_x, block_y))

        # Render hover effect in destroy mode
        if destroy_mode and block_x <= mouse_pos[0] < block_x + tile_width and block_y <= mouse_pos[1] < block_y + tile_height:
            tinted_image = scaled_image.copy()
            tinted_image.fill((255, 0, 0, 205), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted_image, (block_x, block_y))

        # Store tooltip data if hovering over the block
        if block_x <= mouse_pos[0] < block_x + tile_width and block_y <= mouse_pos[1] < block_y + tile_height:
            ticks_left = placed_power_plant_ticks.get((grid_x, grid_y), None)
            tooltip_data = (building_name, (mouse_pos[0] + 15, mouse_pos[1] + 15), ticks_left)

    # Render the tooltip last to ensure it appears on top
    if tooltip_data:
        render_tooltip(*tooltip_data)

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
    global research, research_ps
    added_research = 0
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[0]) * lab1_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[1]) * lab2_research_per_second
    added_research += sum(1 for block_image in placed_blocks.values() if block_image == lab_images[2]) * lab3_research_per_second
    research += added_research
    research_ps = round(added_research, 2)

# Function to update power points based on placed power plants
def update_power():
    global power, power_ps, money
    added_power = 0

    for (grid_x, grid_y), block_image in placed_blocks.items():
        building_name = building_mapping.get(block_image)
        if building_name in power_plant_ticks:
            # Check if the power plant has remaining ticks
            if placed_power_plant_ticks.get((grid_x, grid_y), 0) > 0:
                if building_name == "wind_turbine":
                    added_power += wind_turbine_power_per_second
                elif building_name == "solar_panel":
                    added_power += solar_panel_power_per_second
                elif building_name == "coal_plant":
                    added_power += coal_plant_power_per_second
                elif building_name == "nuclear_plant":
                    added_power += nuclear_plant_power_per_second
                elif building_name == "fusion_plant":
                    added_power += fusion_plant_power_per_second

                # Decrease the tick counter
                placed_power_plant_ticks[(grid_x, grid_y)] -= 1
            elif building_name == "wind_turbine" and auto_repair_wind_turbines:
                # Automatically repair wind turbines if the upgrade is active
                repair_cost = max(1, int(building_prices[building_name] * repair_cost_percentage)) 
                if money >= repair_cost:
                    money -= repair_cost
                    placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[building_name]

    power += added_power
    power_ps = round(added_power, 2)
    power = min(power, max_power)

# Function to convert power into money based on placed houses
def update_money():
    global money, money_ps, power
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
    money_ps = round(earned_money, 2)

# Function to format building names for tooltips
def format_building_name(building_name):
    return building_name.replace("_", " ").title()

# Function to render tooltips
def render_tooltip(building, position, ticks_left=None, show_cost=False, additional_lines=None):
    font = pygame.font.Font(None, 21)
    lines = []

    if building in locked_tiles: 
        lines.append((building, (255, 255, 255)))  
        lines.append(("Unlockable Region", (255, 255, 255)))  
    elif building in ["lab1", "lab2", "lab3"]:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, (255, 255, 255)))  
        lines.append((f"Produces Research", (255, 255, 255)))  
        if show_cost:
            cost_color = (0, 255, 0) if money >= building_prices[building] else (255, 0, 0)  
            lines.append((f"Cost: ${building_prices[building]}", cost_color))
        lines.append((f"Produces: {lab1_research_per_second if building == 'lab1' else lab2_research_per_second if building == 'lab2' else lab3_research_per_second} RP/s", (255, 255, 0)))  
    elif building in ["house1", "house2", "house3"]:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, (255, 255, 255)))  
        lines.append((f"Produces Money", (255, 255, 255)))  
        if show_cost:
            cost_color = (0, 255, 0) if money >= building_prices[building] else (255, 0, 0)  
            lines.append((f"Cost: ${building_prices[building]}", cost_color))
        lines.append((f"Converts: {house1_money_per_second if building == 'house1' else house2_money_per_second if building == 'house2' else house3_money_per_second} MW/s", (255, 255, 0)))  
    elif building in ["battery1", "battery2"]:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, (255, 255, 255)))  
        lines.append((f"Stores Power", (255, 255, 255)))  
        if show_cost:
            cost_color = (0, 255, 0) if money >= building_prices[building] else (255, 0, 0)  
            lines.append((f"Cost: ${building_prices[building]}", cost_color))
        lines.append((f"Stores: {battery1_power if building == 'battery1' else battery2_power} Power", (255, 255, 0)))  
    elif building in ["coal_plant", "nuclear_plant", "fusion_plant", "wind_turbine", "solar_panel"]:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, (255, 255, 255)))  
        lines.append((f"Produces Power", (255, 255, 255)))  
        if ticks_left is not None:
            if ticks_left <= 0:
                lines.append((f"Status: Broken", (255, 0, 0)))
                repair_cost = round(building_prices[building] * repair_cost_percentage, 2)  # Correctly calculate repair cost
                lines.append((f"Repair Cost: ${repair_cost}", (255, 255, 0)))
            else:
                lines.append((f"Status: Operational", (0, 255, 0)))
        if show_cost:
            cost_color = (0, 255, 0) if money >= building_prices[building] else (255, 0, 0)
            lines.append((f"Cost: ${building_prices[building]}", cost_color))
        lines.append((f"Produces: {wind_turbine_power_per_second if building == 'wind_turbine' else solar_panel_power_per_second if building == 'solar_panel' else coal_plant_power_per_second if building == 'coal_plant' else nuclear_plant_power_per_second if building == 'nuclear_plant' else fusion_plant_power_per_second} MW/s", (255, 255, 0)))  # Yellow
        if ticks_left is not None:
            lines.append((f"Ticks Left: {ticks_left} / {power_plant_ticks[building]}",(255, 0, 255)))

    # Add additional lines if provided
    if additional_lines:
        lines.extend(additional_lines)

    # Render each line and calculate the tooltip size
    rendered_lines = [font.render(line[0], True, line[1]) for line in lines]
    line_height = font.get_linesize() + 5  # Add extra spacing between lines
    tooltip_width = max(line.get_width() for line in rendered_lines) + 10
    tooltip_height = len(rendered_lines) * line_height + 10

    # Create a transparent surface for the tooltip background
    tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    pygame.draw.rect(tooltip_surface, (20, 20, 20, 200), (0, 0, tooltip_width, tooltip_height), border_radius=7)

    # Draw the background
    screen.blit(tooltip_surface, position)

    # Draw each line of text
    for i, line_surface in enumerate(rendered_lines):
        screen.blit(line_surface, (position[0] + 5, position[1] + 5 + i * line_height))

# Adjust GUI rendering to include tooltips
def render_gui():
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)

    global destroy_button_rect, research_button_rect, sell_power_button_rect, unlock_button_rect
    
    if money_ps == 0:
        text(f"Money: ${round(money, 2)}", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))
    else:
        text(f"Money: ${round(money, 2)} + {round(money_ps, 2)}/s", 28, (255, 255, 255), (20, 20 - gui_scroll_offset))

    if power_ps == 0:
        text(f"Power: {round(power, 2)} MW / {max_power} MW", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))
    else:
        text(f"Power: {round(power, 2)} MW / {max_power} MW + {round(power_ps, 2)}/s", 28, (255, 255, 255), (20, 60 - gui_scroll_offset))

    if research_ps == 0:
        text(f"Research: {round(research, 2)} RP", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))
    else:
        text(f"Research: {round(research, 2)} RP + {round(research_ps, 2)}/s", 28, (255, 255, 255), (20, 100 - gui_scroll_offset))

    if pollution_ps == 0:
        text(f"Pollution: {round(pollution, 2)} / {max_pollution}", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))
    else:
        text(f"Pollution: {round(pollution, 2)} / {max_pollution} + {round(pollution_ps, 2)}/s", 28, (255, 255, 255), (20, 140 - gui_scroll_offset))

    research_button_rect = text("Research", 24, (255, 255, 255), (20, 180 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    destroy_button_rect = text("Destroy: ON" if destroy_mode else "Destroy: OFF", 24, (255, 255, 255), (20, 220 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    sell_power_button_rect = text("Sell Power", 24, (255, 255, 255), (20, 260 - gui_scroll_offset), True, (120, 35), (100, 100, 100))
    text("Buildings: ", 30, (255, 255, 255), (20, 320 - gui_scroll_offset))
    text("- Power plants", 24, (200, 200, 200), (40, 360 - gui_scroll_offset))
    text("- Labs", 24, (200, 200, 200), (40, 440 - gui_scroll_offset))
    text("- Houses", 24, (200, 200, 200), (40, 520 - gui_scroll_offset))
    text("- Batterys", 24, (200, 200, 200), (40, 600 - gui_scroll_offset))

    global power_plant_buttons, lab_buttons, house_buttons, battery_buttons

    power_plant_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 380 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(5)]
    lab_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 460 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    house_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 540 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(3)]
    battery_buttons = [text("", 24, (255, 255, 255), (60 + i * 50, 620 - gui_scroll_offset), True, (40, 40), (100, 100, 100)) for i in range(2)]

    for i, img in enumerate(power_plant_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 380 + 10 - gui_scroll_offset))

    for i, img in enumerate(lab_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 460 + 10 - gui_scroll_offset))

    for i, img in enumerate(house_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 540 + 10 - gui_scroll_offset))

    for i, img in enumerate(battery_images):
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 620 + 10 - gui_scroll_offset))

    # Handle tooltips for hovering over buttons
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_groups = [
        (power_plant_buttons, list(building_mapping.values())[:5]),
        (lab_buttons, list(building_mapping.values())[5:8]),
        (house_buttons, list(building_mapping.values())[8:11]),
        (battery_buttons, list(building_mapping.values())[11:]),
    ]

    for buttons, buildings in button_groups:
        for i, rect in enumerate(buttons):
            if rect.collidepoint(mouse_x, mouse_y):
                render_tooltip(buildings[i], (mouse_x + 15, mouse_y), show_cost=True)
                break

# Handle block restoration when clicking on a broken building
def handle_repair(grid_x, grid_y):
    if destroy_mode:
        # Do not allow repairs when destroy mode is active
        return

    if (grid_x, grid_y) in placed_blocks:
        block_image = placed_blocks[(grid_x, grid_y)]
        building_name = building_mapping.get(block_image)

        # Check if the building is broken and restore it
        if building_name in power_plant_ticks and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0:
            repair_cost = max(repair_cost_percentage, round(building_prices[building_name] * repair_cost_percentage, 2))
            global money
            if money >= repair_cost:
                money -= repair_cost
                placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[building_name]

                repair_sound1 = pygame.mixer.Sound("Sound_Effects/rachet_click.mp3")
                repair_sound2 = pygame.mixer.Sound("Sound_Effects/repair_metal.mp3")

                repair_sound1.set_volume(0.5)
                repair_sound2.set_volume(0.5)

                repair_sound1.play()
                repair_sound2.play()

# Function to unlock a region
def unlock_region(region_name):
    global money
    if region_name in locked_tiles and locked_tiles[region_name]["locked"]:
        price = locked_tiles[region_name]["price"]
        if money >= price:
            money -= price
            locked_tiles[region_name]["locked"] = False
            print(f"Unlocked {region_name} for ${price}.")
            unlock_sound = pygame.mixer.Sound("Sound_Effects/unlock_region.mp3")
            unlock_sound.play()
        else:
            print("Not enough money to unlock this region!")

# Function to check if a tile is locked
def is_tile_locked(grid_x, grid_y):
    for region_name, region_data in locked_tiles.items():
        if region_data["locked"] and (grid_x, grid_y) in region_data["tiles"]:
            return True
    return False

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

        elif research_tree_open and event.type == pygame.MOUSEBUTTONDOWN:
            # Handle clicks only for the research tree when it is open
            handle_research_tree_click(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            stop_research_tree_drag()

        elif event.type == pygame.MOUSEMOTION:
            handle_research_tree_drag(event.pos)

        elif not research_tree_open and event.type == pygame.MOUSEBUTTONDOWN:
            # Handle other interactions only when the research tree is closed
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
                # Open the research tree
                research_tree_open = True

            if sell_power_button_rect and sell_power_button_rect.collidepoint((mouse_x, mouse_y)):
                # Sell all power and convert it into money
                money += power
                power = 0

            # Handle GUI button clicks
            if gui_rect.collidepoint(mouse_x, mouse_y):
                # Process GUI interactions
                for i, rect in enumerate(power_plant_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == power_plant_images[i]:
                            # Deselect if already selected
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = power_plant_images[i]
                            show_grid = True
                            destroy_mode = False
                        break

                for i, rect in enumerate(lab_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == lab_images[i]:
                            # Deselect if already selected
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = lab_images[i]
                            show_grid = True
                            destroy_mode = False
                        break

                for i, rect in enumerate(house_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == house_images[i]:
                            # Deselect if already selected
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = house_images[i]
                            show_grid = True
                            destroy_mode = False
                        break

                for i, rect in enumerate(battery_buttons):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if selected_building == battery_images[i]:
                            # Deselect if already selected
                            selected_building = None
                            show_grid = False
                        else:
                            selected_building = battery_images[i]
                            show_grid = True
                            destroy_mode = False
                        break

            # Handle region unlocking
            if not destroy_mode and not selected_building:  # Allow region purchasing only if not in build or destroy mode
                if event.button == 1:  # Only allow unlocking with left click
                    for region_name, region_data in locked_tiles.items():
                        if region_data["locked"]:
                            for grid_x, grid_y in region_data["tiles"]:
                                tile_width = int(tilemap.tilewidth * zoom)
                                tile_height = int(tilemap.tileheight * zoom)
                                tile_rect = pygame.Rect(
                                    grid_x * tile_width + gui_width + camera_x,
                                    grid_y * tile_height + camera_y,
                                    tile_width,
                                    tile_height,
                                )
                                if tile_rect.collidepoint(mouse_x, mouse_y):
                                    unlock_region(region_name)
                                    break

            # Handle repairing buildings regardless of build mode
            if not destroy_mode:
                grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))
                handle_repair(grid_x, grid_y)

            # Handle block destruction in destroy mode
            if show_grid and destroy_mode:
                grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in valid_tiles:
                    if event.button == 1:
                        if (grid_x, grid_y) in placed_blocks:
                            block_image = placed_blocks[(grid_x, grid_y)]
                            building_name = building_mapping[block_image]
                            building_cost = building_prices[building_name]

                            # Calculate the refund based on sell_percentage
                            refund = round(building_cost * sell_percentage, 2)
                            money += refund

                            # Remove the block and update max power
                            del placed_blocks[(grid_x, grid_y)]
                            update_max_power()

            elif show_grid and not destroy_mode:
                # Handle block placement and restoration
                grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in placed_blocks:
                    block_image = placed_blocks[(grid_x, grid_y)]
                    building_name = building_mapping.get(block_image)

                    # Check if the building is broken and restore it
                    if building_name in power_plant_ticks and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0:
                        repair_cost = max(1, int(building_prices[building_name] * repair_cost_percentage))
                        if money >= repair_cost:
                            money -= repair_cost
                            placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[building_name]

                elif (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks and can_place_building(grid_x, grid_y):
                    if is_tile_locked(grid_x, grid_y):
                        print("This tile is locked behind a region. Unlock the region to build here.")
                    else:
                        if event.button == 1 and selected_building:
                            building_name = building_mapping[selected_building]
                            building_cost = building_prices[building_name]

                            if money >= building_cost:
                                money -= building_cost
                                placed_blocks[(grid_x, grid_y)] = selected_building

                                # Initialize tick counter for power plants
                                if building_name in power_plant_ticks:
                                    placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[building_name]

                                update_max_power()
                                build_sound = pygame.mixer.Sound("Sound_Effects/lego_building.mp3")
                                build_sound.play()

            if event.button == 3:
                # Start dragging the map
                dragging = True
                last_mouse_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_research_tree_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                stop_research_tree_drag()

            elif event.type == pygame.MOUSEMOTION:
                handle_research_tree_drag(event.pos)

            elif event.type == pygame.MOUSEWHEEL:
                handle_research_tree_zoom(event)

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