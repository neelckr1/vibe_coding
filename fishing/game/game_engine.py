import random
import pygame
from game.hook import Hook, HookState
from game.fish import Fish, FishType
from game.catch import check_catch
from game.renderer import WIDTH, HEIGHT, SURFACE_Y, MAX_DEPTH_Y, draw_scene, draw_text, draw_game_over


class GameEngine:
    ROUND_DURATION = 30.0

    def __init__(self):
        self.score = 0
        self.time_remaining = self.ROUND_DURATION
        self.is_game_over = False
        self.hook = Hook(surface_y=SURFACE_Y, max_depth=MAX_DEPTH_Y)
        self.fish_list = []
        self._spawn_fish()

    def _spawn_fish(self):
        # Spawns combination of COMMON and GOLDEN fish at varied depths
        self.fish_list = [
            Fish(fish_type=FishType.COMMON, depth=160, direction=1),
            Fish(fish_type=FishType.GOLDEN, depth=240, direction=-1),
            Fish(fish_type=FishType.COMMON, depth=320, direction=-1),
            Fish(fish_type=FishType.GOLDEN, depth=400, direction=1),
            Fish(fish_type=FishType.COMMON, depth=450, direction=1),
        ]

    def _respawn_one(self):
        depth = random.choice([160, 240, 320, 400, 450])
        direction = random.choice([-1, 1])
        ftype = FishType.COMMON if random.random() < 0.65 else FishType.GOLDEN
        self.fish_list.append(Fish(fish_type=ftype, depth=depth, direction=direction))

    def update(self, dt: float = 1 / 60):
        if self.is_game_over:
            return

        self.time_remaining = max(0.0, self.time_remaining - dt)
        if self.time_remaining <= 0.0:
            self.time_remaining = 0.0
            self.is_game_over = True
            self.hook.can_cast = False
            return

        for fish in self.fish_list:
            fish.update(WIDTH)

        if self.hook.state == HookState.DROPPING:
            for fish in self.fish_list:
                if not fish.is_caught and check_catch(self.hook, fish):
                    self.hook.snag(fish)
                    break

        hooked_fish_ref = self.hook.caught_fish
        banked = self.hook.update()
        if banked and hooked_fish_ref:
            self.score += hooked_fish_ref.points
            if hooked_fish_ref in self.fish_list:
                self.fish_list.remove(hooked_fish_ref)
            self._respawn_one()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_game_over:
                if event.key in (pygame.K_r, pygame.K_SPACE):
                    self.restart()
            else:
                if event.key in (pygame.K_SPACE, pygame.K_DOWN):
                    self.hook.cast()

    def handle_event(self, event):
        """Alias for handle_input."""
        self.handle_input(event)

    def restart(self):
        self.score = 0
        self.time_remaining = self.ROUND_DURATION
        self.is_game_over = False
        self.hook = Hook(surface_y=SURFACE_Y, max_depth=MAX_DEPTH_Y)
        self.hook.can_cast = True
        self._spawn_fish()

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.hook, self.fish_list)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        time_color = (255, 80, 80) if self.time_remaining <= 5 else (255, 255, 255)
        renderer.draw_text(surface, font, f"Time: {int(self.time_remaining)}s", (WIDTH - 130, 10), color=time_color)
        if not self.is_game_over and self.hook.state == HookState.IDLE:
            renderer.draw_text(surface, font, "Press SPACE to Cast", (WIDTH // 2 - 105, 10), color=(240, 240, 240))
        if self.is_game_over:
            renderer.draw_game_over(surface, font, self.score)
