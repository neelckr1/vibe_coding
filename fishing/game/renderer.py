"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
SURFACE_Y = 80
MAX_DEPTH_Y = HEIGHT - 40

WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_SKY = (140, 200, 230)
COLOR_WATER = (30, 90, 150)
COLOR_BOAT = (120, 80, 50)
COLOR_LINE = (240, 240, 240)
COLOR_HOOK = (220, 220, 220)
COLOR_TEXT = (255, 255, 255)


def draw_scene(surface, hook, fish_list):
    surface.fill(COLOR_SKY, pygame.Rect(0, 0, WIDTH, SURFACE_Y))
    surface.fill(COLOR_WATER, pygame.Rect(0, SURFACE_Y, WIDTH, HEIGHT - SURFACE_Y))

    pygame.draw.rect(surface, COLOR_BOAT, (hook.x - 40, SURFACE_Y - 20, 80, 22))

    pygame.draw.line(surface, COLOR_LINE, (hook.x, SURFACE_Y), (hook.x, hook.y), 2)
    pygame.draw.circle(surface, COLOR_HOOK, (int(hook.x), int(hook.y)), 7)

    for fish in fish_list:
        pygame.draw.ellipse(surface, fish.color, fish.get_rect())


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)


def draw_game_over(surface, font, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    lines = [
        ("TIME'S UP! ROUND OVER", (255, 220, 80)),
        (f"Final Score: {score}", (255, 255, 255)),
        ("Press 'R' or SPACE to Play Again", (180, 220, 255)),
    ]
    center_y = surface.get_height() // 2 - 36
    for i, (text, color) in enumerate(lines):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(surface.get_width() // 2, center_y + i * 36))
        surface.blit(surf, rect)

