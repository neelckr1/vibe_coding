"""
Script to record exact 10-second gameplay videos (600 frames at 60 FPS)
for both 'Before' (buggy baseline) and 'After' (fixed with all features).
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import imageio
import pygame
import numpy as np

VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "fishing", "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)


def record_before_video():
    """Records 10 seconds of the original buggy baseline game."""
    print("Recording 'Before' video (showing catch detection bug)...")
    pygame.init()
    width, height = 700, 500
    surface_y = 80
    max_depth_y = height - 40
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont("consolas", 22)

    # Original Buggy Hook
    class BuggyHook:
        def __init__(self):
            self.x = width / 2
            self.y = surface_y
            self.surface_y = surface_y
            self.max_depth_y = max_depth_y
            self.speed = 5
            self.state = "idle"

        def start_cast(self):
            self.state = "casting"
            self.y = self.surface_y

        def update(self):
            if self.state == "casting":
                self.y += self.speed
                if self.y >= self.max_depth_y:
                    self.y = self.max_depth_y
                    self.state = "retracting"
            elif self.state == "retracting":
                self.y -= self.speed
                if self.y <= self.surface_y:
                    self.y = self.surface_y
                    self.state = "idle"

        def catch_fish(self):
            self.state = "retracting"

    # Original Fish
    class BuggyFish:
        def __init__(self, x, y, speed):
            self.x = float(x)
            self.y = y
            self.speed = speed
            self.width = 36
            self.height = 18
            self.point_value = 10
            self.color = (80, 180, 220)

        def update(self):
            self.x += self.speed
            if self.speed > 0 and self.x > width:
                self.x = -self.width
            elif self.speed < 0 and self.x < -self.width:
                self.x = width

        def get_rect(self):
            return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)

    hook = BuggyHook()
    fish_list = [
        BuggyFish(x=80, y=180, speed=2),
        BuggyFish(x=600, y=280, speed=-2),
        BuggyFish(x=150, y=380, speed=3),
    ]
    hooked_fish = None
    score = 0

    fps = 60
    total_frames = 10 * fps  # 10 seconds
    output_path = os.path.join(VIDEOS_DIR, "gameplay_before_bug.mp4")
    writer = imageio.get_writer(output_path, fps=fps, codec="libx264")

    for frame in range(total_frames):
        # Auto-cast loop
        if hook.state == "idle":
            hook.start_cast()

        hook.update()
        for f in fish_list:
            f.update()

        if hooked_fish is not None:
            hooked_fish.x = hook.x
            hooked_fish.y = hook.y
            if hook.state == "idle":
                score += hooked_fish.point_value
                # Respawn
                fish_list.append(BuggyFish(x=50, y=hooked_fish.y, speed=hooked_fish.speed))
                hooked_fish = None
        else:
            # Buggy check: only depth tolerance!
            for f in fish_list:
                if abs(hook.y - f.y) < 10:
                    hooked_fish = f
                    fish_list.remove(f)
                    hook.catch_fish()
                    break

        # Draw scene
        screen.fill((140, 200, 230), pygame.Rect(0, 0, width, surface_y))
        screen.fill((30, 90, 150), pygame.Rect(0, surface_y, width, height - surface_y))
        pygame.draw.rect(screen, (120, 80, 50), (hook.x - 40, surface_y - 20, 80, 22))
        pygame.draw.line(screen, (240, 240, 240), (hook.x, surface_y), (hook.x, hook.y), 2)
        pygame.draw.circle(screen, (220, 220, 220), (int(hook.x), int(hook.y)), 7)

        for f in fish_list:
            pygame.draw.ellipse(screen, f.color, f.get_rect())
        if hooked_fish is not None:
            pygame.draw.ellipse(screen, hooked_fish.color, hooked_fish.get_rect())

        # Texts
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render("BUG DEMO: Depth-only catch across screen", True, (255, 220, 80)), (130, 10))

        # Capture frame
        frame_data = pygame.surfarray.array3d(screen)
        frame_data = np.transpose(frame_data, (1, 0, 2))  # (H, W, C)
        writer.append_data(frame_data)

    writer.close()
    print(f"  ✓ 'Before' video saved successfully: {output_path}")


def record_after_video():
    """Records 10 seconds of the fixed feature-complete game."""
    print("Recording 'After' video (showing fixed features)...")
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fishing"))
    from game.game_engine import GameEngine
    from game.hook import HookState

    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont("consolas", 22)

    engine = GameEngine()
    fps = 60
    total_frames = 10 * fps
    output_path = os.path.join(VIDEOS_DIR, "gameplay_after_fixed.mp4")
    writer = imageio.get_writer(output_path, fps=fps, codec="libx264")

    # Scripted interactions:
    # Frame 60 (1.0s): Cast 1
    # Frame 360 (6.0s): Cast 2
    space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)

    for frame in range(total_frames):
        if frame == 60:
            engine.handle_input(space_event)
        elif frame == 360:
            engine.handle_input(space_event)

        engine.update(dt=1 / fps)
        engine.draw(screen, font)

        frame_data = pygame.surfarray.array3d(screen)
        frame_data = np.transpose(frame_data, (1, 0, 2))
        writer.append_data(frame_data)

    writer.close()
    print(f"  ✓ 'After' video saved successfully: {output_path}")


if __name__ == "__main__":
    record_before_video()
    record_after_video()
