import pytest
import pygame
from game.catch import check_catch


class DummyEntity:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.x = rect.x
        self.y = rect.y
        self.width = rect.width
        self.height = rect.height


def test_no_catch_when_same_depth_but_horizontal_gap():
    hook = DummyEntity(pygame.Rect(400, 250, 10, 10))
    fish = DummyEntity(pygame.Rect(50, 250, 40, 20))  # Far left
    assert check_catch(hook, fish) is False


def test_catch_registers_on_genuine_overlap():
    hook = DummyEntity(pygame.Rect(400, 250, 10, 10))
    fish = DummyEntity(pygame.Rect(395, 245, 40, 20))  # Encompasses hook
    assert check_catch(hook, fish) is True


def test_no_catch_when_near_boundary_without_overlap():
    hook = DummyEntity(pygame.Rect(400, 250, 10, 10))
    fish = DummyEntity(pygame.Rect(411, 250, 40, 20))  # 1px gap to right
    assert check_catch(hook, fish) is False
