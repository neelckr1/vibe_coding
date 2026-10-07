from game.game_engine import GameEngine


def test_timer_initialization_and_countdown():
    engine = GameEngine()
    assert engine.time_remaining == 30.0
    engine.update(dt=1.5)
    assert engine.time_remaining == 28.5


def test_round_ends_at_zero_and_blocks_cast():
    engine = GameEngine()
    engine.update(dt=30.0)
    assert engine.is_game_over is True
    cast_successful = engine.hook.cast()
    assert cast_successful is False


def test_restart_resets_round():
    engine = GameEngine()
    engine.score = 50
    engine.update(dt=30.0)
    assert engine.is_game_over is True

    engine.restart()
    assert engine.time_remaining == 30.0
    assert engine.score == 0
    assert engine.is_game_over is False
