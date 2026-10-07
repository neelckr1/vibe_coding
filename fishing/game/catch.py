import pygame


def check_catch(hook, fish) -> bool:
    """
    Returns True only if the hook bounding box genuinely overlaps the fish bounding box.
    """
    hook_rect = getattr(hook, "rect", None)
    if hook_rect is None:
        if hasattr(hook, "get_rect"):
            hook_rect = hook.get_rect()
        else:
            hook_rect = pygame.Rect(hook.x, hook.y, getattr(hook, "width", 8), getattr(hook, "height", 8))

    fish_rect = getattr(fish, "rect", None)
    if fish_rect is None:
        if hasattr(fish, "get_rect"):
            fish_rect = fish.get_rect()
        else:
            fish_rect = pygame.Rect(fish.x, fish.y, getattr(fish, "width", 32), getattr(fish, "height", 16))

    return hook_rect.colliderect(fish_rect)
