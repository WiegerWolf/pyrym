# Boosts Rework Plan

## Goal
Convert permanent boosts in the shop to repeatable, percentage-based upgrades that scale in price like a leveling system.

## Summary of Changes
* Damage Boost: +5 % total damage per purchase.
* Max-HP Boost: +10 % maximum HP (heals to full) per purchase.
* Upgrades are repeatable; players may buy any number of levels if they have enough XP.
* XP cost starts at 50 XP (damage) and 90 XP (HP) and grows exponentially by 1.9× per level.

## New Configuration Constants (src/config.py)
```python
# --- Boosts rework ---
DAMAGE_BOOST_PCT = 0.05       # 5 %
MAX_HP_BOOST_PCT = 0.10       # 10 %

DAMAGE_BOOST_BASE_COST = 50   # XP
HP_BOOST_BASE_COST = 90       # XP
BOOST_COST_GROWTH = 1.9       # Exponential multiplier per level
```

## Utility
```python
def scaled_cost(base: int, level: int, growth: float) -> int:
    return int(round(base * (growth ** level)))
```

## Player Entity (src/entities/player.py)
* New attributes
  * `damage_mult: float` (default 1.0)
  * `max_hp_mult: float` (default 1.0)
  * `damage_boost_lvl: int` (default 0)
  * `hp_boost_lvl: int` (default 0)
* Modify damage calculations:  
  `final = (base_damage * damage_mult) + flat_bonuses`
* Override `max_health` property to apply multiplier.
* When `max_hp_mult` increases, call `heal(self.max_health)` to restore full health.

## ShopState (src/states/shop.py)
* `_build_inventory` now regenerates dynamic `cost` and `desc` each frame:
  * `cost` uses `scaled_cost(...)` with current level.
  * `desc` shows next level effect and cost.
* Purchase callbacks:
  * Spend XP `player.spend_xp(cost)`.
  * Increment level.
  * Increase multiplier (`damage_mult += DAMAGE_BOOST_PCT`, etc.).
  * Heal after HP boost.
* Remove one-time purchase guard.

## UI / Feedback
* Shop item text greys out only if player lacks XP.
* Optionally display active boost levels in HUD:  
  "DMG +15 %, HP +20 %".

## Balance Rationale
Starting costs are intentionally low to encourage early investment; exponential growth quickly turns them into a long-term XP sink.

## Migration
Existing saves default to level 0 (multipliers 1.0) which matches current balance. Old flat upgrade constants remain unused but preserved for compatibility.

## Diagram
```mermaid
classDiagram
    class Player {
        +float damage_mult
        +float max_hp_mult
        +int damage_boost_lvl
        +int hp_boost_lvl
    }
    Player <.. ShopState : modifies