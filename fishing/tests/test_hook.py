from game.hook import Hook, HookState


def test_hook_starts_idle_at_surface():
    hook = Hook(surface_y=50, max_depth=400)
    assert hook.state == HookState.IDLE
    assert hook.y == 50


def test_cast_triggers_descent():
    hook = Hook(surface_y=50, max_depth=400)
    hook.cast()
    assert hook.state == HookState.DROPPING
    hook.update()
    assert hook.y > 50


def test_cast_ignored_while_active():
    hook = Hook(surface_y=50, max_depth=400)
    hook.cast()
    hook.y = 100
    hook.cast()  # Attempt duplicate input
    assert hook.state == HookState.DROPPING
    assert hook.y == 100


def test_hook_reverses_at_max_depth():
    hook = Hook(surface_y=50, max_depth=400)
    hook.cast()
    hook.y = 400
    hook.update()
    assert hook.state == HookState.RETRACTING
