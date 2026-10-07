"""
catch: hook-vs-fish catch detection.
"""


def check_catch(hook, fish_list):
    """
    Returns the fish the hook has caught, or None.
    A catch only occurs when the hook and fish bounding rectangles overlap.
    """
    hook_rect = hook.get_rect()
    for fish in fish_list:
        if hook_rect.colliderect(fish.get_rect()):
            return fish
    return None
