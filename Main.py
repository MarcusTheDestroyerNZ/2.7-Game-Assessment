import pygame
import sys
from pytmx.util_pygame import load_pygame
import os
import json
import datetime
from CodeFiles import notifications
from CodeFiles import locked_tiles

pygame.init()

now = datetime.datetime.now()
print(now.strftime("%d-%m-%Y %H:%M:%S"))

os.environ["SDL_VIDEO_CENTERED"] = "1"
screen_width = 1200
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Sustainable Energy Game")

info = pygame.display.Info()
new_screen_width = info.current_w
new_screen_height = info.current_h

gui_width = new_screen_width * 0.3
gui_rect = pygame.Rect(0, 0, gui_width, new_screen_height)

tilemap = load_pygame("terrain_map.tmx")


# loads building statistics and properties from a JSON file
def load_game_variables():
    with open("./BuildingStats.json", "r") as f:
        return json.load(f)


# gets a specific statistic for a given building from the building stats dictionary
def get_building_stat(building, stat):
    return building_stats[building][stat]


game_variables = load_game_variables()
building_stats = game_variables

power_plant_images = [
    pygame.image.load("Assets/wind_turbine.png"),
    pygame.image.load("Assets/solar_panel.png"),
    pygame.image.load("Assets/coal_plant.png"),
    pygame.image.load("Assets/nuclear_plant.png"),
    pygame.image.load("Assets/fusion_plant.png"),
]

lab_images = [
    pygame.image.load("Assets/lab1.png"),
    pygame.image.load("Assets/lab2.png"),
    pygame.image.load("Assets/lab3.png"),
]

house_images = [
    pygame.image.load("Assets/house1.png"),
    pygame.image.load("Assets/house2.png"),
    pygame.image.load("Assets/house3.png"),
]

battery_images = [
    pygame.image.load("Assets/battery1.png"),
    pygame.image.load("Assets/battery2.png"),
]

# load the lock image
lock_image = pygame.image.load("Assets/lock.png")
lock_image = pygame.transform.scale(lock_image, (40, 40))

# dynamically load building variables
building_prices = {
    building: get_building_stat(building, "price") for building in building_stats
}

power_plant_ticks = {
    building: get_building_stat(building, "ticks")
    for building in building_stats
    if "ticks" in building_stats[building]
}

power_per_second = {
    building: get_building_stat(building, "power_per_second")
    for building in building_stats
    if "power_per_second" in building_stats[building]
}

research_per_second = {
    building: get_building_stat(building, "research_per_second")
    for building in building_stats
    if "research_per_second" in building_stats[building]
}

money_per_second = {
    building: get_building_stat(building, "money_per_second")
    for building in building_stats
    if "money_per_second" in building_stats[building]
}

battery_capacity = {
    building: get_building_stat(building, "capacity")
    for building in building_stats
    if "capacity" in building_stats[building]
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
    battery_images[1]: "battery2",
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

global money, money_ps, power, max_power, power_ps, research, research_ps, offline_percentage
money = 1
money_ps = 0
power = 0
max_power = 50
power_ps = 0
research = 0
research_ps = 0
pollution = 0
max_pollution = 1000
pollution_ps = 0

game_clock = pygame.time.Clock()
tick_interval = 1000
last_tick = pygame.time.get_ticks()

global research_button_rect
research_tree_open = False
research_button_rect = None

global sell_power_button_rect
sell_power_button_rect = None

# track remaining ticks for each placed power plant
placed_power_plant_ticks = {}

auto_repair_buildings = {
    "wind_turbine": False,
    "solar_panel": False,
    "coal_plant": False,
    "nuclear_plant": False,
    "fusion_plant": False,
}

# percentage of the building cost returned when selling
sell_percentage = 0.5
repair_cost_percentage = 0.5
offline_percentage = 0.25

# add unlock flags for buildings
building_unlocks = {
    "wind_turbine": True,  # wind turbines are unlocked by default
    "solar_panel": False,
    "coal_plant": False,
    "nuclear_plant": False,
    "fusion_plant": False,
    "lab1": False,
    "lab2": False,
    "lab3": False,
    "house1": False,
    "house2": False,
    "house3": False,
    "battery1": False,
    "battery2": False,
}


# update unlock flags in research effects
def unlock_building(building_name):
    global building_unlocks
    if building_name in building_unlocks:
        building_unlocks[building_name] = True
    else:
        print(f"Building {building_name} not found in unlocks.")


# define research upgrades
research_upgrades = [
    {
        "name": "Double Wind Turbine Ticks",
        "cost": 15,
        "currency": "money",
        "effect": lambda: handle_upgrade("wind_turbine", "Ticks"),
        "purchased": False,
    },
    {
        "name": "Double Wind Turbine Efficiency",
        "cost": 50,
        "currency": "research",
        "effect": lambda: handle_upgrade("wind_turbine", "Power Efficiency"),
        "purchased": False,
    },
    {
        "name": "Automatically Repair Wind Turbines",
        "cost": 100,
        "currency": "research",
        "effect": lambda: handle_upgrade("wind_turbine", "Auto Repair"),
        "purchased": False,
    },
    {
        "name": "Double Solar Panel Ticks",
        "cost": 3500,
        "currency": "research",
        "effect": lambda: handle_upgrade("solar_panel", "Ticks"),
        "purchased": False,
    },
    {
        "name": "Double Solar Panel Efficiency",
        "cost": 6000,
        "currency": "research",
        "effect": lambda: handle_upgrade("solar_panel", "Power Efficiency"),
        "purchased": False,
    },
    {
        "name": "Automatically Repair Solar Panels",
        "cost": 10000,
        "currency": "research",
        "effect": lambda: handle_upgrade("solar_panel", "Auto Repair"),
        "purchased": False,
    },
    {
        "name": "Double Coal Plant Ticks",
        "cost": 25000,
        "currency": "research",
        "effect": lambda: handle_upgrade("coal_plant", "Ticks"),
        "purchased": False,
    },
    {
        "name": "Double Coal Plant Efficiency",
        "cost": 35000,
        "currency": "research",
        "effect": lambda: handle_upgrade("coal_plant", "Power Efficiency"),
        "purchased": False,
    },
    {
        "name": "Automatically Repair Coal Plants",
        "cost": 50000,
        "currency": "research",
        "effect": lambda: handle_upgrade("coal_plant", "Auto Repair"),
        "purchased": False,
    },
    {
        "name": "Double Nuclear Plant Ticks",
        "cost": 75000,
        "currency": "research",
        "effect": lambda: handle_upgrade("nuclear_plant", "Ticks"),
        "purchased": False,
    },
    {
        "name": "Double Nuclear Plant Efficiency",
        "cost": 100000,
        "currency": "research",
        "effect": lambda: handle_upgrade("nuclear_plant", "Power Efficiency"),
        "purchased": False,
    },
    {
        "name": "Automatically Repair Nuclear Plants",
        "cost": 150000,
        "currency": "research",
        "effect": lambda: handle_upgrade("nuclear_plant", "Auto Repair"),
        "purchased": False,
    },
    {
        "name": "Double Fusion Plant Ticks",
        "cost": 250000,
        "currency": "research",
        "effect": lambda: handle_upgrade("fusion_plant", "Ticks"),
        "purchased": False,
    },
    {
        "name": "Double Fusion Plant Efficiency",
        "cost": 350000,
        "currency": "research",
        "effect": lambda: handle_upgrade("fusion_plant", "Power Efficiency"),
        "purchased": False,
    },
    {
        "name": "Automatically Repair Fusion Plants",
        "cost": 500000,
        "currency": "research",
        "effect": lambda: handle_upgrade("fusion_plant", "Auto Repair"),
        "purchased": False,
    },
    {
        "name": "Double Battery 1 Efficiency",
        "cost": 2500,
        "currency": "research",
        "effect": lambda: handle_upgrade("battery1", "Battery Efficiency"),
        "purchased": False,
    },
    {
        "name": "Double Battery 2 Efficiency",
        "cost": 50000,
        "currency": "research",
        "effect": lambda: handle_upgrade("battery2", "Battery Efficiency"),
        "purchased": False,
    },
    {
        "name": "Double House 1 Efficiency",
        "cost": 5000,
        "currency": "research",
        "effect": lambda: handle_upgrade("house1", "House Efficiency"),
        "purchased": False,
    },
    {
        "name": "Double House 2 Efficiency",
        "cost": 20000,
        "currency": "research",
        "effect": lambda: handle_upgrade("house2", "House Efficiency"),
        "purchased": False,
    },
    {
        "name": "Double House 3 Efficiency",
        "cost": 100000,
        "currency": "research",
        "effect": lambda: handle_upgrade("house3", "House Efficiency"),
        "purchased": False,
    },
    {
        "name": "Unlock Research Lab 1",
        "cost": 150,
        "currency": "money",
        "effect": lambda: handle_upgrade("lab1", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Research Lab 2",
        "cost": 5000,
        "currency": "research",
        "effect": lambda: handle_upgrade("lab2", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Research Lab 3",
        "cost": 50000,
        "currency": "research",
        "effect": lambda: handle_upgrade("lab3", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock House 1",
        "cost": 500,
        "currency": "research",
        "effect": lambda: handle_upgrade("house1", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock House 2",
        "cost": 10000,
        "currency": "research",
        "effect": lambda: handle_upgrade("house2", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock House 3",
        "cost": 50000,
        "currency": "research",
        "effect": lambda: handle_upgrade("house3", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Solar Panels",
        "cost": 1000,
        "currency": "research",
        "effect": lambda: handle_upgrade("solar_panel", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Coal Plant",
        "cost": 20000,
        "currency": "research",
        "effect": lambda: handle_upgrade("coal_plant", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Nuclear Plant",
        "cost": 75000,
        "currency": "research",
        "effect": lambda: handle_upgrade("nuclear_plant", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Fusion Plant",
        "cost": 200000,
        "currency": "research",
        "effect": lambda: handle_upgrade("fusion_plant", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Battery 1",
        "cost": 250,
        "currency": "research",
        "effect": lambda: handle_upgrade("battery1", "Unlock"),
        "purchased": False,
    },
    {
        "name": "Unlock Battery 2",
        "cost": 20000,
        "currency": "research",
        "effect": lambda: handle_upgrade("battery2", "Unlock"),
        "purchased": False,
    },
]

# define the research tree layout as a global variable
tree_layout = [
    # 1st node row
    [
        {
            "name": "Double Wind Turbine Ticks",
            "x": 0,
            "y": 500,
            "image": power_plant_images[0],
            "unlocks": ["Unlock Research Lab 1"],
        },
    ],
    # 2nd node row
    [
        {
            "name": "Unlock Research Lab 1",
            "x": 500,
            "y": 500,
            "image": lab_images[0],
            "unlocks": [
                "Unlock Solar Panels",
                "Unlock Research Lab 2",
                "Unlock Battery 1",
                "Double Wind Turbine Efficiency",
            ],
        },
    ],
    # 3rd node row
    [
        {
            "name": "Unlock Solar Panels",
            "x": 1000,
            "y": 100,
            "image": power_plant_images[1],
            "unlocks": ["Double Solar Panel Ticks", "Double Solar Panel Efficiency"],
        },
        {
            "name": "Unlock Research Lab 2",
            "x": 1000,
            "y": 300,
            "image": lab_images[1],
            "unlocks": ["Unlock Research Lab 3"],
        },
        {
            "name": "Unlock Battery 1",
            "x": 1000,
            "y": 700,
            "image": battery_images[0],
            "unlocks": [
                "Unlock Battery 2",
                "Unlock House 1",
                "Double Battery 1 Efficiency",
            ],
        },
        {
            "name": "Double Wind Turbine Efficiency",
            "x": 1000,
            "y": 900,
            "image": power_plant_images[0],
            "unlocks": ["Automatically Repair Wind Turbines"],
        },
    ],
    # 4th node row
    [
        {
            "name": "Double Solar Panel Ticks",
            "x": 1500,
            "y": -100,
            "image": power_plant_images[1],
            "unlocks": ["Automatically Repair Solar Panels"],
        },
        {
            "name": "Double Solar Panel Efficiency",
            "x": 1500,
            "y": 100,
            "image": power_plant_images[1],
            "unlocks": ["Unlock Coal Plant"],
        },
        {
            "name": "Unlock Research Lab 3",
            "x": 1500,
            "y": 300,
            "image": lab_images[2],
            "unlocks": [],
        },
        {
            "name": "Unlock Battery 2",
            "x": 1500,
            "y": 500,
            "image": battery_images[1],
            "unlocks": ["Double Battery 2 Efficiency"],
        },
        {
            "name": "Unlock House 1",
            "x": 1500,
            "y": 900,
            "image": house_images[0],
            "unlocks": ["Unlock House 2", "Double House 1 Efficiency"],
        },
        {
            "name": "Double Battery 1 Efficiency",
            "x": 1500,
            "y": 700,
            "image": battery_images[0],
            "unlocks": [""],
        },
        {
            "name": "Automatically Repair Wind Turbines",
            "x": 1500,
            "y": 1100,
            "image": power_plant_images[0],
            "unlocks": [],
        },
    ],
    # 5th node row
    [
        {
            "name": "Automatically Repair Solar Panels",
            "x": 2000,
            "y": -100,
            "image": power_plant_images[1],
            "unlocks": [],
        },
        {
            "name": "Unlock Coal Plant",
            "x": 2000,
            "y": 100,
            "image": power_plant_images[2],
            "unlocks": ["Double Coal Plant Ticks", "Double Coal Plant Efficiency"],
        },
        {
            "name": "Double Battery 2 Efficiency",
            "x": 2000,
            "y": 500,
            "image": battery_images[1],
            "unlocks": [],
        },
        {
            "name": "Unlock House 2",
            "x": 2000,
            "y": 900,
            "image": house_images[1],
            "unlocks": ["Unlock House 3", "Double House 2 Efficiency"],
        },
        {
            "name": "Double House 1 Efficiency",
            "x": 2000,
            "y": 1100,
            "image": house_images[0],
            "unlocks": [""],
        },
    ],
    # 6th node row
    [
        {
            "name": "Double Coal Plant Ticks",
            "x": 2500,
            "y": -100,
            "image": power_plant_images[2],
            "unlocks": ["Automatically Repair Coal Plants"],
        },
        {
            "name": "Double Coal Plant Efficiency",
            "x": 2500,
            "y": 100,
            "image": power_plant_images[2],
            "unlocks": ["Unlock Nuclear Plant"],
        },
        {
            "name": "Unlock House 3",
            "x": 2500,
            "y": 900,
            "image": house_images[2],
            "unlocks": ["Double House 3 Efficiency"],
        },
        {
            "name": "Double House 2 Efficiency",
            "x": 2500,
            "y": 1100,
            "image": house_images[1],
            "unlocks": [""],
        },
    ],
    # 7th node row
    [
        {
            "name": "Automatically Repair Coal Plants",
            "x": 3000,
            "y": -100,
            "image": power_plant_images[2],
            "unlocks": [],
        },
        {
            "name": "Unlock Nuclear Plant",
            "x": 3000,
            "y": 100,
            "image": power_plant_images[3],
            "unlocks": [
                "Double Nuclear Plant Ticks",
                "Double Nuclear Plant Efficiency",
            ],
        },
        {
            "name": "Double House 3 Efficiency",
            "x": 3000,
            "y": 1100,
            "image": house_images[2],
            "unlocks": [""],
        },
    ],
    # 8th node row
    [
        {
            "name": "Double Nuclear Plant Ticks",
            "x": 3500,
            "y": -100,
            "image": power_plant_images[3],
            "unlocks": ["Automatically Repair Nuclear Plants"],
        },
        {
            "name": "Double Nuclear Plant Efficiency",
            "x": 3500,
            "y": 100,
            "image": power_plant_images[3],
            "unlocks": ["Unlock Fusion Plant"],
        },
    ],
    # 9th node row
    [
        {
            "name": "Automatically Repair Nuclear Plants",
            "x": 4000,
            "y": -100,
            "image": power_plant_images[3],
            "unlocks": [],
        },
        {
            "name": "Unlock Fusion Plant",
            "x": 4000,
            "y": 100,
            "image": power_plant_images[4],
            "unlocks": ["Double Fusion Plant Ticks", "Double Fusion Plant Efficiency"],
        },
    ],
    # 10th node row
    [
        {
            "name": "Double Fusion Plant Ticks",
            "x": 4500,
            "y": -100,
            "image": power_plant_images[4],
            "unlocks": ["Automatically Repair Fusion Plants"],
        },
        {
            "name": "Double Fusion Plant Efficiency",
            "x": 4500,
            "y": 100,
            "image": power_plant_images[4],
            "unlocks": [],
        },
    ],
    # 11th node row
    [
        {
            "name": "Automatically Repair Fusion Plants",
            "x": 5000,
            "y": -100,
            "image": power_plant_images[4],
            "unlocks": [],
        },
    ],
]


def handle_upgrade(name, upgrade):
    if upgrade == "Unlock":
        unlock_building(name)
        print(f"Unlocked: {name}")
    elif upgrade == "Power Efficiency":
        power_per_second[name] *= 2
        print(f"Power Efficiency: {name}")
    elif upgrade == "House Efficiency":
        money_per_second[name] *= 2
        print(f"House Efficiency: {name}")
        print(f"New Money per Second for {name}: {money_per_second[name]}")
    elif upgrade == "Battery Efficiency":
        battery_capacity[name] *= 2
        update_max_power()
        print(f"Battery Efficiency: {name}")
    elif upgrade == "Ticks":
        power_plant_ticks[name] *= 2
        print(f"Ticks: {name}")
    elif upgrade == "Auto Repair":
        auto_repair_buildings[name] = True
        print(f"Auto Repair: {name}")
    else:
        print(f"Unknown: Name: {name}, Upgrade: {upgrade}")


# variables for research tree movement and zoom
research_tree_offset_x = 100
research_tree_offset_y = 250
research_tree_dragging = False
last_research_mouse_pos = None
research_tree_zoom = 0.4
research_tree_zoom_step = 0.1
min_research_tree_zoom = 0.3
max_research_tree_zoom = 0.7

# load the custom font
custom_font = pygame.font.Font("Assets/font.ttf", 18)


# saves current game state including resources, buildings, and upgrades to a JSON file
def save_player_data():
    print(now.strftime("%d-%m-%Y %H:%M:%S")),
    player_data = {
        "time_logged_out": now.strftime("%d-%m-%Y %H:%M:%S"),
        "money": money,
        "research": research,
        "power": power,
        "max_power": max_power,
        "money_ps": money_ps,
        "research_ps": research_ps,
        "upgrades": {
            upgrade["name"]: upgrade["purchased"] for upgrade in research_upgrades
        },
        "placed_blocks": {
            f"{grid_x},{grid_y}": building_mapping[block_image]
            for (grid_x, grid_y), block_image in placed_blocks.items()
        },
        "placed_power_plant_ticks": {
            f"{grid_x},{grid_y}": ticks
            for (grid_x, grid_y), ticks in placed_power_plant_ticks.items()
        },
        "unlocked_areas": {
            region_name: not region_data["locked"]
            for region_name, region_data in locked_tiles.locked_tiles.items()
        },
    }
    with open("playerData.json", "w") as f:
        json.dump(player_data, f, indent=4)


# loads previously saved game state and applies all research upgrades and building placements
def load_player_data():
    global money, research, power, max_power, placed_blocks, placed_power_plant_ticks, idle_seconds, money_ps, research_ps
    try:
        with open("playerData.json", "r") as f:
            player_data = json.load(f)
            if not player_data:
                print("Empty save file detected. Starting a new game.")
                return

            money = player_data.get("money", money)
            research = player_data.get("research", research)
            power = player_data.get("power", power)
            max_power = player_data.get("max_power", max_power)
            money_ps = player_data.get("money_ps", money_ps)
            research_ps = player_data.get("research_ps", research_ps)

            for upgrade in research_upgrades:
                upgrade["purchased"] = player_data.get("upgrades", {}).get(
                    upgrade["name"], upgrade["purchased"]
                )
                if upgrade["purchased"]:
                    upgrade["effect"]()

            saved_blocks = player_data.get("placed_blocks", {})
            placed_blocks.clear()  

            for pos_str, building_name in saved_blocks.items():
                try:
                    grid_x, grid_y = map(int, pos_str.split(","))
                    # find the corresponding image
                    for img, name in building_mapping.items():
                        if name == building_name:
                            placed_blocks[(grid_x, grid_y)] = img
                            break
                except Exception as e:
                    print(f"Error loading building at {pos_str}: {e}")

            # load power plant ticks after buildings are placed
            saved_ticks = player_data.get("placed_power_plant_ticks", {})
            placed_power_plant_ticks.clear() 

            for pos_str, ticks in saved_ticks.items():
                try:
                    grid_x, grid_y = map(int, pos_str.split(","))
                    placed_power_plant_ticks[(grid_x, grid_y)] = ticks
                except Exception as e:
                    print(f"Error loading ticks at {pos_str}: {e}")

            # calculate idle time after everything else is loaded
            time_logged_out = player_data.get(
                "time_logged_out", now.strftime("%d-%m-%Y %H:%M:%S")
            )
            idle_seconds = calculate_time_difference(
                time_logged_out, now.strftime("%d-%m-%Y %H:%M:%S")
            )

            # load unlocked areas last
            unlocked_areas = player_data.get("unlocked_areas", {})
            for region_name, unlocked in unlocked_areas.items():
                if region_name in locked_tiles.locked_tiles:
                    locked_tiles.locked_tiles[region_name]["locked"] = not unlocked

            print(f"Successfully loaded save file with {len(placed_blocks)} buildings")
            idle_reward()

            update_max_power()

    except FileNotFoundError:
        print("No save file found. Starting a new game.")
    except json.JSONDecodeError:
        print("Save file corrupted. Starting a new game.")
    except Exception as e:
        print(f"Error loading save file: {e}")
        print("Starting a new game.")


# calculates the time difference in seconds between two timestamps
def calculate_time_difference(start_time, end_time):
    # convert string timestamps to datetime objects
    start = datetime.datetime.strptime(start_time, "%d-%m-%Y %H:%M:%S")
    end = datetime.datetime.strptime(end_time, "%d-%m-%Y %H:%M:%S")

    # calculate time difference
    time_difference = end - start

    # get total seconds
    seconds_difference = time_difference.total_seconds()

    if seconds_difference > 0:
        return seconds_difference
    else:
        print("Wow you are from the future?")
        return 0


# processes offline progress and rewards player for time away from the game
def idle_reward():
    global money, research, money_ps, research_ps, idle_seconds, power, placed_power_plant_ticks

    ticks_passed = int(idle_seconds)
    offline_money = 0
    offline_research = 0
    offline_power = 0

    # first calculate total power generation for this tick
    for (grid_x, grid_y), block_image in list(placed_blocks.items()):
        building_name = building_mapping[block_image]

        if building_name in power_plant_ticks:
            current_ticks = placed_power_plant_ticks.get((grid_x, grid_y), 0)
            building_max_ticks = power_plant_ticks[building_name]

            if current_ticks > 0:
                productive_seconds = min(current_ticks, ticks_passed)
                if building_name in power_per_second:
                    offline_power += (
                        power_per_second[building_name]
                        * productive_seconds
                        * offline_percentage
                    )

                remaining_ticks = max(0, current_ticks - ticks_passed)
                placed_power_plant_ticks[(grid_x, grid_y)] = remaining_ticks

                # auto-repairs
                if remaining_ticks == 0:
                    auto_repair_enabled = (
                        (
                            building_name == "wind_turbine"
                            and auto_repair_buildings("wind_turbine")
                        )
                        or (
                            building_name == "solar_panel"
                            and auto_repair_buildings("solar_panel")
                        )
                        or (
                            building_name == "coal_plant"
                            and auto_repair_buildings("coal_plant")
                        )
                        or (
                            building_name == "nuclear_plant"
                            and auto_repair_buildings("nuclear_plant")
                        )
                        or (
                            building_name == "fusion_plant"
                            and auto_repair_buildings("fusion_plant")
                        )
                    )

                    if auto_repair_enabled:
                        remaining_time = ticks_passed - productive_seconds
                        if remaining_time > 0:
                            repairs_needed = remaining_time // building_max_ticks
                            repair_cost = (
                                building_prices[building_name] * repair_cost_percentage
                            )
                            total_repair_cost = repair_cost * repairs_needed

                            if (
                                offline_money >= total_repair_cost
                                and repairs_needed > 0
                            ):
                                offline_money -= total_repair_cost
                                complete_cycles = repairs_needed * building_max_ticks
                                offline_power += (
                                    power_per_second[building_name]
                                    * complete_cycles
                                    * offline_percentage
                                )

                                final_ticks = building_max_ticks - (
                                    remaining_time % building_max_ticks
                                )
                                placed_power_plant_ticks[(grid_x, grid_y)] = final_ticks
                            elif money >= total_repair_cost and repairs_needed > 0:
                                money -= total_repair_cost
                                complete_cycles = repairs_needed * building_max_ticks
                                offline_power += (
                                    power_per_second[building_name]
                                    * complete_cycles
                                    * offline_percentage
                                )

                                final_ticks = building_max_ticks - (
                                    remaining_time % building_max_ticks
                                )
                                placed_power_plant_ticks[(grid_x, grid_y)] = final_ticks

        # labs (these work independently of power)
        elif building_name in research_per_second:
            earned = (
                research_per_second[building_name] * ticks_passed * offline_percentage
            )
            offline_research += earned

    # process houses after we know how much power was generated
    required_power = 0
    for (grid_x, grid_y), block_image in placed_blocks.items():
        building_name = building_mapping[block_image]
        if building_name in money_per_second:
            required_power += money_per_second[building_name]

    # convert available power to money through houses
    if offline_power >= required_power:
        offline_money += required_power * ticks_passed * offline_percentage
    else:
        offline_money += offline_power * ticks_passed * offline_percentage

    money += offline_money
    research += offline_research
    # format idle time into days, hours, minutes, or seconds
    if idle_seconds >= 86400:
        idle_time_str = f"{int(idle_seconds // 86400)} days"
    elif idle_seconds >= 3600:
        idle_time_str = f"{int(idle_seconds // 3600)} hours"
    elif idle_seconds >= 60:
        idle_time_str = f"{int(idle_seconds // 60)} minutes"
    else:
        idle_time_str = f"{int(idle_seconds)} seconds"

    message = f"You were away for {idle_time_str} and earned ${format_number(offline_money)} and {format_number(offline_research)} research points while away!"
    notifications.create_popup("Welcome Back!", message)


# renders the research tree interface including nodes, connections and upgrade options
def render_research_tree():
    global back_button_rect
    screen.fill((50, 50, 50))

    # draw connections between nodes
    for i in range(len(tree_layout)):
        for node in tree_layout[i]:
            for unlock_name in node["unlocks"]:
                # find the target node in subsequent rows
                for j in range(i + 1, len(tree_layout)):
                    for next_node in tree_layout[j]:
                        if next_node["name"] == unlock_name:
                            # check if the target node is purchased
                            upgrade = next(
                                (
                                    u
                                    for u in research_upgrades
                                    if u["name"] == next_node["name"]
                                ),
                                None,
                            )
                            if upgrade:
                                prerequisites_met = all(
                                    prereq["purchased"]
                                    for prereq in research_upgrades
                                    if prereq["name"]
                                    in [
                                        n["name"]
                                        for t in tree_layout
                                        for n in t
                                        if next_node["name"] in n["unlocks"]
                                    ]
                                )
                                if upgrade["purchased"]:
                                    line_color = (0, 100, 250)
                                elif prerequisites_met:
                                    line_color = (
                                        0,
                                        200,
                                        0,
                                    )
                                else:
                                    line_color = (125, 50, 50)

                                # calculate the start and end points of the line
                                start_x = (
                                    node["x"] * research_tree_zoom
                                    + research_tree_offset_x
                                    + (300 * research_tree_zoom)
                                )  # right side of the left node
                                start_y = (
                                    node["y"] * research_tree_zoom
                                    + research_tree_offset_y
                                    + (100 * research_tree_zoom) / 2
                                )  # middle of the left node

                                end_x = (
                                    next_node["x"] * research_tree_zoom
                                    + research_tree_offset_x
                                )  # left side of the right node
                                end_y = (
                                    next_node["y"] * research_tree_zoom
                                    + research_tree_offset_y
                                    + (100 * research_tree_zoom) / 2
                                )  # middle of the right node

                                # draw the line
                                pygame.draw.line(
                                    screen,
                                    line_color,
                                    (start_x, start_y),
                                    (end_x, end_y),
                                    3,
                                )

    # draw research nodes with images, names, and prices
    for tier in tree_layout:
        for node in tier:
            upgrade = next(
                (u for u in research_upgrades if u["name"] == node["name"]), None
            )
            if upgrade:
                # check if all prerequisites are purchased
                prerequisites_met = all(
                    prereq["purchased"]
                    for prereq in research_upgrades
                    if prereq["name"]
                    in [
                        n["name"]
                        for t in tree_layout
                        for n in t
                        if node["name"] in n["unlocks"]
                    ]
                )
                affordable = (
                    money >= upgrade["cost"]
                    if upgrade["currency"] == "money"
                    else research >= upgrade["cost"]
                )
                if upgrade["purchased"]:
                    button_color = (0, 100, 250)
                elif affordable and prerequisites_met:
                    button_color = (0, 200, 0)
                else:
                    button_color = (115, 100, 100)

                button_rect = pygame.Rect(
                    node["x"] * research_tree_zoom + research_tree_offset_x,
                    node["y"] * research_tree_zoom + research_tree_offset_y,
                    300 * research_tree_zoom,
                    100 * research_tree_zoom,
                )
                corner_radius = int(
                    min(300 * research_tree_zoom, 100 * research_tree_zoom) // 6.4
                )
                pygame.draw.rect(screen, button_color, button_rect, 0, corner_radius)
                pygame.draw.rect(screen, (255, 255, 255), button_rect, 1, corner_radius)

                # assign the button_rect to the upgrade dictionary
                upgrade["button_rect"] = button_rect

                # draw the corresponding image on the left
                if "image" in node:
                    scaled_image = pygame.transform.scale(
                        node["image"],
                        (int(80 * research_tree_zoom), int(80 * research_tree_zoom)),
                    )
                    screen.blit(
                        scaled_image,
                        (
                            node["x"] * research_tree_zoom + 4 + research_tree_offset_x,
                            node["y"] * research_tree_zoom + 4 + research_tree_offset_y,
                        ),
                    )

                name_font_size = int((300 * research_tree_zoom) / 100)
                cost_font_size = int((300 * research_tree_zoom) / 50)

                # display the name and cost on the right
                upgrade_name = node["name"]
                words = upgrade_name.split()
                if len(upgrade_name) > 10 and len(words) > 1:
                    # split at the halfway point of the words
                    split_index = len(words) // 2
                    line1 = " ".join(words[:split_index])
                    line2 = " ".join(words[split_index:])
                    render_text(
                        line1,
                        name_font_size,
                        (255, 255, 255),
                        (
                            node["x"] * research_tree_zoom
                            + 100 * research_tree_zoom
                            + research_tree_offset_x,
                            node["y"] * research_tree_zoom
                            + 10 * research_tree_zoom
                            + research_tree_offset_y,
                        ),
                    )
                    render_text(
                        line2,
                        name_font_size,
                        (255, 255, 255),
                        (
                            node["x"] * research_tree_zoom
                            + 100 * research_tree_zoom
                            + research_tree_offset_x,
                            node["y"] * research_tree_zoom
                            + 35 * research_tree_zoom
                            + research_tree_offset_y,
                        ),
                    )
                else:
                    render_text(
                        upgrade_name,
                        name_font_size,
                        (255, 255, 255),
                        (
                            node["x"] * research_tree_zoom
                            + 100 * research_tree_zoom
                            + research_tree_offset_x,
                            node["y"] * research_tree_zoom
                            + 20 * research_tree_zoom
                            + research_tree_offset_y,
                        ),
                    )

                render_text(
                    f"Cost: {'$' if upgrade['currency'] == 'money' else ''} {format_number(upgrade['cost'])} {'RP' if upgrade['currency'] == 'research' else ''}",
                    cost_font_size,
                    (255, 255, 255),
                    (
                        node["x"] * research_tree_zoom
                        + 100 * research_tree_zoom
                        + research_tree_offset_x,
                        node["y"] * research_tree_zoom
                        + 60 * research_tree_zoom
                        + research_tree_offset_y,
                    ),
                )
            else:
                node["button_rect"] = None

    # draw a semi-transparent header background
    header_surface = pygame.Surface((new_screen_width, 200), pygame.SRCALPHA)
    header_surface.fill((30, 30, 30, 200))
    screen.blit(header_surface, (0, 0))

    # render title, back button, and resource displays
    render_text("Research Tree", 43, (255, 255, 255), (new_screen_width // 2 - 150, 50))
    back_button_rect = render_text(
        "< Back",
        15,
        (255, 255, 255),
        (new_screen_width - (new_screen_width / 1.1), 45),
        True,
        (100, 40),
        (100, 100, 100),
    )
    render_text(
        f"Research Points: {format_number(research)} RP", 15, (255, 255, 255), (20, 140)
    )
    render_text(f"Money: ${format_number(money)}", 15, (255, 255, 255), (20, 160))


# handles click interactions within the research tree interface
def handle_research_tree_click(mouse_pos):
    global research, money, research_tree_open, research_tree_dragging, last_research_mouse_pos
    for upgrade in research_upgrades:
        if upgrade.get("button_rect") and upgrade["button_rect"].collidepoint(
            mouse_pos
        ):
            if not upgrade["purchased"]:
                # check if all prerequisites are purchased
                prerequisites_met = all(
                    prereq["purchased"]
                    for prereq in research_upgrades
                    if prereq["name"]
                    in [
                        n["name"]
                        for t in tree_layout
                        for n in t
                        if upgrade["name"] in n["unlocks"]
                    ]
                )
                if prerequisites_met:
                    if upgrade["currency"] == "money" and money >= upgrade["cost"]:
                        money -= upgrade["cost"]
                        upgrade["purchased"] = True
                        upgrade["effect"]()
                    elif (
                        upgrade["currency"] == "research"
                        and research >= upgrade["cost"]
                    ):
                        research -= upgrade["cost"]
                        upgrade["purchased"] = True
                        upgrade["effect"]()
                return  # stop further processing once a button is clicked

    # handle back button click
    if back_button_rect and back_button_rect.collidepoint(mouse_pos):
        research_tree_open = False

    # start dragging the research tree only with the right mouse button
    if pygame.mouse.get_pressed()[2]:
        research_tree_dragging = True
        last_research_mouse_pos = mouse_pos


# updates research tree position when dragging with the mouse
def handle_research_tree_drag(mouse_pos):
    global research_tree_offset_x, research_tree_offset_y, last_research_mouse_pos
    if research_tree_dragging and last_research_mouse_pos:
        dx = mouse_pos[0] - last_research_mouse_pos[0]
        dy = mouse_pos[1] - last_research_mouse_pos[1]
        research_tree_offset_x += dx
        research_tree_offset_y += dy
        last_research_mouse_pos = mouse_pos


# stops the research tree dragging interaction
def stop_research_tree_drag():
    global research_tree_dragging, last_research_mouse_pos
    research_tree_dragging = False
    last_research_mouse_pos = None


# handles zooming in/out of the research tree view
def handle_research_tree_zoom(event):
    global research_tree_zoom, research_tree_offset_x, research_tree_offset_y
    if event.y > 0:
        new_zoom = min(
            research_tree_zoom + research_tree_zoom_step, max_research_tree_zoom
        )
    elif event.y < 0:
        new_zoom = max(
            research_tree_zoom - research_tree_zoom_step, min_research_tree_zoom
        )
    else:
        return

    # adjust offsets to zoom around the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    offset_x = (mouse_x - research_tree_offset_x) / research_tree_zoom
    offset_y = (mouse_y - research_tree_offset_y) / research_tree_zoom
    research_tree_offset_x -= int(offset_x * (new_zoom - research_tree_zoom))
    research_tree_offset_y -= int(offset_y * (new_zoom - research_tree_zoom))
    research_tree_zoom = new_zoom


# renders the tilemap with proper offsets and zoom level
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
                            scaled_tile = pygame.transform.scale(
                                tile, (tile_width, tile_height)
                            )
                            surface.blit(
                                scaled_tile,
                                (x * tile_width + offset_x, y * tile_height + offset_y),
                            )
    tooltip_data = locked_tiles.render_locked_tiles_with_tooltips(
        surface,
        offset_x,
        offset_y,
        zoom,
        pygame.mouse.get_pos(),
        tilemap,
        destroy_mode,
        selected_building,
    )
    if tooltip_data:
        render_tooltip(
            tooltip_data[0],
            (tooltip_data[2][0] + 15, tooltip_data[2][1] + 15),
            show_cost=False,
            additional_lines=[(f"Price: ${tooltip_data[1]}", (255, 255, 0))],
        )


# renders grid overlay on valid building placement tiles
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

                        pygame.draw.line(
                            surface,
                            (200, 200, 200),
                            (grid_x, grid_y),
                            (grid_x + tile_width, grid_y),
                        )
                        pygame.draw.line(
                            surface,
                            (200, 200, 200),
                            (grid_x, grid_y),
                            (grid_x, grid_y + tile_height),
                        )
                        pygame.draw.line(
                            surface,
                            (200, 200, 200),
                            (grid_x + tile_width, grid_y),
                            (grid_x + tile_width, grid_y + tile_height),
                        )
                        pygame.draw.line(
                            surface,
                            (200, 200, 200),
                            (grid_x, grid_y + tile_height),
                            (grid_x + tile_width, grid_y + tile_height),
                        )

                        valid_tiles.add((x, y))


# renders placed buildings with hover effects and tooltips
def render_placed_blocks(surface, placed_blocks, offset_x, offset_y, zoom, mouse_pos):
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)
    tooltip_data = None

    for (grid_x, grid_y), block_image in placed_blocks.items():
        block_x = grid_x * tile_width + offset_x
        block_y = grid_y * tile_height + offset_y
        scaled_image = pygame.transform.scale(block_image, (tile_width, tile_height))

        # grey out the block if it's out of ticks
        building_name = building_mapping.get(block_image)
        if (
            building_name in power_plant_ticks
            and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0
        ):
            greyed_out_image = scaled_image.copy()
            greyed_out_image.fill(
                (128, 128, 128, 150), special_flags=pygame.BLEND_RGBA_MULT
            )
            surface.blit(greyed_out_image, (block_x, block_y))
        else:
            surface.blit(scaled_image, (block_x, block_y))

        # render hover effect in destroy mode
        if (
            destroy_mode
            and block_x <= mouse_pos[0] < block_x + tile_width
            and block_y <= mouse_pos[1] < block_y + tile_height
        ):
            tinted_image = scaled_image.copy()
            tinted_image.fill((255, 0, 0, 205), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted_image, (block_x, block_y))

        # store tooltip data if hovering over the block
        if (
            block_x <= mouse_pos[0] < block_x + tile_width
            and block_y <= mouse_pos[1] < block_y + tile_height
        ):
            ticks_left = placed_power_plant_ticks.get((grid_x, grid_y), None)
            tooltip_data = (
                building_name,
                (mouse_pos[0] + 15, mouse_pos[1] + 15),
                ticks_left,
            )

    # render the tooltip last to ensure it appears on top
    if tooltip_data:
        render_tooltip(*tooltip_data)


# renders text elements with optional button functionality
def render_text(
    text,
    size,
    color,
    position,
    button=False,
    button_size=(0, 0),
    button_color=(0, 0, 0),
):
    font = pygame.font.Font("Assets/font.ttf", size + 5)
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


# checks if a building can be placed at the given grid position
def can_place_building(grid_x, grid_y):
    if 0 <= grid_x < tilemap.width and 0 <= grid_y < tilemap.height:
        gid_layer2 = tilemap.layers[1].data[grid_y][grid_x]
        return gid_layer2 == 0
    return False


# updates maximum power capacity based on placed battery buildings
def update_max_power():
    global max_power
    max_power = 50
    for (grid_x, grid_y), block_image in placed_blocks.items():
        building_name = building_mapping.get(block_image)
        if building_name in battery_capacity:
            max_power += battery_capacity[building_name]


# updates research points based on placed research labs
def update_research():
    global research, research_ps
    added_research = sum(
        research_per_second[building_mapping[block_image]]
        for block_image in placed_blocks.values()
        if building_mapping[block_image] in research_per_second
    )
    research += added_research
    research_ps = round(added_research, 2)


# updates power production based on active power plants
def update_power():
    global power, power_ps, money
    added_power = 0

    for (grid_x, grid_y), block_image in placed_blocks.items():
        building_name = building_mapping.get(block_image)
        if building_name in power_plant_ticks:
            # check if the power plant has remaining ticks
            if placed_power_plant_ticks.get((grid_x, grid_y), 0) > 0:
                if building_name in power_per_second:
                    added_power += power_per_second[building_name]

                # decrease the tick counter
                placed_power_plant_ticks[(grid_x, grid_y)] -= 1
            elif (
                (
                    building_name == "wind_turbine"
                    and auto_repair_buildings["wind_turbine"]
                )
                or (
                    building_name == "solar_panel"
                    and auto_repair_buildings["solar_panel"]
                )
                or (
                    building_name == "coal_plant"
                    and auto_repair_buildings["coal_plant"]
                )
                or (
                    building_name == "nuclear_plant"
                    and auto_repair_buildings["nuclear_plant"]
                )
                or (
                    building_name == "fusion_plant"
                    and auto_repair_buildings["fusion_plant"]
                )
            ):
                # automatically repair if the upgrade is active
                repair_cost = max(
                    1, int(building_prices[building_name] * repair_cost_percentage)
                )
                money = round(money, 2)
                if money >= repair_cost:
                    money -= repair_cost
                    placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[
                        building_name
                    ]

    power += added_power
    power_ps = round(added_power, 2)
    power = min(power, max_power)


# converts power into money based on placed houses
def update_money():
    global money, money_ps, power
    required_power = 0
    earned_money = 0

    for block_image in placed_blocks.values():
        building_name = building_mapping.get(block_image)
        if building_name in money_per_second:
            required_power += money_per_second[building_name]

    if power >= required_power:
        earned_money += required_power
        power -= required_power
    else:
        earned_money += power
        power = 0

    money += earned_money
    money = round(money, 2)
    money_ps = round(earned_money, 2)


# formats building names for display in tooltips
def format_building_name(building_name):
    return building_name.replace("_", " ").title()


# renders tooltips for buildings and regions
def render_tooltip(
    building, position, ticks_left=None, show_cost=False, additional_lines=None
):
    font = pygame.font.Font(None, 21)
    lines = []

    COLOR_TITLE = (255, 255, 255)
    COLOR_ACTION = (255, 0, 255)
    COLOR_POWER = (255, 255, 0)
    COLOR_MONEY = (0, 255, 0)
    COLOR_SELL = (255, 0, 0)
    COLOR_STATUS_GOOD = (0, 255, 0)
    COLOR_STATUS_BAD = (255, 0, 0)
    COLOR_STATUS_WARN = (255, 255, 0)
    COLOR_CAPACITY = (255, 255, 0)
    COLOR_RESEARCH = (0, 200, 255)

    if building in locked_tiles.locked_tiles:
        lines.append((building, COLOR_TITLE))
        lines.append(("Unlockable Region", COLOR_ACTION))
    elif building in research_per_second:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, COLOR_TITLE))
        lines.append(("Produces Research:", COLOR_ACTION))
        lines.append(
            (f"{format_number(research_per_second[building])} RP/s", COLOR_RESEARCH)
        )
        if show_cost:
            cost_color = (
                COLOR_MONEY if money >= building_prices[building] else COLOR_SELL
            )
            lines.append(
                (f"Cost: ${format_number(building_prices[building])}", cost_color)
            )
        sell_price = int(building_prices[building] * sell_percentage)
        lines.append((f"Sell Price: ${format_number(sell_price)}", COLOR_SELL))
    elif building in money_per_second:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, COLOR_TITLE))
        lines.append(("Converts Power to Money:", COLOR_ACTION))
        lines.append((f"{format_number(money_per_second[building])} MW/s", COLOR_POWER))
        if show_cost:
            cost_color = (
                COLOR_MONEY if money >= building_prices[building] else COLOR_SELL
            )
            lines.append(
                (f"Cost: ${format_number(building_prices[building])}", cost_color)
            )
        sell_price = int(building_prices[building] * sell_percentage)
        lines.append((f"Sell Price: ${format_number(sell_price)}", COLOR_SELL))
    elif building in battery_capacity:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, COLOR_TITLE))
        lines.append(("Stores Power:", COLOR_ACTION))
        lines.append(
            (f"{format_number(battery_capacity[building])} MW", COLOR_CAPACITY)
        )
        if show_cost:
            cost_color = (
                COLOR_MONEY if money >= building_prices[building] else COLOR_SELL
            )
            lines.append(
                (f"Cost: ${format_number(building_prices[building])}", cost_color)
            )
        sell_price = int(building_prices[building] * sell_percentage)
        lines.append((f"Sell Price: ${format_number(sell_price)}", COLOR_SELL))
    elif building in power_per_second:
        formatted_name = format_building_name(building)
        lines.append((formatted_name, COLOR_TITLE))
        lines.append(("Produces Power:", COLOR_ACTION))
        lines.append((f"{format_number(power_per_second[building])} MW/s", COLOR_POWER))
        if ticks_left is not None:
            if ticks_left <= 0:
                lines.append(("Status: Broken", COLOR_STATUS_BAD))
                repair_cost = round(
                    building_prices[building] * repair_cost_percentage, 2
                )
                lines.append(
                    (f"Repair Cost: ${format_number(repair_cost)}", COLOR_STATUS_WARN)
                )
            else:
                lines.append(("Status: Operational", COLOR_STATUS_GOOD))
        if show_cost:
            cost_color = (
                COLOR_MONEY if money >= building_prices[building] else COLOR_SELL
            )
            lines.append(
                (f"Cost: ${format_number(building_prices[building])}", cost_color)
            )
        if ticks_left is not None:
            lines.append(
                (
                    f"Ticks Left: {ticks_left} / {power_plant_ticks[building]}",
                    COLOR_ACTION,
                )
            )
        sell_price = int(building_prices[building] * sell_percentage)
        lines.append((f"Sell Price: ${format_number(sell_price)}", COLOR_SELL))

    # add additional lines if provided
    if additional_lines:
        lines.extend(additional_lines)

    # render each line and calculate the tooltip size
    rendered_lines = [font.render(line[0], True, line[1]) for line in lines]
    line_height = font.get_linesize() + 5  
    tooltip_width = max(line.get_width() for line in rendered_lines) + 10
    tooltip_height = len(rendered_lines) * line_height + 10

    # create a transparent surface for the tooltip background
    tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    pygame.draw.rect(
        tooltip_surface,
        (20, 20, 20, 200),
        (0, 0, tooltip_width, tooltip_height),
        border_radius=7,
    )

    # draw the background
    screen.blit(tooltip_surface, position)

    # draw each line of text
    for i, line_surface in enumerate(rendered_lines):
        screen.blit(line_surface, (position[0] + 5, position[1] + 5 + i * line_height))


# renders the game's graphical user interface
def render_gui():
    pygame.draw.rect(screen, (50, 50, 50), gui_rect)

    global destroy_button_rect, research_button_rect, sell_power_button_rect

    # render resource stats with formatted numbers
    if money_ps == 0:
        render_text(
            f"Money: ${format_number(money)}",
            12,
            (255, 255, 255),
            (20, 20 - gui_scroll_offset),
        )
    else:
        render_text(
            f"Money: ${format_number(money)} + {format_number(money_ps)}/s",
            12,
            (255, 255, 255),
            (20, 20 - gui_scroll_offset),
        )

    if power_ps == 0:
        render_text(
            f"Power: {format_number(power)} MW / {format_number(max_power)} MW",
            12,
            (255, 255, 255),
            (20, 50 - gui_scroll_offset),
        )
    else:
        render_text(
            f"Power: {format_number(power)} MW / {format_number(max_power)} MW + {format_number(power_ps)}/s",
            12,
            (255, 255, 255),
            (20, 50 - gui_scroll_offset),
        )

    if research_ps == 0:
        render_text(
            f"Research: {format_number(research)} RP",
            12,
            (255, 255, 255),
            (20, 80 - gui_scroll_offset),
        )
    else:
        render_text(
            f"Research: {format_number(research)} RP + {format_number(research_ps)}/s",
            12,
            (255, 255, 255),
            (20, 80 - gui_scroll_offset),
        )

    if pollution_ps == 0:
        render_text(
            f"Pollution: {format_number(pollution)} / {format_number(max_pollution)}",
            12,
            (255, 255, 255),
            (20, 110 - gui_scroll_offset),
        )
    else:
        render_text(
            f"Pollution: {format_number(pollution)} / {format_number(max_pollution)} + {format_number(pollution_ps)}/s",
            12,
            (255, 255, 255),
            (20, 110 - gui_scroll_offset),
        )

    # render buttons
    research_button_rect = render_text(
        "Research",
        10,
        (255, 255, 255),
        (20, 180 - gui_scroll_offset),
        True,
        (120, 35),
        (100, 100, 100),
    )
    destroy_button_rect = render_text(
        "Destroy: ON" if destroy_mode else "Destroy: OFF",
        10,
        (255, 255, 255),
        (20, 220 - gui_scroll_offset),
        True,
        (120, 35),
        (100, 100, 100),
    )
    sell_power_button_rect = render_text(
        "Sell Power",
        10,
        (255, 255, 255),
        (20, 260 - gui_scroll_offset),
        True,
        (120, 35),
        (100, 100, 100),
    )

    render_text("Buildings: ", 19, (255, 255, 255), (20, 320 - gui_scroll_offset))
    render_text("- Power plants", 15, (200, 200, 200), (40, 355 - gui_scroll_offset))
    render_text("- Labs", 15, (200, 200, 200), (40, 435 - gui_scroll_offset))
    render_text("- Houses", 15, (200, 200, 200), (40, 515 - gui_scroll_offset))
    render_text("- Batteries", 15, (200, 200, 200), (40, 595 - gui_scroll_offset))

    # render building buttons with lock images and tooltips
    global power_plant_buttons, lab_buttons, house_buttons, battery_buttons

    mouse_x, mouse_y = pygame.mouse.get_pos()
    tooltip_data = None 

    power_plant_buttons = []
    for i, img in enumerate(power_plant_images):
        building_name = list(building_mapping.values())[i]
        rect = render_text(
            "",
            19,
            (255, 255, 255),
            (60 + i * 50, 380 - gui_scroll_offset),
            True,
            (40, 40),
            (100, 100, 100),
        )
        power_plant_buttons.append(rect)
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 380 + 10 - gui_scroll_offset))
        if not building_unlocks[building_name]:
            screen.blit(
                lock_image, (60 + i * 50, 380 - gui_scroll_offset)
            )  # display lock image
        if rect.collidepoint(mouse_x, mouse_y):
            tooltip_data = (
                building_name,
                (mouse_x + 15, mouse_y + 15),
                building_prices[building_name],
            )  # adjust tooltip offset

    lab_buttons = []
    for i, img in enumerate(lab_images):
        building_name = list(building_mapping.values())[5 + i] 
        rect = render_text(
            "",
            19,
            (255, 255, 255),
            (60 + i * 50, 460 - gui_scroll_offset),
            True,
            (40, 40),
            (100, 100, 100),
        )
        lab_buttons.append(rect)
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 460 + 10 - gui_scroll_offset))
        if not building_unlocks[building_name]:
            screen.blit(
                lock_image, (60 + i * 50, 460 - gui_scroll_offset)
            )  
        if rect.collidepoint(mouse_x, mouse_y):
            tooltip_data = (
                building_name,
                (mouse_x + 15, mouse_y + 15),
            )  

    house_buttons = []
    for i, img in enumerate(house_images):
        building_name = list(building_mapping.values())[8 + i]
        rect = render_text(
            "",
            19,
            (255, 255, 255),
            (60 + i * 50, 540 - gui_scroll_offset),
            True,
            (40, 40),
            (100, 100, 100),
        )
        house_buttons.append(rect)
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 540 + 10 - gui_scroll_offset))
        if not building_unlocks[building_name]:
            screen.blit(
                lock_image, (60 + i * 50, 540 - gui_scroll_offset)
            )  
        if rect.collidepoint(mouse_x, mouse_y):
            tooltip_data = (
                building_name,
                (mouse_x + 15, mouse_y + 15),
            )  

    battery_buttons = []
    for i, img in enumerate(battery_images):
        building_name = list(building_mapping.values())[11 + i]
        rect = render_text(
            "",
            19,
            (255, 255, 255),
            (60 + i * 50, 620 - gui_scroll_offset),
            True,
            (40, 40),
            (100, 100, 100),
        )
        battery_buttons.append(rect)
        scaled_img = pygame.transform.scale(img, (30, 30))
        screen.blit(scaled_img, (60 + i * 50 + 5, 620 + 10 - gui_scroll_offset))
        if not building_unlocks[building_name]:
            screen.blit(
                lock_image, (60 + i * 50, 620 - gui_scroll_offset)
            )  
        if rect.collidepoint(mouse_x, mouse_y):
            tooltip_data = (
                building_name,
                (mouse_x + 15, mouse_y + 15),
            )  

    # render the tooltip last to ensure it appears on top
    if tooltip_data:
        render_tooltip(
            tooltip_data[0],
            (tooltip_data[1][0] + 15, tooltip_data[1][1] + 15),
            show_cost=True,
        )


# handles click interactions within the GUI
def handle_gui_click(mouse_x, mouse_y):
    global selected_building, show_grid, destroy_mode

    for i, rect in enumerate(power_plant_buttons):
        if rect.collidepoint(mouse_x, mouse_y):
            building_name = list(building_mapping.values())[i]
            if building_unlocks[building_name]:
                if selected_building == power_plant_images[i]:
                    selected_building = None
                    show_grid = False
                else:
                    selected_building = power_plant_images[i]
                    show_grid = True
                    destroy_mode = False
            else:
                notifications.create_toast(
                    f"{building_name} is locked. Unlock it via the research tree."
                )
            break

    for i, rect in enumerate(lab_buttons):
        if rect.collidepoint(mouse_x, mouse_y):
            building_name = list(building_mapping.values())[
                5 + i
            ]  
            if building_unlocks[building_name]:
                if selected_building == lab_images[i]:
                    selected_building = None
                    show_grid = False
                else:
                    selected_building = lab_images[i]
                    show_grid = True
                    destroy_mode = False
            else:
                notifications.create_toast(
                    f"{building_name} is locked. Unlock it via the research tree."
                )
            break

    for i, rect in enumerate(house_buttons):
        if rect.collidepoint(mouse_x, mouse_y):
            building_name = list(building_mapping.values())[8 + i]
            if building_unlocks[building_name]:
                if selected_building == house_images[i]:
                    selected_building = None
                    show_grid = False
                else:
                    selected_building = house_images[i]
                    show_grid = True
                    destroy_mode = False
            else:
                notifications.create_toast(
                    f"{building_name} is locked. Unlock it via the research tree."
                )
            break

    for i, rect in enumerate(battery_buttons):
        if rect.collidepoint(mouse_x, mouse_y):
            building_name = list(building_mapping.values())[11 + i]
            if building_unlocks[building_name]:
                if selected_building == battery_images[i]:
                    selected_building = None
                    show_grid = False
                else:
                    selected_building = battery_images[i]
                    show_grid = True
                    destroy_mode = False
            else:
                notifications.create_toast(
                    f"{building_name} is locked. Unlock it via the research tree."
                )
            break


# handles repairing of broken buildings
def handle_repair(grid_x, grid_y):
    if destroy_mode:
        # do not allow repairs when destroy mode is active
        return

    if (grid_x, grid_y) in placed_blocks:
        block_image = placed_blocks[(grid_x, grid_y)]
        building_name = building_mapping.get(block_image)

        # check if the building is broken and restore it
        if (
            building_name in power_plant_ticks
            and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0
        ):
            repair_cost = max(
                repair_cost_percentage,
                round(building_prices[building_name] * repair_cost_percentage, 2),
            )
            global money
            if money >= repair_cost:
                money -= repair_cost
                placed_power_plant_ticks[(grid_x, grid_y)] = power_plant_ticks[
                    building_name
                ]

                repair_sound1 = pygame.mixer.Sound("Sound_Effects/rachet_click.mp3")
                repair_sound2 = pygame.mixer.Sound("Sound_Effects/repair_metal.mp3")

                repair_sound1.set_volume(0.5)
                repair_sound2.set_volume(0.5)

                repair_sound1.play()
                repair_sound2.play()
            else:
                notifications.create_toast(
                    f"Not enough money to repair {building_name}! Need ${format_number(repair_cost)}"
                )


# format numbers for display in the GUI
def format_number(number):
    if abs(number) >= 1e9:
        return f"{number/1e9:.2f}B"
    elif abs(number) >= 1e6:
        return f"{number/1e6:.2f}M"
    elif abs(number) >= 1e3:
        return f"{number/1e3:.2f}K"
    else:
        return f"{number:.2f}"


# load player data at the start of the game
load_player_data()

# main game loop
running = True
valid_tiles = set()
while running:
    # check for screen resizing and adjust dimensions
    info = pygame.display.Info()

    if new_screen_width != info.current_w or new_screen_height != info.current_h:

        new_screen_width = info.current_w
        new_screen_height = info.current_h

        gui_width = new_screen_width * 0.3
        gui_rect = pygame.Rect(0, 0, gui_width, new_screen_height)

    # clear the screen with a background color
    screen.fill((92, 105, 160))

    # render the tilemap with the current camera and zoom settings
    render_tilemap(screen, tilemap, gui_width + camera_x, camera_y, zoom)

    if show_grid:
        # clear and render the grid if enabled
        valid_tiles.clear()
        render_grid(screen, tilemap, gui_width + camera_x, camera_y, zoom, valid_tiles)

    # render placed blocks and handle hover effects in destroy mode
    render_placed_blocks(
        screen,
        placed_blocks,
        gui_width + camera_x,
        camera_y,
        zoom,
        pygame.mouse.get_pos(),
    )

    if show_grid and not destroy_mode and selected_building:
        # highlight valid placement tiles for the selected building
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = int((mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom))
        grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

        if (grid_x, grid_y) in valid_tiles and (grid_x, grid_y) not in placed_blocks:
            tile_width = int(tilemap.tilewidth * zoom)
            tile_height = int(tilemap.tileheight * zoom)
            block_x = grid_x * tile_width + gui_width + camera_x
            block_y = grid_y * tile_height + camera_y

            greyed_out_image = pygame.transform.scale(
                selected_building, (tile_width, tile_height)
            ).copy()
            greyed_out_image.fill(
                (128, 128, 128, 150), special_flags=pygame.BLEND_RGBA_MULT
            )
            screen.blit(greyed_out_image, (block_x, block_y))

    # render the GUI elements
    render_gui()

    notifications.render_notifications(screen, custom_font)

    for event in pygame.event.get():
        # handle quitting the game
        if event.type == pygame.QUIT:
            save_player_data()  # save data when quitting
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and notifications.handle_popup_click(
                event.pos
            ):  # only handle left clicks
                continue

            if research_tree_open:
                # handle clicks only for the research tree when it is open
                handle_research_tree_click(event.pos)
                continue

            # handle other game interactions
            mouse_x, mouse_y = event.pos

            if destroy_button_rect and destroy_button_rect.collidepoint(
                (mouse_x, mouse_y)
            ):
                # toggle destroy mode
                destroy_mode = not destroy_mode
                if destroy_mode:
                    show_grid = True
                    selected_building = None
                else:
                    show_grid = False

            if research_button_rect and research_button_rect.collidepoint(
                (mouse_x, mouse_y)
            ):
                # open the research tree
                research_tree_open = True

            if sell_power_button_rect and sell_power_button_rect.collidepoint(
                (mouse_x, mouse_y)
            ):
                # sell all power and convert it into money
                money += power
                power = 0

            # handle GUI button clicks
            if gui_rect.collidepoint(mouse_x, mouse_y):
                # process GUI interactions
                handle_gui_click(mouse_x, mouse_y)

            # handle region unlocking
            if (
                not destroy_mode and not selected_building
            ):  # allow region purchasing only if not in build or destroy mode
                if event.button == 1:  # only allow unlocking with left click
                    tile_x = int(
                        (mouse_x - gui_width - camera_x)
                        // int(tilemap.tilewidth * zoom)
                    )
                    tile_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))
                    for region_name, region_data in locked_tiles.locked_tiles.items():
                        if (
                            region_data["locked"]
                            and (tile_x, tile_y) in region_data["tiles"]
                        ):
                            money, _ = locked_tiles.unlock_region(region_name, money)
                            break

            # handle repairing buildings regardless of build mode
            if not destroy_mode:
                grid_x = int(
                    (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
                )
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))
                handle_repair(grid_x, grid_y)

            # handle block destruction in destroy mode
            if show_grid and destroy_mode:
                grid_x = int(
                    (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
                )
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in valid_tiles:
                    if event.button == 1:
                        if (grid_x, grid_y) in placed_blocks:
                            block_image = placed_blocks[(grid_x, grid_y)]
                            building_name = building_mapping[block_image]
                            building_cost = building_prices[building_name]

                            # calculate the refund based on sell_percentage
                            refund = round(building_cost * sell_percentage, 2)
                            money += refund

                            # remove the block and update max power
                            del placed_blocks[(grid_x, grid_y)]
                            update_max_power()

            elif show_grid and not destroy_mode:
                # handle block placement and restoration
                grid_x = int(
                    (mouse_x - gui_width - camera_x) // int(tilemap.tilewidth * zoom)
                )
                grid_y = int((mouse_y - camera_y) // int(tilemap.tileheight * zoom))

                if (grid_x, grid_y) in placed_blocks:
                    block_image = placed_blocks[(grid_x, grid_y)]
                    building_name = building_mapping.get(block_image)

                    # check if the building is broken and restore it
                    if (
                        building_name in power_plant_ticks
                        and placed_power_plant_ticks.get((grid_x, grid_y), 0) <= 0
                    ):
                        repair_cost = max(
                            1,
                            int(
                                building_prices[building_name] * repair_cost_percentage
                            ),
                        )
                        if money >= repair_cost:
                            money -= repair_cost
                            placed_power_plant_ticks[(grid_x, grid_y)] = (
                                power_plant_ticks[building_name]
                            )

                elif (
                    (grid_x, grid_y) in valid_tiles
                    and (grid_x, grid_y) not in placed_blocks
                    and can_place_building(grid_x, grid_y)
                ):
                    if locked_tiles.is_tile_locked(grid_x, grid_y):
                        notifications.create_toast(
                            "This tile is locked behind a region. Unlock the region to build here."
                        )
                    else:
                        if event.button == 1 and selected_building:
                            building_name = building_mapping[selected_building]
                            building_cost = building_prices[building_name]

                            if money >= building_cost:
                                money -= building_cost
                                placed_blocks[(grid_x, grid_y)] = selected_building

                                # initialize tick counter for power plants
                                if building_name in power_plant_ticks:
                                    placed_power_plant_ticks[(grid_x, grid_y)] = (
                                        power_plant_ticks[building_name]
                                    )

                                update_max_power()
                                build_sound = pygame.mixer.Sound(
                                    "Sound_Effects/lego_building.mp3"
                                )
                                build_sound.play()
                            else:
                                notifications.create_toast(
                                    f"Not enough money! Need ${format_number(building_cost)}"
                                )

            if event.button == 3:
                # start dragging the map
                dragging = True
                last_mouse_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            # stop dragging the map
            if event.button == 3:
                dragging = False
                last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            # handle map dragging
            if dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_x += dx
                camera_y += dy
                last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            # handle zooming and GUI scrolling
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if gui_rect.collidepoint(mouse_x, mouse_y):
                # scroll the GUI
                gui_scroll_offset = max(
                    0, gui_scroll_offset - event.y * gui_scroll_speed
                )
            else:
                # zoom the map
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
        # render the research tree if open
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

    # update game state at regular intervals
    current_time = pygame.time.get_ticks()
    if current_time - last_tick >= tick_interval:
        last_tick = current_time
        update_research()
        update_power()
        update_money()

    # save data periodically (e.g., every 10 seconds)
    if current_time - last_tick >= 10000:  # 10 seconds
        save_player_data()

    now = datetime.datetime.now()

    pygame.display.flip()

pygame.quit()
sys.exit()
