"""
Comprehensive end-to-end and stress test suite for the Fishing game.
Validates collision precision, entity physics, input handling, timer expiration,
rendering pipeline, and complete gameplay lifecycle.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import unittest
import pygame
from game.hook import Hook, IDLE, CASTING, RETRACTING
from game.fish import Fish, CommonFish, FastFish, GoldenFish
from game.catch import check_catch
from game.game_engine import GameEngine, ROUND_DURATION
from game.renderer import WIDTH, HEIGHT, SURFACE_Y, MAX_DEPTH_Y, WINDOW_SIZE


class ComprehensiveFishingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.surface = pygame.display.set_mode(WINDOW_SIZE)
        cls.font = pygame.font.SysFont("consolas", 22)

    def test_01_pixel_precision_collision(self):
        """Verify strict 2D AABB bounding box collision boundaries."""
        hook = Hook(x=350, surface_y=SURFACE_Y, max_depth_y=MAX_DEPTH_Y, width=14, height=14)
        hook.y = 200
        # Hook rect: x from 343 to 357 (width 14), y from 193 to 207 (height 14)
        h_rect = hook.get_rect()
        self.assertEqual(h_rect.left, 343)
        self.assertEqual(h_rect.right, 357)
        self.assertEqual(h_rect.top, 193)
        self.assertEqual(h_rect.bottom, 207)

        # Fish width=36, height=18. Center (x, y): rect left=x-18, right=x+18, top=y-9, bottom=y+9
        # Case A: 1 pixel to the left of the hook bounding box
        # Fish right = 342 -> center x = 324
        just_outside_left = CommonFish(x=324, y=200)
        self.assertIsNone(check_catch(hook, [just_outside_left]))

        # Case B: 1 pixel overlapping on the left boundary
        # Fish right = 344 -> center x = 326
        overlapping_left = CommonFish(x=326, y=200)
        self.assertEqual(check_catch(hook, [overlapping_left]), overlapping_left)

        # Case C: 1 pixel below the hook bounding box
        # Fish top = 208 -> center y = 217
        just_outside_bottom = CommonFish(x=350, y=217)
        self.assertIsNone(check_catch(hook, [just_outside_bottom]))

        # Case D: 1 pixel overlapping on the bottom boundary
        # Fish top = 206 -> center y = 215
        overlapping_bottom = CommonFish(x=350, y=215)
        self.assertEqual(check_catch(hook, [overlapping_bottom]), overlapping_bottom)

    def test_02_fish_movement_and_screen_wrapping(self):
        """Verify that all fish types update position correctly and wrap around screen borders."""
        common = CommonFish(x=100, y=200, speed=2.0)
        fast = FastFish(x=100, y=250, speed=4.0)
        golden = GoldenFish(x=100, y=300, speed=1.0)

        # Advance 10 frames
        for _ in range(10):
            common.update(WIDTH)
            fast.update(WIDTH)
            golden.update(WIDTH)

        self.assertAlmostEqual(common.x, 120.0, places=1)
        self.assertAlmostEqual(fast.x, 140.0, places=1)
        self.assertAlmostEqual(golden.x, 110.0, places=1)
        # Fast fish moved more distance than common, which moved more than golden
        self.assertGreater(fast.x - 100, common.x - 100)
        self.assertGreater(common.x - 100, golden.x - 100)

        # Test screen wrapping when exiting on the right
        right_exiter = CommonFish(x=WIDTH + 10, y=200, speed=2.0)
        right_exiter.update(WIDTH)
        self.assertEqual(right_exiter.x, -right_exiter.width)

        # Test screen wrapping when exiting on the left
        left_exiter = CommonFish(x=-40, y=200, speed=-2.0)
        left_exiter.update(WIDTH)
        self.assertEqual(left_exiter.x, WIDTH)

    def test_03_scoring_and_reel_in_cycle(self):
        """Test full catch lifecycle: contact, ride-up, surface reel-in, and score award."""
        engine = GameEngine()
        engine.fish_list = []  # clear initial fish

        fast_fish = FastFish(x=engine.hook.x, y=250, speed=0)
        engine.fish_list.append(fast_fish)

        # Hook starts idle, cast it
        engine.cast_hook()
        self.assertEqual(engine.hook.state, CASTING)

        # Step until hook collides with fish
        for _ in range(100):
            if engine.hooked_fish is not None:
                break
            engine.update(dt=1/60)

        # Contact made: fish should be hooked, hook state should transition to RETRACTING
        self.assertEqual(engine.hooked_fish, fast_fish)
        self.assertEqual(engine.hook.state, RETRACTING)
        # Score is NOT awarded yet mid-water
        self.assertEqual(engine.score, 0)

        # Retract back up to surface
        for _ in range(100):
            if engine.hook.state == IDLE:
                break
            # During retraction, fish coordinates must follow the hook exactly
            self.assertEqual(engine.hooked_fish.x, engine.hook.x)
            self.assertEqual(engine.hooked_fish.y, engine.hook.y)
            engine.update(dt=1/60)

        # Now hook is back at surface: score should be awarded (25 for FastFish)
        self.assertEqual(engine.hook.state, IDLE)
        self.assertIsNone(engine.hooked_fish)
        self.assertEqual(engine.score, 25)

    def test_04_input_robustness_and_rapid_keypresses(self):
        """Verify key spamming does not disrupt or restart ongoing casts."""
        engine = GameEngine()
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)

        # Initial cast with DOWN arrow
        engine.handle_event(down_event)
        self.assertEqual(engine.hook.state, CASTING)

        # Advance partially down
        engine.update(dt=1/60)
        current_y = engine.hook.y

        # Spam SPACE and DOWN 50 times
        for _ in range(50):
            engine.handle_event(space_event)
            engine.handle_event(down_event)

        # Hook must not have reset to surface
        self.assertEqual(engine.hook.state, CASTING)
        self.assertEqual(engine.hook.y, current_y)

    def test_05_mid_cast_timer_expiration(self):
        """If round timer expires while hook is mid-water, no catches occur and game ends."""
        engine = GameEngine()
        engine.time_left = 1.0  # 1 second left

        # Start cast
        engine.cast_hook()
        # Move hook down
        engine.update(dt=0.5)
        self.assertEqual(engine.hook.state, CASTING)
        self.assertFalse(engine.game_over)

        # Fish positioned in the path of the hook
        target_fish = GoldenFish(x=engine.hook.x, y=engine.hook.y + 20)
        engine.fish_list = [target_fish]

        # Timer runs out (1.0 second expires)
        engine.update(dt=1.0)
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.time_left, 0.0)

        # Hook passes through target_fish, but no catch should register
        engine.hook.y = target_fish.y
        engine.update(dt=1/60)
        self.assertIsNone(engine.hooked_fish)
        self.assertEqual(engine.score, 0)

    def test_06_rendering_pipeline_no_crashes(self):
        """Verify draw calls execute without errors in both playing and game_over states."""
        engine = GameEngine()
        # Active play draw
        engine.draw(self.surface, self.font)

        # Game over draw
        engine.game_over = True
        engine.score = 85
        engine.draw(self.surface, self.font)

    def test_07_full_game_lifecycle_simulation(self):
        """Simulate a 35-second gameplay session at 60 FPS (2100 frames)."""
        engine = GameEngine()
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        r_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)

        frames = 0
        total_casts = 0

        # Run 2100 frames (35 seconds of game time)
        while frames < 2100:
            dt = 1 / 60
            # Periodically cast if idle
            if engine.hook.state == IDLE and not engine.game_over and (frames % 90 == 0):
                engine.handle_event(space_event)
                total_casts += 1

            engine.update(dt)
            if frames % 30 == 0:
                engine.draw(self.surface, self.font)
            frames += 1

        # At frame 2100 (> 30 seconds), game must be over
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.time_left, 0.0)
        final_score = engine.score

        # Restart via 'R' key
        engine.handle_event(r_event)
        self.assertFalse(engine.game_over)
        self.assertEqual(engine.score, 0)
        self.assertEqual(engine.time_left, 30.0)
        self.assertEqual(engine.hook.state, IDLE)


if __name__ == "__main__":
    unittest.main()
