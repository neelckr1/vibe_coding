from game.fish import Fish, FishType


def test_fish_species_attributes():
    sardine = Fish(fish_type=FishType.COMMON, depth=150, direction=1)
    tuna = Fish(fish_type=FishType.GOLDEN, depth=250, direction=-1)

    assert sardine.points == 10
    assert tuna.points == 30
    assert abs(tuna.speed) > abs(sardine.speed)
    assert tuna.color != sardine.color


def test_fish_wrap_around():
    screen_width = 800
    fish = Fish(fish_type=FishType.COMMON, depth=100, direction=1)
    fish.x = screen_width + 10
    fish.update(screen_width)
    assert fish.x <= 0  # Wrapped back to left boundary
