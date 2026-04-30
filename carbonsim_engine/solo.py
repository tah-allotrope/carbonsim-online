from .engine import create_initial_state


def create_solo_game(
    player_name: str = "Player",
    province_name: str = "default",
    difficulty: str = "standard",
    num_years: int = 15,
) -> dict:
    """Create a solo-mode game state.

    Wraps create_initial_state() with solo-mode defaults:
    - 1 human participant + N bot participants
    - Extended year count (15 by default)
    - Difficulty-adjusted scenario selection

    This is a stub — full implementation in Phase 3.

    Args:
        player_name: Display name for the human player.
        province_name: Narrative province identifier.
        difficulty: One of "easy", "standard", "hard".
        num_years: Number of virtual years in the game.

    Returns:
        A game state dict, same shape as create_initial_state().
    """
    scenario_map = {
        "easy": "generous",
        "standard": "vietnam_pilot",
        "hard": "high_pressure",
    }
    scenario = scenario_map.get(difficulty, "vietnam_pilot")
    bot_count = {"easy": 2, "standard": 3, "hard": 5}.get(difficulty, 3)

    return create_initial_state(
        participant_count=1,
        num_years=num_years,
        scenario=scenario,
        bot_count=bot_count,
    )
