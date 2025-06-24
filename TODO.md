Below are nine concrete, modular ways to add variety, depth, and long-term engagement to your prototype.  Each idea is paired with the subsystem(s) it touches plus implementation tips that map cleanly onto your existing FSM / entity architecture.

---

1. Branching Quest / Job Board  
   • NEW STATE: [`src/states/quest.py`](src/states/quest.py)  
   • UI: add a simple scrollable list to [`src/core/ui.py`](src/core/ui.py)  
   • Flow:  
     ```mermaid
     graph TD
         ExploreState --> |town tile| QuestState
         QuestState --> |accept| ExploreState
         QuestState --> |back| ExploreState
         ExploreState --> BattleState
     ```  
   • Quests are lightweight goals (e.g. *“Defeat 5 Skeletons”, “Collect 50 Gold”*).  
     Reward players with XP, gold, or a rare item, giving purpose beyond endless waves.

2. Procedural “Mini-Events” During Exploration
   • ✔ Done Step 1 — Add `MiniEvent` ABC and `ItemFindEvent`, `TrapEvent` stubs.
   • ✔ Done Step 2 — Implement weighted selection in `choose_event`.
   • ✔ Done Step 3 — Hook `trigger_random` into `ExploreState`.
   • ✔ Done Step 4 — Add logic to `ItemFindEvent` and `TrapEvent`.
   • ✔ Done Step 5 — Implement `FriendlyNPCEvent`, `PuzzleEvent`, `GoldCacheEvent`.
   • ✔ Done Step 6 — Add `register_event` for extensibility.
   • ✔ Done Step 7 — Refine logging & test `choose_event` distribution.
   • ✔ Done Step 8 — Add `flash_message` and status effect helpers.
   • Step 9 — docs (this commit)
   • Step 10 — Add side-effect unit tests for each event subclass.
   • Step 11 — Add `AnimationRequest` signal for visuals.
   • Step 12 — Add two more event types (e.g., temporary buff, mysterious stranger).

3. Status Effects (Poison, Bleed, Stun, Regeneration)  
   • Extend [`Entity`](src/entities/base.py) with `statuses: list[Status]`.  
   • Define an abstract `Status` class in [`src/entities/status.py`](src/entities/status.py) (new).  
   • In [`src/states/battle.py`](src/states/battle.py) tick `status.on_turn_start(entity)` and render icons.  
   • Adds tactical depth: defend to shrug off Bleed, use Antidote item, etc.

4. Active Skills & Cool-downs  
   • Your stamina system is solid; layer *cool-downs* on top.  
   • Add `cooldown` attribute to abilities in [`src/abilities/player_abilities.py`](src/abilities/player_abilities.py).  
   • Track per-ability timers in `Player` and `Enemy`.  
   • Sample skills: *Shield Bash (stun + dmg, 3-turn CD)*, *Adrenaline Rush (+2 stamina, 4-turn CD)*.  
   • Expose on keys `Q`, `W`, `E`, `R`.

5. Town / Hub & Shop Makeover  
   • Rename current **ShopState** to **TownState**; inside create sub-menus:  
     a) Item Shop b) Blacksmith (upgrade gear) c) Inn (heal & gossip).  
   • Inter-state transitions neatly handled by your FSM; see [`docs/fsm_spec.md`](docs/fsm_spec.md).  
   • Let gossip provide hints that seed quests (#1) or foreshadow bosses (#8).

6. Relic / Passive System (Rogue-like spice)  
   • Relics = passive modifiers (e.g. “+1 Stamina cap”, “10 % lifesteal”).  
   • Store `player.relics: set[Relic]`; resolve their effects in combat calc helpers of [`src/utils.py`](src/utils.py:40-75).  
   • Acquire via rare drops, boss chests, or quest rewards.  
   • Synergy-hunting keeps subsequent runs fresh.

7. Global Difficulty Tiers (“Depths”)  
   • After each victorious battle increment `depth`; scale enemy stats and rewards.  
   • Show depth meter in HUD (`src/core/ui.py`).  
   • At certain breakpoints spawn an *elite* version of the enemy with a guaranteed relic drop.

8. Boss Encounters with Mechanics  
   • Every *n* depths inject a **BossState** derived from BattleState but with custom AI script.  
   • Bosses showcase telegraphed attacks forcing defend or ability use:  
     • wind-up heavy slash (skip turn ➞ double dmg next turn)  
     • summon adds (targets must be cleared first)  
   • Defeating a boss unlocks a new relic slot or shop inventory tier.

9. Meta-Progression & Achievements  
   • Persist unlocks in `save.json`; simple read/write helpers in [`src/utils.py`](src/utils.py).  
   • Permanent account-level perks: +1 starting stamina, starter relic choice, cosmetics.  
   • Achievements (“Win a battle with 1 HP”, “Poison 10 enemies in one run”) award trophies shown on title screen.

---

Implementation Order Recommendation  
1. Status Effects (#3) – small, self-contained, instantly enriches combat.  
2. Procedural Mini-Events (#2) – uses existing Explore loop; adds surprise factor.  
3. Active Skills & Cool-downs (#4) – deepens decision-making.  
4. Relics (#6) – pairs nicely with #2 rewards.  
5. Quest Board & Town Rework (#1 & #5) – ties systems together and enables narrative hooks.  
6. Difficulty Depths & Bosses (#7 & #8) – escalate challenge curve.  
7. Achievements & Meta-Progression (#9) – long-term retention.

Each step is incremental, leverages your modular FSM, and delivers a clear uptick in engagement. Feel free to cherry-pick or reorder based on dev time and desired scope.