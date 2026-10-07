import os
import sys
from pathlib import Path
import pytest
import pygame

# Ensure game and tests packages are discoverable
root_dir = Path(__file__).resolve().parent.parent
fishing_dir = root_dir / "fishing" if (root_dir / "fishing").exists() else root_dir
for p in [str(fishing_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="session", autouse=True)
def setup_headless_pygame():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()
