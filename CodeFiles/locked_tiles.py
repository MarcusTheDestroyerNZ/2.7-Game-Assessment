import pygame
from CodeFiles import notifications  # Change import to use relative import

# Define locked tiles for each region (manually assign tiles here)
locked_tiles = {
    "Stewart Island": {
        "tiles": {
            (6, 26),
            (5, 27),
            (6, 27),
        },
        "locked": True,
        "price": 0,
    },
    "Southland": {
        "tiles": {
            (8, 16),
            (9, 16),
            (7, 17),
            (8, 17),
            (9, 17),
            (6, 18),
            (7, 18),
            (8, 18),
            (9, 18),
            (10, 18),
            (5, 19),
            (6, 19),
            (7, 19),
            (8, 19),
            (9, 19),
            (10, 19),
            (4, 20),
            (5, 20),
            (6, 20),
            (7, 20),
            (8, 20),
            (9, 20),
            (10, 20),
            (4, 21),
            (5, 21),
            (6, 21),
            (7, 21),
            (8, 21),
            (9, 21),
            (10, 21),
            (5, 22),
            (6, 22),
            (7, 22),
            (8, 22),
            (9, 22),
            (10, 22),
            (11, 22),
            (8, 23),
            (9, 23),
            (10, 23),
            (11, 23),
            (11, 24),
        },
        "locked": True,
        "price": 5,
    },
    "Otago": {
        "tiles": {
            (14, 15),
            (15, 15),
            (16, 15),
            (13, 16),
            (14, 16),
            (15, 16),
            (16, 16),
            (12, 17),
            (13, 17),
            (14, 17),
            (15, 17),
            (16, 17),
            (11, 18),
            (12, 18),
            (13, 18),
            (14, 18),
            (15, 18),
            (11, 19),
            (12, 19),
            (13, 19),
            (14, 19),
            (15, 19),
            (11, 20),
            (12, 20),
            (13, 20),
            (14, 20),
            (15, 20),
            (11, 21),
            (12, 21),
            (13, 21),
            (14, 21),
            (15, 21),
            (12, 22),
            (13, 22),
            (14, 22),
            (12, 23),
            (13, 23),
            (12, 24),
        },
        "locked": True,
        "price": 1000,
    },
    "West Coast": {
        "tiles": {
            (18, 5),
            (17, 6),
            (18, 6),
            (19, 6),
            (17, 7),
            (18, 7),
            (19, 7),
            (17, 8),
            (18, 8),
            (16, 9),
            (17, 9),
            (18, 9),
            (15, 10),
            (16, 10),
            (17, 10),
            (14, 11),
            (15, 11),
            (16, 11),
            (13, 12),
            (14, 12),
            (15, 12),
            (11, 13),
            (12, 13),
            (13, 13),
            (14, 13),
            (10, 14),
            (11, 14),
            (12, 14),
            (13, 14),
            (14, 14),
            (9, 15),
            (10, 15),
            (11, 15),
            (12, 15),
            (13, 15),
            (10, 16),
            (11, 16),
            (12, 16),
            (10, 17),
            (11, 17),
        },
        "locked": True,
        "price": 5000,
    },
    "Canterbury": {
        "tiles": {
            (19, 8),
            (20, 8),
            (21, 8),
            (22, 8),
            (23, 8),
            (19, 9),
            (20, 9),
            (21, 9),
            (22, 9),
            (18, 10),
            (19, 10),
            (20, 10),
            (21, 10),
            (22, 10),
            (17, 11),
            (18, 11),
            (19, 11),
            (20, 11),
            (16, 12),
            (17, 12),
            (18, 12),
            (19, 12),
            (20, 12),
            (15, 13),
            (16, 13),
            (17, 13),
            (18, 13),
            (19, 13),
            (20, 13),
            (21, 13),
            (15, 14),
            (16, 14),
            (17, 14),
            (18, 14),
        },
        "locked": True,
        "price": 15000,
    },
    "Marlborough and Nelson": {
        "tiles": {
            (20, 2),
            (19, 3),
            (20, 3),
            (21, 3),
            (24, 3),
            (19, 4),
            (20, 4),
            (21, 4),
            (22, 4),
            (23, 4),
            (24, 4),
            (19, 5),
            (20, 5),
            (21, 5),
            (22, 5),
            (23, 5),
            (24, 5),
            (20, 6),
            (21, 6),
            (22, 6),
            (23, 6),
            (24, 6),
            (20, 7),
            (21, 7),
            (22, 7),
            (23, 7),
            (24, 7),
        },
        "locked": True,
        "price": 7500,
    },
}


# Renders locked region tiles with overlays and tooltips
def render_locked_tiles_with_tooltips(
    surface,
    offset_x,
    offset_y,
    zoom,
    mouse_pos,
    tilemap,
    destroy_mode,
    selected_building,
):
    tooltip_data = None
    tile_width = int(tilemap.tilewidth * zoom)
    tile_height = int(tilemap.tileheight * zoom)

    # First, render all locked tiles with base overlay
    for region_name, region_data in locked_tiles.items():
        if region_data["locked"]:
            for grid_x, grid_y in region_data["tiles"]:
                tile_x = grid_x * tile_width + offset_x
                tile_y = grid_y * tile_height + offset_y
                grey_overlay = pygame.Surface(
                    (tile_width, tile_height), pygame.SRCALPHA
                )
                grey_overlay.fill((50, 50, 50, 150))
                surface.blit(grey_overlay, (tile_x, tile_y))

    # Then, handle hover effects and tooltip only when not in build/destroy mode
    if not destroy_mode and not selected_building:
        for region_name, region_data in locked_tiles.items():
            if region_data["locked"]:
                hovering = False
                for grid_x, grid_y in region_data["tiles"]:
                    tile_x = grid_x * tile_width + offset_x
                    tile_y = grid_y * tile_height + offset_y
                    tile_rect = pygame.Rect(tile_x, tile_y, tile_width, tile_height)
                    if tile_rect.collidepoint(mouse_pos):
                        hovering = True
                        break

                if hovering:
                    # Add blue highlight overlay for hovered region
                    for grid_x, grid_y in region_data["tiles"]:
                        tile_x = grid_x * tile_width + offset_x
                        tile_y = grid_y * tile_height + offset_y
                        highlight_overlay = pygame.Surface(
                            (tile_width, tile_height), pygame.SRCALPHA
                        )
                        highlight_overlay.fill((100, 100, 255, 100))
                        surface.blit(highlight_overlay, (tile_x, tile_y))
                    tooltip_data = (region_name, region_data["price"], mouse_pos)

    return tooltip_data


# Unlocks a region if player has enough money
def unlock_region(region_name, money):
    if region_name in locked_tiles and locked_tiles[region_name]["locked"]:
        price = locked_tiles[region_name]["price"]
        if money >= price:
            money -= price
            locked_tiles[region_name]["locked"] = False
            print(f"Unlocked {region_name} for ${price}.")
            unlock_sound = pygame.mixer.Sound("Sound_Effects/unlock_region.mp3")
            unlock_sound.play()
            return money, True
        else:
            notifications.create_toast("Not enough money to unlock this region!")
    return money, False


# Checks if a specific tile position is within a locked region
def is_tile_locked(grid_x, grid_y):
    for region_name, region_data in locked_tiles.items():
        if region_data["locked"] and (grid_x, grid_y) in region_data["tiles"]:
            return True
    return False
