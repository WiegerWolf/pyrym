# Always-Visible Numbered Inventory

## Goal
Simplify item usage by displaying the player’s grouped inventory permanently and letting the player press **1-9** at any time to use the corresponding item.

## Behaviour
* The bottom-right corner lists at most nine grouped inventory items.
* Each line is prefixed with a number key, e.g. `1.`–`9.` followed by the item name and quantity:

```
1. Healing Potion x3
2. Gold Pile x1
3. Elixir x2
```

* When the player presses the matching number key while exploring or in battle, the item is immediately used through `handle_item_use`.
* Excess grouped items (>9) are not shown and cannot be used until space frees up.
* The `I` key / item-menu flow is removed.

## Code Changes

### 1. UI Rendering  
File [`src/core/ui.py`](src/core/ui.py)

* Update `render_inventory` to:
  * Call `group_inventory` instead of using `Counter`.
  * Enumerate the **first nine** groups and draw  
    ```python
    text = f"{idx+1}. {item.name} x{qty}"
    ```
  * Keep existing coordinates `(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 110)` and font settings.

### 2. Input Flow

#### Battle  
File [`src/states/battle.py`](src/states/battle.py)

* Remove `item_menu_open`, `_toggle_item_menu`, and `_handle_item_menu`.
* In `_handle_player_actions`  
  * Delete the `use_item` branch.  
  * If `signals["number_keys"]` exists, call  
    ```python
    handle_item_use(
        self.player,
        signals["number_keys"][0],
        lambda m: add_to_log(self.battle_log, m)
    )
    ```  
  * Keep existing attack/defend/flee logic.

#### Explore  
File [`src/states/explore.py`](src/states/explore.py)

* Remove `item_menu_open` and `_handle_item_menu`.
* In `_handle_player_actions`, treat `number_keys` exactly as in battle.

### 3. Utils
No change needed; `handle_item_use` already maps keycodes 1-9 → grouped-inventory indices.

### 4. Documentation / Hints
Remove references to “`I` = inventory” from any on-screen help text and docs.

## Sequence Diagram
```mermaid
sequenceDiagram
    participant Player
    participant Loop as PygameLoop
    participant State as Battle/ExploreState
    participant UI
    participant Utils

    Player->>Loop: press "3"
    Loop->>State: signals {number_keys:[K_3]}
    State->>Utils: handle_item_use(player, K_3, logger)
    Utils-->>State: {"success": true}
    State->>UI: UI.notify(...)
    State->>UI: render_inventory(...)
```

## Estimated Effort
~6 targeted edits, no new Python files. Regression risk low; grouped-inventory path already exists.