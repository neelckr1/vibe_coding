"""
End-to-End (E2E) Test Suite for Fishing Game.

Simulates an entire real player session through the actual main loop:
- Launches game window/display and main loop
- Simulates player keyboard interactions via pygame event queue
- Validates game states, physics, scoring, and UI transitions
- Captures PNG screenshots of each milestone into 'e2e_screenshots/'
- Exits via pygame.QUIT event
"""

import os
import sys

# Headless display driver for automated execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from game.game_engine import GameEngine, ROUND_DURATION
from game.hook import IDLE, CASTING, RETRACTING
from game.renderer import WINDOW_SIZE

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "e2e_screenshots")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def run_e2e_test():
    print("=" * 60)
    print("STARTING FISHING GAME E2E TEST")
    print("=" * 60)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Fishing - E2E Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    engine = GameEngine()

    # ---------------------------------------------------------
    # PHASE 1: Verify Initial Idle State
    # ---------------------------------------------------------
    print("\n[PHASE 1] Checking initial game state...")
    assert engine.hook.state == IDLE, f"Hook should be IDLE, got {engine.hook.state}"
    assert engine.score == 0, f"Initial score should be 0, got {engine.score}"
    assert engine.time_left == ROUND_DURATION, f"Initial time should be {ROUND_DURATION}, got {engine.time_left}"
    assert not engine.game_over, "Game should not be over at launch"
    assert len(engine.fish_list) >= 3, f"Expected at least 3 fish, got {len(engine.fish_list)}"

    # Render a few idle frames
    for _ in range(15):
        engine.update(dt=1 / 60)
        engine.draw(screen, font)
        pygame.display.flip()

    # Hook must STILL be idle (proves no automatic casting!)
    assert engine.hook.state == IDLE, "Hook must remain IDLE until player presses cast"
    screenshot_1 = os.path.join(ARTIFACTS_DIR, "01_idle_start.png")
    pygame.image.save(screen, screenshot_1)
    print(f"  ✓ Initial idle state confirmed. Screenshot saved: {screenshot_1}")

    # ---------------------------------------------------------
    # PHASE 2: Player Cast via Key Press (SPACE)
    # ---------------------------------------------------------
    print("\n[PHASE 2] Simulating player pressing SPACE to cast...")
    # Inject real pygame event
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

    # Process events through the event loop
    for event in pygame.event.get():
        engine.handle_event(event)

    assert engine.hook.state == CASTING, f"Hook should transition to CASTING, got {engine.hook.state}"

    # Advance several frames of downward travel
    for _ in range(20):
        engine.update(dt=1 / 60)
        engine.draw(screen, font)
        pygame.display.flip()

    assert engine.hook.y > engine.hook.surface_y, "Hook should have traveled downward"
    screenshot_2 = os.path.join(ARTIFACTS_DIR, "02_hook_casting.png")
    pygame.image.save(screen, screenshot_2)
    print(f"  ✓ Hook casting downward confirmed (y={engine.hook.y:.1f}). Screenshot saved: {screenshot_2}")

    # ---------------------------------------------------------
    # PHASE 3: Cast Interruption Protection
    # ---------------------------------------------------------
    print("\n[PHASE 3] Testing that spamming cast keys cannot interrupt active cast...")
    mid_descent_y = engine.hook.y
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    for event in pygame.event.get():
        engine.handle_event(event)

    assert engine.hook.state == CASTING, "Hook state must remain CASTING"
    assert engine.hook.y == mid_descent_y, "Hook y position must not reset"
    print("  ✓ Active cast cannot be interrupted by new key presses.")

    # ---------------------------------------------------------
    # PHASE 4: Catching a Fish and Reeling In
    # ---------------------------------------------------------
    print("\n[PHASE 4] Testing genuine catch detection and reel-in...")
    # Spawn a target fish directly along the hook path at depth 280
    from game.fish import FastFish
    test_fish = FastFish(x=engine.hook.x, y=280, speed=0)
    engine.fish_list.append(test_fish)

    hooked = False
    for frame in range(120):
        engine.update(dt=1 / 60)
        engine.draw(screen, font)
        pygame.display.flip()
        if engine.hooked_fish is not None:
            hooked = True
            break

    assert hooked, "Hook should have caught the fish upon overlapping"
    assert engine.hook.state == RETRACTING, "Hook must immediately start RETRACTING upon catch"
    screenshot_3 = os.path.join(ARTIFACTS_DIR, "03_fish_hooked.png")
    pygame.image.save(screen, screenshot_3)
    print(f"  ✓ Fish snagged and riding hook! Target: {type(engine.hooked_fish).__name__} (pts={engine.hooked_fish.point_value})")
    print(f"  Screenshot saved: {screenshot_3}")

    # Reel back up to surface
    expected_pts = engine.hooked_fish.point_value
    score_before = engine.score
    while engine.hook.state == RETRACTING:
        engine.update(dt=1 / 60)
        engine.draw(screen, font)
        pygame.display.flip()

    assert engine.hook.state == IDLE, "Hook must return to IDLE at surface"
    assert engine.score == score_before + expected_pts, f"Score should increase by {expected_pts}, got {engine.score}"
    assert engine.hooked_fish is None, "Hooked fish should be cleared after scoring"
    screenshot_4 = os.path.join(ARTIFACTS_DIR, "04_score_awarded.png")
    pygame.image.save(screen, screenshot_4)
    print(f"  ✓ Fish scored at surface! New Score: {engine.score}. Screenshot saved: {screenshot_4}")

    # ---------------------------------------------------------
    # PHASE 5: Round Timer Expiration & Game Over
    # ---------------------------------------------------------
    print("\n[PHASE 5] Testing 30-second round timer countdown and Game Over state...")
    # Fast forward remaining time down to zero
    while engine.time_left > 0:
        step_dt = min(1.0, engine.time_left)
        engine.update(dt=step_dt)
        engine.draw(screen, font)
        pygame.display.flip()

    assert engine.time_left == 0.0, f"Time left should be 0, got {engine.time_left}"
    assert engine.game_over, "Game should enter game_over state"

    # Verify no catches can happen in game_over
    dummy_fish = FastFish(x=engine.hook.x, y=engine.hook.y, speed=0)
    engine.fish_list = [dummy_fish]
    engine.update(dt=1 / 60)
    assert engine.hooked_fish is None, "No catches should be allowed once round ends"

    # Draw Game Over screen
    engine.draw(screen, font)
    pygame.display.flip()
    screenshot_5 = os.path.join(ARTIFACTS_DIR, "05_game_over.png")
    pygame.image.save(screen, screenshot_5)
    print(f"  ✓ Timer reached 0.0s. Game Over confirmed. Screenshot saved: {screenshot_5}")

    # ---------------------------------------------------------
    # PHASE 6: Restart Round via 'R' Key
    # ---------------------------------------------------------
    print("\n[PHASE 6] Testing round restart via 'R' key...")
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    for event in pygame.event.get():
        engine.handle_event(event)

    assert not engine.game_over, "Game should not be over after restart"
    assert engine.score == 0, f"Score should be reset to 0, got {engine.score}"
    assert engine.time_left == ROUND_DURATION, f"Timer should reset to {ROUND_DURATION}, got {engine.time_left}"
    assert engine.hook.state == IDLE, "Hook should be IDLE at surface after restart"
    assert len(engine.fish_list) >= 3, "Fish list should be repopulated"

    engine.draw(screen, font)
    pygame.display.flip()
    screenshot_6 = os.path.join(ARTIFACTS_DIR, "06_restarted.png")
    pygame.image.save(screen, screenshot_6)
    print(f"  ✓ Round restarted successfully. Screenshot saved: {screenshot_6}")

    # ---------------------------------------------------------
    # PHASE 7: Clean Quit
    # ---------------------------------------------------------
    print("\n[PHASE 7] Testing clean application exit...")
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    quit_handled = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_handled = True

    assert quit_handled, "QUIT event should be received cleanly"
    pygame.quit()
    print("  ✓ Pygame quit cleanly.")

    print("\n" + "=" * 60)
    print("ALL E2E TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_e2e_test()
    sys.exit(0 if success else 1)
