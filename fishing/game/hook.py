from enum import Enum
import pygame


class HookState(Enum):
    IDLE = "idle"
    DROPPING = "dropping"
    RETRACTING = "retracting"


class Hook:
    def __init__(self, surface_y: int = 60, max_depth: int = 500, drop_speed: float = 4.0, retract_speed: float = 6.0):
        self.x = 400
        self.y = surface_y
        self.surface_y = surface_y
        self.max_depth = max_depth
        self.drop_speed = drop_speed
        self.retract_speed = retract_speed
        self.state = HookState.IDLE
        self.caught_fish = None
        self.can_cast = True
        self.rect = pygame.Rect(self.x, self.y, 8, 12)

    def cast(self) -> bool:
        if not getattr(self, "can_cast", True):
            return False
        if self.state == HookState.IDLE:
            self.state = HookState.DROPPING
            return True
        return False

    def snag(self, fish):
        if self.state == HookState.DROPPING and not self.caught_fish:
            self.caught_fish = fish
            fish.is_caught = True
            self.state = HookState.RETRACTING

    def update(self) -> bool:
        """Returns True if a fish has surfaced and been banked into score."""
        scored = False

        if self.state == HookState.DROPPING:
            self.y += self.drop_speed
            if self.y >= self.max_depth:
                self.y = self.max_depth
                self.state = HookState.RETRACTING

        elif self.state == HookState.RETRACTING:
            self.y -= self.retract_speed
            if self.y <= self.surface_y:
                self.y = self.surface_y
                self.state = HookState.IDLE
                if self.caught_fish:
                    scored = True
                    self.caught_fish = None

        if self.caught_fish:
            self.caught_fish.x = self.x - self.caught_fish.width // 2
            self.caught_fish.y = self.y
            self.caught_fish.rect.x = int(self.caught_fish.x)
            self.caught_fish.rect.y = int(self.caught_fish.y)

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        return scored

    def get_rect(self):
        return self.rect
