from enum import Enum
import pygame


class FishType(Enum):
    COMMON = "common"
    GOLDEN = "golden"


SPECIES_CONFIG = {
    FishType.COMMON: {
        "speed": 2.0,
        "points": 10,
        "color": (70, 130, 180),   # Steel blue
        "size": (36, 16),
    },
    FishType.GOLDEN: {
        "speed": 4.5,
        "points": 30,
        "color": (255, 215, 0),    # Gold
        "size": (24, 12),
    },
}


class Fish:
    def __init__(self, fish_type: FishType, depth: int, direction: int = 1):
        config = SPECIES_CONFIG[fish_type]
        self.type = fish_type
        self.points = config["points"]
        self.point_value = config["points"]
        self.color = config["color"]
        self.width, self.height = config["size"]
        self.speed = config["speed"] * direction
        self.y = depth
        self.x = 0 if direction > 0 else 800
        self.is_caught = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, screen_width: int = 800):
        if not self.is_caught:
            self.x += self.speed
            if self.speed > 0 and self.x > screen_width:
                self.x = -self.width
            elif self.speed < 0 and self.x < -self.width:
                self.x = screen_width
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_rect(self):
        return self.rect
