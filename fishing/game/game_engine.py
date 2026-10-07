"""
GameEngine: owns the hook, fish entities, round timer, scoring, and input handling.
"""

import random
import pygame

from game.hook import Hook, IDLE
from game.fish import Fish, CommonFish, FastFish, GoldenFish
from game.catch import check_catch
from game.renderer import WIDTH, HEIGHT, SURFACE_Y, MAX_DEPTH_Y

ROUND_DURATION = 30.0


class GameEngine:
    def __init__(self):
        self.hook = Hook(x=WIDTH / 2, surface_y=SURFACE_Y, max_depth_y=MAX_DEPTH_Y, speed=5)
        self.hooked_fish = None
        self.score = 0
        self.time_left = ROUND_DURATION
        self.game_over = False
        self.fish_list = self._create_initial_fish()

    def _create_initial_fish(self):
        """Creates an initial variety of fish swimming at different depths and speeds."""
        return [
            CommonFish(x=80, y=160, speed=2.2),
            FastFish(x=450, y=230, speed=-4.2),
            CommonFish(x=200, y=300, speed=-2.0),
            GoldenFish(x=100, y=360, speed=1.2),
            FastFish(x=350, y=420, speed=4.0),
        ]

    def _respawn_fish(self):
        """Spawns a new fish to keep the pond populated throughout the round."""
        depth = random.choice([160, 230, 300, 360, 420])
        direction = random.choice([-1, 1])
        start_x = -50 if direction > 0 else WIDTH + 50
        roll = random.random()
        if roll < 0.50:
            new_fish = CommonFish(x=start_x, y=depth, speed=2.2 * direction)
        elif roll < 0.85:
            new_fish = FastFish(x=start_x, y=depth, speed=4.2 * direction)
        else:
            new_fish = GoldenFish(x=start_x, y=depth, speed=1.2 * direction)
        self.fish_list.append(new_fish)

    def handle_event(self, event):
        """Handles player input for casting and round restarting."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_DOWN):
                if self.game_over:
                    self.restart()
                else:
                    self.cast_hook()
            elif event.key == pygame.K_r:
                self.restart()

    def cast_hook(self):
        """Starts a cast only if the hook is idle and the round is active."""
        if not self.game_over and self.hook.state == IDLE:
            self.hook.start_cast()

    def restart(self):
        """Resets the round timer, score, hook, and fish for a new game."""
        self.score = 0
        self.time_left = ROUND_DURATION
        self.game_over = False
        self.hooked_fish = None
        self.hook.state = IDLE
        self.hook.y = self.hook.surface_y
        self.fish_list = self._create_initial_fish()

    def update(self, dt=1 / 60):
        # Update round countdown timer
        if not self.game_over:
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left <= 0:
                self.time_left = 0.0
                self.game_over = True

        # Hook movement updates
        self.hook.update()

        # Fish movement updates
        for fish in self.fish_list:
            fish.update(WIDTH)

        # Handle hooked fish and catch detection
        if self.hooked_fish is not None:
            self.hooked_fish.x = self.hook.x
            self.hooked_fish.y = self.hook.y
            if self.hook.state == IDLE:
                self.score += self.hooked_fish.point_value
                self.hooked_fish = None
                if not self.game_over:
                    self._respawn_fish()
        elif not self.game_over:
            # Catch detection is only active while the round is running
            caught = check_catch(self.hook, self.fish_list)
            if caught is not None:
                self.fish_list.remove(caught)
                self.hooked_fish = caught
                self.hooked_fish.x = self.hook.x
                self.hooked_fish.y = self.hook.y
                self.hook.catch_fish()

    def draw(self, surface, font):
        from game import renderer
        draw_list = list(self.fish_list)
        if self.hooked_fish is not None:
            draw_list.append(self.hooked_fish)
        renderer.draw_scene(surface, self.hook, draw_list)

        # UI: Score display (top-left)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))

        # UI: Timer display (top-right)
        time_color = (255, 80, 80) if self.time_left <= 5 and not self.game_over else (255, 255, 255)
        renderer.draw_text(surface, font, f"Time: {int(self.time_left)}s", (WIDTH - 130, 10), color=time_color)

        # Controls hint when idle
        if not self.game_over and self.hook.state == IDLE:
            renderer.draw_text(surface, font, "Press SPACE to Cast", (WIDTH // 2 - 105, 10), color=(240, 240, 240))

        # Game Over Banner
        if self.game_over:
            renderer.draw_game_over(surface, font, self.score)
