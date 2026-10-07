"""
Unit test suite for Fishing Lab implementation covering all 4 tasks.
Run with: python -m unittest test_fishing.py
"""

import pygame
import unittest
from game.hook import Hook, IDLE, CASTING, RETRACTING
from game.fish import Fish, CommonFish, FastFish, GoldenFish
from game.catch import check_catch
from game.game_engine import GameEngine, ROUND_DURATION
from game.renderer import WIDTH, SURFACE_Y, MAX_DEPTH_Y


class TestFishingLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_task_1_catch_detection(self):
        """Task 1: Catch is based on 2D overlap (AABB colliderect), not depth-only."""
        hook = Hook(x=350, surface_y=80, max_depth_y=460)
        hook.y = 200

        # Fish at same depth (y=200), but far to the left (x=50) -> should NOT catch
        far_fish = CommonFish(x=50, y=200)
        self.assertIsNone(check_catch(hook, [far_fish]))

        # Fish at same depth (y=200) and overlapping horizontally (x=350) -> SHOULD catch
        overlapping_fish = CommonFish(x=350, y=200)
        self.assertEqual(check_catch(hook, [overlapping_fish]), overlapping_fish)

        # Fish overlapping horizontally (x=350), but far in depth (y=350) -> should NOT catch
        deep_fish = CommonFish(x=350, y=350)
        self.assertIsNone(check_catch(hook, [deep_fish]))

    def test_task_2_multiple_fish_types(self):
        """Task 2: Multiple fish types differing in speed, points, size, and color."""
        common = CommonFish(x=100, y=160, speed=2.0)
        fast = FastFish(x=100, y=230, speed=4.5)
        golden = GoldenFish(x=100, y=360, speed=1.2)

        # Check speeds
        self.assertGreater(abs(fast.speed), abs(common.speed))
        self.assertLess(abs(golden.speed), abs(common.speed))

        # Check point values
        self.assertEqual(common.point_value, 10)
        self.assertEqual(fast.point_value, 25)
        self.assertEqual(golden.point_value, 50)

        # Check visual distinctness (colors and sizes)
        self.assertNotEqual(common.color, fast.color)
        self.assertNotEqual(common.color, golden.color)
        self.assertNotEqual((common.width, common.height), (fast.width, fast.height))
        self.assertNotEqual((common.width, common.height), (golden.width, golden.height))

        # Check correct score awarded on catch
        engine = GameEngine()
        engine.fish_list = [fast]
        engine.hook.x = 100
        engine.hook.y = 230
        engine.update(dt=0)  # should catch
        self.assertEqual(engine.hooked_fish, fast)

        # Retract hook to surface to score
        engine.hook.y = engine.hook.surface_y
        engine.hook.state = IDLE
        engine.update(dt=0)
        self.assertEqual(engine.score, 25)
        self.assertIsNone(engine.hooked_fish)

    def test_task_3_player_controlled_casting(self):
        """Task 3: Hook does not auto-loop; player controls cast; cannot interrupt."""
        engine = GameEngine()

        # 1. Idle hook does not cast automatically on update
        self.assertEqual(engine.hook.state, IDLE)
        for _ in range(10):
            engine.update(dt=1/60)
        self.assertEqual(engine.hook.state, IDLE)

        # 2. Player casts via Space key
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine.handle_event(space_event)
        self.assertEqual(engine.hook.state, CASTING)

        # 3. Ongoing cast cannot be interrupted by new key press
        engine.hook.y = 250  # Hook is mid-cast
        engine.handle_event(space_event)
        self.assertEqual(engine.hook.state, CASTING)
        self.assertEqual(engine.hook.y, 250)

        # 4. Retracts and returns to IDLE
        engine.hook.state = RETRACTING
        engine.hook.y = engine.hook.surface_y
        engine.update(dt=1/60)
        self.assertEqual(engine.hook.state, IDLE)

    def test_task_4_round_timer_and_restart(self):
        """Task 4: 30-second round timer, no catches when expired, and restart capability."""
        engine = GameEngine()
        self.assertEqual(engine.time_left, 30.0)
        self.assertFalse(engine.game_over)

        # Advance timer by 10 seconds
        engine.update(dt=10.0)
        self.assertAlmostEqual(engine.time_left, 20.0, places=2)
        self.assertFalse(engine.game_over)

        # Advance past 30 seconds
        engine.update(dt=25.0)
        self.assertEqual(engine.time_left, 0.0)
        self.assertTrue(engine.game_over)

        # No catches possible when time runs out
        test_fish = CommonFish(x=engine.hook.x, y=200)
        engine.fish_list = [test_fish]
        engine.hook.y = 200
        engine.update(dt=0.1)
        self.assertIsNone(engine.hooked_fish)

        # Restart via 'R' key
        engine.score = 75
        r_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        engine.handle_event(r_event)
        self.assertEqual(engine.score, 0)
        self.assertEqual(engine.time_left, 30.0)
        self.assertFalse(engine.game_over)
        self.assertEqual(engine.hook.state, IDLE)
        self.assertGreater(len(engine.fish_list), 0)


if __name__ == "__main__":
    unittest.main()
