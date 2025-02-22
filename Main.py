import pygame
import sys
import random
from enum import Enum
from Keyboard import Keyboard
from Player import Player, PlayerSetup
from Vector2 import Vector2

class GameState(Enum):
    HOME = 1
    INGAME = 2
    GAME_OVER = 3

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SPAWN_BORDER_OUT = 20 # Distance between screen border and the outer edge of the spawn area
SPAWN_BORDER_IN = 50 # Distance between screen border and the inner edge of the spawn area
TOP_MENU_HEIGHT = 28
PLAYER_SCORES_GAP = 100
FPS = 120

TRANSPARENT = (0, 0, 0, 0)
BG_COLOR = (41, 48, 61)
MENU_COLOR = (65, 74, 89)
TEXT_COLOR = (255, 255, 255)
DISABLED_TEXT_COLOR = (67, 75, 89)
PLAYER_SETUP = [
    PlayerSetup((66, 209, 245), (66, 135, 245), pygame.K_a, pygame.K_d, "Blue"),
    PlayerSetup((250, 181, 125), (247, 136, 45), pygame.K_LEFT, pygame.K_RIGHT, "Orange"),
    PlayerSetup((120, 255, 145), (40, 235, 76), pygame.K_b, pygame.K_m, "Green"),
    PlayerSetup((199, 161, 212), (203, 91, 240), pygame.K_KP1, pygame.K_KP3, "Purple")
]
MOTIVATIONAL_MESSAGES = [
    "Wow, you've covered such a long trail!",
    "You won... again.",
    "Keep it up!",
    "Isn't this a bit boring?",
    "You should play with your 'friends' someday.",
    "You want to try again?",
    "Better luck next time!",
    "Sigh...",
    "Better be careful there."
]

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# The foreground is for rendering the players
foreground = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
# The background is for rendering the trails of the players
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(BG_COLOR)
# Define font
font_s = pygame.font.Font(None, 24)
font_l = pygame.font.Font(None, 40)
font_xl = pygame.font.Font(None, 50)

pygame.display.set_caption("Be careful of sudden turns!")

keyboard = Keyboard()
game_state = GameState.HOME
players = []
running = True

def render_text(text, screen, position, font, color, background=None):
    t = font.render(text, True, color, background)
    t_rect = t.get_rect(center=position)
    screen.blit(t, t_rect)

def draw_home_screen():
    global font_s, font_l, font_xl
    background.fill(BG_COLOR)
    screen.blit(background, (0, 0))
    font_s = pygame.font.Font(None, 24)
    font_xl = pygame.font.Font(None, 50)
    render_text("ESC: Quit", screen, (45, 15), font_s, TEXT_COLOR)
    render_text("Be careful of sudden turns!", screen, (SCREEN_WIDTH / 2, 150), font_xl, TEXT_COLOR)
    # Render player count
    for i in range(len(PLAYER_SETUP)):
        color = PLAYER_SETUP[i].inactive_color if i < len(players) else DISABLED_TEXT_COLOR
        render_text(f"{PLAYER_SETUP[i].name}: {pygame.key.name(PLAYER_SETUP[i].left_key).upper()} {pygame.key.name(PLAYER_SETUP[i].right_key).upper()}", screen, (SCREEN_WIDTH / 2, 250 + i * 50), font_l, color)
    render_text("UP: Remove Player     DOWN: Add Player     SPACE: Start Game", screen, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100), font_s, TEXT_COLOR)

# Players can spawn in a frame-shaped area around the playing field.
def calculate_starting_position(side):
    x, y = 0, 0
    match side:
        case 0:
            # Left border
            x = random.randrange(SPAWN_BORDER_OUT, SPAWN_BORDER_IN)
            y = random.randrange(TOP_MENU_HEIGHT + SPAWN_BORDER_OUT, SCREEN_HEIGHT - SPAWN_BORDER_OUT)
        case 1:
            # Right border
            x = random.randrange(SCREEN_WIDTH - SPAWN_BORDER_IN, SCREEN_WIDTH - SPAWN_BORDER_OUT)
            y = random.randrange(TOP_MENU_HEIGHT + SPAWN_BORDER_OUT, SCREEN_HEIGHT - SPAWN_BORDER_OUT)
        case 2:
            # Top border
            x = random.randrange(SPAWN_BORDER_IN, SCREEN_WIDTH - SPAWN_BORDER_IN)
            y = random.randrange(TOP_MENU_HEIGHT + SPAWN_BORDER_OUT, TOP_MENU_HEIGHT + SPAWN_BORDER_IN)
        case 3:
            # Bottom border
            x = random.randrange(SPAWN_BORDER_IN, SCREEN_WIDTH - SPAWN_BORDER_IN)
            y = random.randrange(SCREEN_HEIGHT - SPAWN_BORDER_IN, SCREEN_HEIGHT - SPAWN_BORDER_OUT)
    rotation = (Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2) - Vector2(x, y))
    rotation.normalize()
    return (x, y, rotation)

# Add a player with the next available setup from the predefined setups
# and a random position and rotation
def add_player():
    i = len(players)
    # Prevent adding more players than there are predefined setups
    if i >= len(PLAYER_SETUP):
        print("Maximum number of players reached. Cannot add another one!")
        return
    x, y, rotation = calculate_starting_position(i if i < 4 else 4)
    players.append(Player(PLAYER_SETUP[i], x, y, rotation))

# Function to convert trail pixels in a ring around the player
def activate_trail(surface, player):
    cx = round(player.position.x)
    cy = round(player.position.y)
    inner_radius = int(player.radius) + 2
    outer_radius = inner_radius + 4  # Slightly larger than player's radius
    for x in range(cx - outer_radius, cx + outer_radius + 1):
        for y in range(cy - outer_radius, cy + outer_radius + 1):
            dist_sq = (x - cx)**2 + (y - cy)**2
            if inner_radius**2 <= dist_sq <= outer_radius**2:  # Only activate pixels in the ring
                if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                    if surface.get_at((x, y)) == player.inactive_color:
                        surface.set_at((x, y), player.active_color)  # Activate trail

# Function to apply to every pixel in the circle
def process_pixel(surface, x, y, player):
    """Modifies the pixel at (x, y) on the surface with the given color."""
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        if surface.get_at((x, y)) != BG_COLOR and surface.get_at((x, y)) != player.inactive_color:
            player.lose()
        surface.set_at((x, y), player.inactive_color)

# Function to manually draw a circle and call `process_pixel`
def draw_trail(surface, player):
    cx = round(player.position.x)
    cy = round(player.position.y)
    radius = int(player.radius)
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            if (x - cx)**2 + (y - cy)**2 <= radius**2:  # Check if inside the circle
                process_pixel(surface, x, y, player)

def next_round():
    global game_state, background, players
    background.fill(BG_COLOR)
    sides = [0, 1, 2, 3]
    for p in players:
        x, y, rotation = calculate_starting_position(sides.pop(random.randrange(0, len(sides))))
        p.reset_to_starting_position(x, y, rotation)
    game_state = GameState.INGAME

# 2 Players is the default setting but the players can
# increase or decrease the number in the home screen
add_player()
add_player()

clock = pygame.time.Clock()
while running:
    # CALCULATING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keyboard.handle_event(event)

    if keyboard.was_key_pressed(pygame.K_ESCAPE):
        if game_state == GameState.HOME:
            # Quit game when in home screen
            running = False
        else:
            # Delete player scores and return to home screen when not already in home screen
            for p in players:
                p.score = 0
            game_state = GameState.HOME

    match game_state:
        case GameState.HOME:
            if keyboard.was_key_pressed(pygame.K_UP):
                if len(players) > 1:
                    players.pop()
            if keyboard.was_key_pressed(pygame.K_DOWN):
                add_player()
            if keyboard.was_key_pressed(pygame.K_SPACE):
                next_round()
            draw_home_screen()
        
        case GameState.INGAME:
            alive_players_count = 0
            winner = None
            for p in players:
                # Move the player
                if keyboard.is_key_down(p.left_key):
                    p.turn_left()
                elif keyboard.is_key_down(p.right_key):
                    p.turn_right()
                p.move()
                # Check if the player left the screen
                if not (SCREEN_WIDTH - p.radius > p.position.x > p.radius and SCREEN_HEIGHT - p.radius > p.position.y > p.radius + TOP_MENU_HEIGHT):
                    p.lose()
                # Check if player is still alive
                if p.alive:
                    alive_players_count += 1
                    winner = p # only has effect if alive_player_count stays at 1
            
            # DRAWING
            foreground.fill(TRANSPARENT)

            for p in players:
                p.update_gaps(1.0 / FPS)
                if not p.gap:
                    draw_trail(background, p)  # Draw the new trail
                activate_trail(background, p)  # Activate only the ring around the player
                pygame.draw.circle(foreground, p.inactive_color, (p.position.x, p.position.y), p.radius)

            # Draw text
            screen.blit(background, (0, 0))
            screen.blit(foreground, (0, 0))

            # I am handling the game over screen after all other draw calls because I want the players to
            # actually see the circles overlap the screen or another line. Otherwise the game over screen
            # would show the last frame in which no winner was defined yet.
            if alive_players_count == 0:
                message = "It's a draw!"
                if len(players) == 1:
                    message = MOTIVATIONAL_MESSAGES[random.randrange(0, len(MOTIVATIONAL_MESSAGES))]
                render_text(message, screen, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), font_xl, TEXT_COLOR, BG_COLOR)
                game_state = GameState.GAME_OVER
            elif alive_players_count == 1 and len(players) > 1: # solo mode has no winners :(
                winner.score += 1
                render_text(f"{winner.name} won!", screen, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), font_xl, winner.inactive_color, BG_COLOR)
                game_state = GameState.GAME_OVER

            pygame.draw.rect(screen, MENU_COLOR, (0, 0, SCREEN_WIDTH, TOP_MENU_HEIGHT))
            render_text("ESC: Home", screen, (51, 15), font_s, TEXT_COLOR)
            # Rendering player scores
            total_width = (len(players) - 1) * PLAYER_SCORES_GAP
            start_x = (SCREEN_WIDTH - total_width) / 2  # Centering formula
            for i in range(len(players)):
                x = start_x + i * PLAYER_SCORES_GAP
                render_text(f"{players[i].name}: {players[i].score}", screen, (x, 15), font_s, players[i].inactive_color)
        
        case GameState.GAME_OVER:
            if keyboard.was_key_pressed(pygame.K_SPACE):
                next_round()
            continue

    # Update display
    pygame.display.flip()

    # Reset pressed state on keyboard
    keyboard.reset_frame_state()

    # Control frame rate
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()