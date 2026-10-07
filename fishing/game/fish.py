"""
Fish: swims horizontally at a fixed depth, wrapping around when it
exits the screen. The starter has one fish type; Task 2 adds more.
"""

import pygame


class Fish:
    def __init__(self, x, y, speed, width=36, height=18, point_value=10, color=(80, 180, 220)):
        self.x = float(x)
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.point_value = point_value
        self.color = color

    def update(self, screen_width):
        self.x += self.speed
        if self.speed > 0 and self.x > screen_width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = screen_width

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height,
        )


class CommonFish(Fish):
    """Common fish: standard speed, medium size, 10 points."""
    def __init__(self, x, y, speed=2.0):
        super().__init__(
            x=x, y=y, speed=speed,
            width=36, height=18,
            point_value=10, color=(80, 180, 220),
        )


class FastFish(Fish):
    """Fast darting fish: high speed, smaller size, 25 points."""
    def __init__(self, x, y, speed=4.5):
        super().__init__(
            x=x, y=y, speed=speed,
            width=26, height=14,
            point_value=25, color=(240, 120, 50),
        )


class GoldenFish(Fish):
    """Trophy golden fish: slow speed, large size, 50 points."""
    def __init__(self, x, y, speed=1.2):
        super().__init__(
            x=x, y=y, speed=speed,
            width=50, height=26,
            point_value=50, color=(245, 215, 60),
        )
