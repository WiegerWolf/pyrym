import pytest
from unittest.mock import Mock
from src.core.ui import UI

# Since format_skill_label only needs a .name attribute,
# we can use a simple Mock object for the skill.
class MockSkill:
    def __init__(self, name):
        self.name = name

@pytest.mark.parametrize(
    "keybind, skill_name, remaining_cd, expected_label",
    [
        ("Q", "Shield Bash", 0, "Q Shield Bash READY"),
        ("W", "Adrenaline Rush", 2, "W Adrenaline Rush (2)"),
        ("E", "Ultra-Mega-Blast", 5, "E Ultra-Mega-Blast (5)"),
        # Assuming no truncation logic for now as per instructions.
        ("R", "A", 99, "R A (99)"),
    ],
)
def test_format_skill_label(keybind, skill_name, remaining_cd, expected_label):
    """Tests the format_skill_label helper for various cooldown states."""
    skill = MockSkill(skill_name)
    result = UI.format_skill_label(skill, keybind, remaining_cd)
    assert result == expected_label