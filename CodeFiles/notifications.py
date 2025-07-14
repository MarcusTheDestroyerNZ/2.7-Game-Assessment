import pygame

active_toast_notifications = []
active_popup = None


# Formats building names by replacing underscores with spaces and capitalizing words
def format_building_name(name):
    return name.replace("_", " ").title()


# Creates a temporary toast notification that fades away after a duration
def create_toast(message, duration=1500):
    # Format any building names in the message
    if "is locked" in message:
        building_name = message.split(" is locked")[0]
        formatted_name = format_building_name(building_name)
        message = message.replace(building_name, formatted_name)

    # Remove oldest toast if we have more than 3
    if len(active_toast_notifications) >= 3:
        active_toast_notifications.pop(0)  # Remove oldest toast

    active_toast_notifications.append(
        {
            "message": message,
            "start_time": pygame.time.get_ticks(),
            "duration": duration,
            "alpha": 255,
        }
    )


# Creates a modal popup with a title, message, and close button
def create_popup(title, message):
    global active_popup
    active_popup = {"title": title, "message": message}


# Closes the currently active popup
def close_popup():
    global active_popup
    active_popup = None


# Renders all active notifications (toasts and popups) on the screen
def render_notifications(screen, font):
    current_time = pygame.time.get_ticks()
    screen_width = screen.get_width()

    # Render toast notifications
    y_offset = 10
    for notification in active_toast_notifications[:]:
        elapsed = current_time - notification["start_time"]

        if elapsed >= notification["duration"]:
            active_toast_notifications.remove(notification)
            continue

        # Calculate fade
        if elapsed > notification["duration"] - 500:  # Start fading 500ms before end
            notification["alpha"] = max(
                0, 255 * (1 - (elapsed - (notification["duration"] - 500)) / 500)
            )

        # Render toast
        text_surface = font.render(notification["message"], True, (255, 255, 255))

        # Create background with padding
        padding = 10
        bg_width = text_surface.get_width() + (padding * 2)
        bg_height = text_surface.get_height() + (padding * 2)
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 20, notification["alpha"]))  # Dark background

        # Center horizontally
        x = (screen_width - bg_width) // 2

        # Draw background and text
        screen.blit(bg_surface, (x, y_offset))
        text_alpha = text_surface.copy()
        text_alpha.fill(
            (255, 255, 255, notification["alpha"]), special_flags=pygame.BLEND_RGBA_MULT
        )
        screen.blit(text_alpha, (x + padding, y_offset + padding))

        y_offset += bg_height + 5  # Add small gap between toasts

    # Render popup if active
    if active_popup:
        # Create semi-transparent background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Create popup box
        box_width = 400
        title_height = 40
        padding = 20

        # Calculate message height
        message_words = active_popup["message"].split()
        message_lines = []
        current_line = []
        for word in message_words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if font.size(test_line)[0] > box_width - (padding * 2):
                current_line.pop()
                if current_line:
                    message_lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            message_lines.append(" ".join(current_line))

        message_height = len(message_lines) * (font.get_linesize() + 5)
        box_height = title_height + message_height + (padding * 3)

        # Draw popup box
        box_x = (screen_width - box_width) // 2
        box_y = (screen.get_height() - box_height) // 2
        popup_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (50, 50, 50), popup_rect)
        pygame.draw.rect(screen, (100, 100, 100), popup_rect, 2)

        # Draw title
        title_surface = font.render(active_popup["title"], True, (255, 255, 255))
        screen.blit(title_surface, (box_x + padding, box_y + padding))

        # Draw close button
        close_text = font.render("×", True, (255, 255, 255))
        close_x = box_x + box_width - padding - close_text.get_width()
        close_y = box_y + padding
        screen.blit(close_text, (close_x, close_y))

        # Store close button rect for click detection
        active_popup["close_rect"] = pygame.Rect(
            close_x, close_y, close_text.get_width(), close_text.get_height()
        )

        # Draw message
        y = box_y + title_height + padding
        for line in message_lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (box_x + padding, y))
            y += font.get_linesize() + 5


# Handles click interactions with popup close buttons
def handle_popup_click(pos):
    if active_popup and "close_rect" in active_popup:
        if active_popup["close_rect"].collidepoint(pos):
            close_popup()
            return True
    return False
