import pygame
from game.game_engine import GameEngine
from game.fish import Fish, FishType
from game.hook import HookState


def test_full_game_lifecycle_e2e():
    # 1. Initialize Game
    engine = GameEngine()
    engine.fish_list = []  # Clear random spawn for deterministic verification
    assert engine.time_remaining == 30.0
    assert engine.score == 0
    assert engine.hook.state == HookState.IDLE

    # Place a Golden fish at (400, 100) and a Common fish far away at (50, 100)
    golden_fish = Fish(FishType.GOLDEN, depth=100, direction=0)
    golden_fish.x = 390
    golden_fish.rect.x = 390
    golden_fish.rect.y = 100

    distant_fish = Fish(FishType.COMMON, depth=100, direction=0)
    distant_fish.x = 50
    distant_fish.rect.x = 50
    distant_fish.rect.y = 100

    engine.fish_list = [golden_fish, distant_fish]

    # 2. Trigger Player Cast via Spacebar event
    space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    engine.handle_input(space_event)
    assert engine.hook.state == HookState.DROPPING

    # 3. Prevent duplicate interrupt cast
    engine.handle_input(space_event)
    assert engine.hook.state == HookState.DROPPING

    # 4. Step game until hook reaches depth 100
    while engine.hook.y < 100 and engine.hook.state == HookState.DROPPING:
        engine.update(dt=0.016)

    # 5. Overlap detection verification
    # Golden fish must be snagged; distant fish must remain free
    assert engine.hook.caught_fish == golden_fish
    assert distant_fish.is_caught is False
    assert engine.hook.state == HookState.RETRACTING

    # 6. Step game until hook fully returns to surface
    while engine.hook.state == HookState.RETRACTING:
        engine.update(dt=0.016)

    assert engine.hook.state == HookState.IDLE
    assert engine.score == 30  # Golden fish value banked

    # 7. Advance timer to expire round
    engine.update(dt=30.0)
    assert engine.is_game_over is True
    assert engine.time_remaining == 0.0

    # 8. Verify casts blocked during Game Over
    engine.handle_input(space_event)
    assert engine.hook.state == HookState.IDLE

    # 9. Verify restart reset cycle
    restart_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
    engine.handle_input(restart_event)
    assert engine.is_game_over is False
    assert engine.time_remaining == 30.0
    assert engine.score == 0
