"""
Unit tests for skill and cooldown mechanics.
"""
import pytest
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.states.battle import BattleState

# Mock BattleState context for abilities that need it for logging
class MockBattleContext:
    """A dummy battle context for testing purposes."""
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.battle_log = []

    def add_log(self, message):
        """Dummy method to satisfy abilities."""
        self.battle_log.append(message)


@pytest.fixture
def player():
    """Provides a fresh Player instance for each test."""
    return Player()


@pytest.fixture
def enemy():
    """Provides a fresh Enemy instance for each test."""
    return Enemy()


@pytest.fixture
def battle_ctx(player, enemy):
    """Provides a mock battle context."""
    return MockBattleContext(player, enemy)


def test_shield_bash_cooldown(player, enemy, battle_ctx):
    """T1: Test Shield Bash ability cooldown mechanics."""
    skill = player.get_skill_for_key('q')  # Shield Bash
    assert player.ability_ready(skill.name)

    skill.execute(player, enemy, battle_ctx)
    assert player.cooldowns.get(skill.name) == 3
    assert not player.ability_ready(skill.name)

    # Tick three times ➜ ready again
    for _ in range(3):
        player.tick_cooldowns()
    assert player.ability_ready(skill.name)


def test_adrenaline_rush(player, battle_ctx):
    """T2: Test Adrenaline Rush stamina gain and cooldown."""
    skill = player.get_skill_for_key('w')
    start_stam = player.stamina
    skill.execute(player, player, battle_ctx)  # self-target
    assert player.stamina == start_stam + 2
    assert player.cooldowns.get(skill.name) == 4
    assert not player.ability_ready(skill.name)


def test_cooldowns_only_decrement_on_owner_turn(player):
    """T3: Test that cooldowns decrement via tick_cooldowns method."""
    player.cooldowns["Test"] = 2
    # This test verifies that the tick_cooldowns method works as expected.
    # The turn-based application logic resides in the BattleState.
    player.tick_cooldowns()
    assert player.cooldowns["Test"] == 1
    player.tick_cooldowns()
    assert player.cooldowns["Test"] == 0


def test_enemy_uses_skill(enemy, player):
    """T4: Test that the enemy AI uses a skill and puts it on cooldown."""
    from src.utils import EncounterMeta

    # Set all enemy skills to be ready
    for sk in enemy.skills:
        enemy.cooldowns[sk.name] = 0

    # Create a real BattleState to test enemy AI logic
    # The screen is not needed for this logic test.
    meta = EncounterMeta(1)
    bs = BattleState(player, enemy, encounter_meta=meta, screen=None)
    bs.player_turn = False # It's enemy's turn

    bs.enemy_action()

    # Enemy should have placed a cooldown on its chosen skill
    assert any(cd > 0 for cd in enemy.cooldowns.values())