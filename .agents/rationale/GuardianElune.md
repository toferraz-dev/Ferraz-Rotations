# GuardianElune — rationale
Every technical comment that used to live in `FerrazGuardianElune.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "1.8.0"

`FerrazGuardianElune.yaml` line 1

```
=============================================================================
Guardian Druid — spec 104 — patch 12.1 (Midnight) — Elune's Chosen, M+.
=============================================================================

LISTS
  main            plumbing, form, survival, utility, delegates damage.
  set_tank_var    reads the Encounter Timeline into 2 variables.
  defensives      Barkskin / Survival Instincts / Frenzied Regen.
  cooldowns       Barkskin, Lunar Beam, Berserk/Incarnation, racials.
  bear            form + rage spending, shared, runs before st/aoe.
  st / aoe        damage priority, <2 / 2+ enemies (var.aoe_mode).

ST: Moonfire uptime -> Thrash (Lunar Calling) -> Thrash to stacks -> Mangle
-> Moonfire (Galactic Guardian) -> Thrash on CD -> Moonfire (Lunation) ->
Swipe filler. AoE: same but both Thrash lines promoted above Moonfire, no
Lunation slot.

Measured with SimC 1210-01, fight_style=DungeonSlice, against this
character's actual gear/talents. Harness sim/ab_test.py, target_error=0.15
(~±0.08%) — under ~0.2% is noise and not quoted. NOT validated: everything
defensive (no M+ damage-intake model) — defensives list, tank-buster
prediction, var.heavy_incoming, all Defensive HP/Prediction sliders.

Untalented on this character (harmless dead lines, flagged inline): Red
Moon, Convoke the Spirits, Sundering Roar, Ravage, Bristling Fur, Fluid
Form, Moonkin Form, Wildpower Surge, Killing Blow, Fount of Strength, the
Rake/Rip/Shred/Ferocious Bite catweave.

Numeric spell IDs (name is ambiguous): 77758 Thrash(Bear) vs 106832
Thrash(Cat); 213764 Swipe(Bear) vs 106785 Swipe(Cat); 1261868 HotW in Cat
Form (button morphs); 1307881 Gory Fur (3 spells share the display name).
=============================================================================
```

---

## spell_overrides:

`FerrazGuardianElune.yaml` line 47

```
=============================================================================
SPELL OVERRIDES — AND-ed into every occurrence of that spell in the file.
=============================================================================
```

---

## incarnation_guardian_of_ursoc: "!buff.incarnation_guardian_of_ursoc.up"

`FerrazGuardianElune.yaml` line 51

```
Maul and Mangle deliberately NOT overridden globally: an old Mangle
override (Gore+low rage+Thrash-on-CD+<=3 enemies, all at once) cut it
from ~78 to ~15 casts/fight — removing it measured +1.5% ST, +4.9% at 5.
Per-line conditions in bear/st/aoe do the real gating now.

Blocks re-suggesting Incarnation while its own buff is up.
```

---

## moonfire: "!talent.lunar_calling.enabled|cooldown.77758.down|enemies.combat.8y=0"

`FerrazGuardianElune.yaml` line 59

```
Lunar Calling makes Thrash cast Moonfire — only allow raw Moonfire when
untalented, Thrash is on CD, or nothing is in Thrash range.
```

---

## barkskin: "(!player.inmythicplus|fight_remains>=20|player.on_last_boss)&(variable.tank_buster_remains<=1|variable.tank_buster_casting|variable.tank_buster_remains>34)"

`FerrazGuardianElune.yaml` line 63

```
Barkskin held for a predicted tank buster (Encounter Timeline, see
set_tank_var) unless the fight is short/final enough that holding is pointless.
```

---

## config:

`FerrazGuardianElune.yaml` line 67

```
=============================================================================
CONFIG — defensive defaults are unvalidated by simulation.
=============================================================================
```

---

## about:

`FerrazGuardianElune.yaml` line 71

```
Display-only build stamp — keep in sync with version:/patch: above.
```

---

## recommended_talents:

`FerrazGuardianElune.yaml` line 78

```
Exact string every number here was measured against (sim/Tassiana_guardian.simc).
```

---

## survival_instincts_hp_pct:

`FerrazGuardianElune.yaml` line 85

```
=== DEFENSIVE HP THRESHOLDS === (reactive: fire once HP already dropped)
```

---

## survival_instincts_dmg_pct:

`FerrazGuardianElune.yaml` line 108

```
=== PREDICTED INCOMING DAMAGE THRESHOLDS ===
Proactive. incoming.mitigated.pct is post-defensives, so NOT comparable
to the HP sliders above (40 here != 40 there).
```

---

## ironfur_dmg_pct:

`FerrazGuardianElune.yaml` line 125

```
Drives var.heavy_incoming: above this, rage goes to Ironfur not Raze/Maul.
```

---

## rage_deficit_maul:

`FerrazGuardianElune.yaml` line 134

```
=== RAGE SPENDING === (100 cap on this build — default 20 fires at 80+ rage)
```

---

## auto_hotw:

`FerrazGuardianElune.yaml` line 143

```
=== COOLDOWN CONFIGURATIONS ===
HotW weave is the single most valuable thing here (-15% DungeonSlice if
removed). These 3 sliders gate it — loosening all three measured -3.3%.
```

---

## use_potion:

`FerrazGuardianElune.yaml` line 168

```
Combat potion. The file carried NO potion line at all before 1.1, which is
why every variant below beats the old baseline by so much.
```

---

## potion_sync_burst:

`FerrazGuardianElune.yaml` line 177

```
Measured on DungeonSlice against this file's own priority:
    sync with Incarnation/Berserk   +3.45%
    fire as soon as it is ready     +5.34%
    sync, but not if Berserk >30s   +3.27%   (no better than plain sync)
Syncing loses because the burst itself is deliberately held for the HotW
weave (see the berserk/incarnation lines in `cooldowns`), so "wait for
Incarnation" leaves the potion unused through that whole window.
```

---

## lunar_beam_moving_check:

`FerrazGuardianElune.yaml` line 191

```
Lunar Beam plants a ground effect; casting it while running wastes it.
```

---

## MO_moonfire:

`FerrazGuardianElune.yaml` line 197

```
=== MOUSEOVER CONFIGURATIONS ===
```

---

## engine_loot_nearby:

`FerrazGuardianElune.yaml` line 207

```
=============================================================================
VARIABLES
=============================================================================
=== ENGINE & DISPEL CONFIGURATIONS ===
Inlined from Simia's _shared.yaml instead of inherited, so every piece has
a toggle. See the `engine` list for what was left out and why.
Druid removes POISON and CURSE only (remove_corruption 2782) plus enrage
offensively (soothe 2908) — simia_data_dump/_dispeldata.yaml. The .list
suffix applies Simia's own dispel_list filter.
UNVALIDATED: SimC models none of this.
```

---

## aoe_mode: enemies.combat.8y>=2&state.aoe

`FerrazGuardianElune.yaml` line 299

```
2+ enemies (threshold: 2 measured +0.70%, 4 measured -0.79% vs 3), and the
user's AoE toggle.
```

---

## heavy_incoming: incoming.mitigated.pct>=config.ironfur_dmg_pct

`FerrazGuardianElune.yaml` line 303

```
Big hit predicted -> routes rage to Ironfur over Raze/Maul. Unmeasured:
SimC has no equivalent prediction, treats this as permanently false.
```

---

## hotw_weave: config.auto_hotw&talent.heart_of_the_wild&cooldown_bypass.heart_of_the_wild.ready&target.valid&target.attackable&player.combat&combat.time>=config.hotw_delay&health.pct>=config.hotw_hp_pct&buff.ironfur.up&!buff.incarnation_guardian_of_ursoc.up&!buff.berserk.up

`FerrazGuardianElune.yaml` line 307

```
Gate for the HotW weave: feature on, talented, ready, live target,
combat running long enough, HP above floor, Ironfur already up, no
burst window active (burst and weave compete for the same GCDs).
```

---

## engine:

`FerrazGuardianElune.yaml` line 313

```
Everything spell_queue / sanity_checks / auto_target / auto_heal used to do,
inlined so each piece is configurable. `sanity_checks` is not just guards —
it also calls auto_dispel, affix, auto_purge_enrage, auto_brez, auto_rez and
auto_combat_potion, and that last one fought this file's own combat_potion
line. The five return guards are copied verbatim; dropping any of them lets
the rotation fire while dead or mounted.
Not copied (no Druid content): anti_cc, auto_freedom, auto_feign_death,
auto_death_grip, auto_combat_potion.
```

---

## - queue_spell,if=!player.casting&!player.channeling

`FerrazGuardianElune.yaml` line 322

```
`&`, not `|`. With `|` the condition is true whenever you are not doing at
least ONE of the two things — and you are almost never casting AND
channelling at once, so it read true on essentially every pass. The queue
is meant to flush only when you are genuinely free.
```

---

## - attack_target,off_gcd=true,delay=100,if=player.combat&target.exists&target.attackable&target.alive&target.in_melee&!player.auto_attacking

`FerrazGuardianElune.yaml` line 337

```
Melee-only, and this file IS melee: keeps auto-attack running.
target.in_melee, not target.range<=8: SIMIA_DOCUMENTATION rule 7 — range is
EDGE distance, so 'max melee' reads 4.5 on a small mob and 2.33 on a
9-reach boss. The shared list used the constant; this does not.
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazGuardianElune.yaml` line 346

```
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## - target_enemy,delay=200,off_gcd=true,if=config.engine_auto_target.has(0)&!target.exists&enemies.combat.8y>=1

`FerrazGuardianElune.yaml` line 358

```
Melee auto target: 8y, matching the shared melee list.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazGuardianElune.yaml` line 363

```
--- Temple of Sethraliss, Adderis and Aspix ---------------------------
Storm Blessed alternates between the two bosses and gives its holder
"Immunity - Damage Only" on every school — a hard immunity, not a
reduction. Damage into it is wasted entirely, so swap off.

1289229 is the AURA. 1310311 is the 2.5s cast that applies it; checking
the cast id would only ever be true for those 2.5 seconds. Same trap as
Symbiotic Relationship, where the cast and the aura are different ids.

target_enemy takes no filter — it is "target nearest enemy" and CYCLES
on repeated presses, like Tab. So the pattern is to describe why the
CURRENT target is wrong and let it re-evaluate next pass; delay=500
keeps that from spinning. This is the same shape the official rotations
use for interrupt scanning.

enemies.combat.40y>=2 stops it hunting once one boss is dead: the
survivor gains Frenzy (1292035), never Storm Blessed, and with nothing
to swap to the line would otherwise cycle for nothing. 40y in every
file, melee included — the count only asks "is there another boss",
not "is it in melee range".

No config toggle: the condition is one boss aura in one dungeon, and
there is no reason to ever want to keep hitting an immune target.
```

---

## set_tank_var:

`FerrazGuardianElune.yaml` line 388

```
Tank-buster prediction feeding the barkskin override. Reads the native
Encounter Timeline (C_EncounterTimeline, 12.0+) instead of hardcoded boss
ability names.
```

---

## defensives:

`FerrazGuardianElune.yaml` line 396

```
Predicted damage first, reactive HP second. Unvalidated by simulation.
```

---

## - lunar_beam,if=target.valid&(!config.lunar_beam_moving_check|player.moving.time<=1)

`FerrazGuardianElune.yaml` line 406

```
Deliberately unsynced from Incarnation/Berserk — forcing sync measured
+0.17% (noise). Moving check: it's a ground effect, running out wastes it.
```

---

## - berserk,if=target.valid&(!config.auto_hotw|!talent.heart_of_the_wild|!cooldown_bypass.heart_of_the_wild.ready)

`FerrazGuardianElune.yaml` line 410

```
Berserk/Incarnation are mutually exclusive talents, both listed so the
file works either way. Held until HotW is spent — delaying burst for the
weave measured +0.95% DungeonSlice (-10.6% Patchwerk, M+-specific).
First two clauses are the escape hatch when there's no weave to wait for.
```

---

## - combat_potion,name="Combat Potion",if=config.use_potion&combat_potion.ready&player.combat&(!config.potion_sync_burst|buff.incarnation_guardian_of_ursoc.up|buff.berserk.up|fight_remains<=30)

`FerrazGuardianElune.yaml` line 417

```
Combat potion. With potion_sync_burst ON it rides the Incarnation/Berserk
buff; OFF, the first clause is always true and it fires on cooldown.
fight_remains<=30 stops a potion being carried unused to the end.
```

---

## - blood_fury

`FerrazGuardianElune.yaml` line 424

```
Racials, unconditional — dead on a Harronir character, kept for race changes.
```

---

## bear:

`FerrazGuardianElune.yaml` line 430

```
Form + rage spending, shared by st/aoe. Called BEFORE them in main, so
anything here outranks the whole damage priority.
```

---

## - ironfur,use_off_gcd=1,name="Ironfur (uptime)",if=buff.ironfur.remains<2&player.combat

`FerrazGuardianElune.yaml` line 435

```
--- Ironfur, off the global cooldown (use_off_gcd=1, neutral for damage
but correct for M+ — not losing a GCD to armour) ---
```

---

## - maul,name="Maul (Gory Fur)",if=buff.1307881.up&!talent.raze.enabled&enemies.combat.8y<3&buff.ironfur.up&!var.heavy_incoming

`FerrazGuardianElune.yaml` line 440

```
Dumping at 40 like SimC's raid APL measured -2.86% DungeonSlice
(+9.41% Patchwerk) — a raid-only gain. Do not "fix" this to match SimC.

--- Rage spenders. Split on talent.raze (parse-time redirect in SimC —
with it, EVERY Maul becomes Raze at any target count), never on enemy
count. Gory Fur (1307881, 3 spells share the name) spent on sight: +2.24%.
```

---

## st:

`FerrazGuardianElune.yaml` line 451

```
===========================================================================
ST — damage priority below the AoE threshold. Also covers the opener.
===========================================================================
```

---

## - 77758,name="Thrash (stacks)",range_check=mob_count_8y,if=cooldown.77758.ready&(dot.thrash.refreshable|dot.thrash.stack<5&talent.flashing_claws.rank=2|dot.thrash.stack<4&talent.flashing_claws.rank=1|dot.thrash.stack<3&!talent.flashing_claws.enabled)

`FerrazGuardianElune.yaml` line 458

```
Must stay a real if=: target_if is a SimC modifier that does NOT exist
in Simia (absent from all stepModifiers). Writing it drops the
condition silently and Thrash spams. Costs nothing to keep as if=
anyway — Thrash(Bear) is PBAoE, no other target to retarget to.
```

---

## - mangle,name="Mangle (burst)",if=(buff.incarnation_guardian_of_ursoc.up|buff.berserk.up)&buff.ursine_potential.stack<6&talent.wildpower_surge.enabled

`FerrazGuardianElune.yaml` line 464

```
Dead while Wildpower Surge is untalented (removing measured -0.04%, nothing).
```

---

## - mangle,name="Mangle",if=(buff.incarnation_guardian_of_ursoc.up|buff.berserk.up)|((rage<88)&!talent.fount_of_strength.enabled)|((rage<83)&!talent.fount_of_strength.enabled&talent.soul_of_the_forest.enabled)|((rage<108)&talent.fount_of_strength.enabled)|((rage<103)&talent.fount_of_strength.enabled&talent.soul_of_the_forest.enabled)

`FerrazGuardianElune.yaml` line 467

```
Free in burst, else gated on rage headroom. Four numbers cover Fount of
Strength/SotF combos; live branch on this build (no Fount, yes SotF) is rage<83.
```

---

## - moonfire,name="Moonfire (GG proc)",if=buff.galactic_guardian.up&target.valid

`FerrazGuardianElune.yaml` line 471

```
Placed after Mangle, not at the top of `bear` — proc lives long enough
to wait a GCD; jumping the queue cost 2.95%.
```

---

## - 213764,name="Swipe (filler)"

`FerrazGuardianElune.yaml` line 476

```
Numeric id: "swipe" also matches the Cat version.
```

---

## aoe:

`FerrazGuardianElune.yaml` line 479

```
Same as `st` with both Thrash lines promoted above Moonfire, no Lunation
slot — Swipe beats single-target Moonfire at several targets.
```

---

## main:

`FerrazGuardianElune.yaml` line 491

```
Entry point: first matching line wins the GCD.
```

---

## - return,if=player.channeling

`FerrazGuardianElune.yaml` line 493

```
Convoke is a channel and nothing here ever wants to break it. Bare
player.channeling, the shape every official rotation in simia_data_dump
uses — see FerrazRestoDruid.yaml, where a narrower id-based guard failed
open often enough to clip Convoke in a real key.
```

---

## - bear_form,range_check=none,if=buff.bear_form.down&!buff.cat_form.up&(target.attackable|enemies.40y)

`FerrazGuardianElune.yaml` line 503

```
!cat_form yields to the weave below so they don't fight each other.
```

---

## - cat_form,name="Cat Form (HotW)",range_check=none,if=var.hotw_weave&buff.cat_form.down

`FerrazGuardianElune.yaml` line 506

```
--- Heart of the Wild weave — biggest block in the file: -15%
DungeonSlice if removed. Cast by name AND cat-form morph id (1261868),
only one resolves per form. ---
```

---

## - bear_form,name="Bear Form (post-HotW)",range_check=none,if=buff.cat_form.up&(!cooldown_bypass.heart_of_the_wild.ready|health.pct<config.hotw_hp_pct|!target.valid|!target.attackable)

`FerrazGuardianElune.yaml` line 512

```
Escape hatches back to Bear if the cast is blocked, HP drops, or target dies mid-weave.
```

---

## - return,if=!player.combat

`FerrazGuardianElune.yaml` line 516

```
--- COMBAT WALL. Nothing below this line runs out of combat. ---
Everything above it is what a tank may do before the pull: the engine,
Mark of the Wild, entering Bear Form, the Heart of the Wild weave (which
carries its own player.combat gate in var.hotw_weave) and the Moonfire
mouseover pull directly above — that one is a DELIBERATE pull, kept above
the wall on purpose and switchable with config.allow_pull_with_mo.

player.combat, NOT player.auto_combat. The catalog defines the second as
a "Config-based auto-combat check", not combat state; using it here is
the bug that silently disabled four rotations in this repo.
```

---

## - call_action_list,name=defensives

`FerrazGuardianElune.yaml` line 530

```
NOTE: there used to be a `return,if=auto_combat.player` here, meant to
hand control to Simia's auto-combat driver. That expression does not
exist (it is player.auto_combat reversed), so it never evaluated true
and the line was dead — which is the only reason the rotation worked.
"Fixing" the spelling made it live, and since player.auto_combat is a
config-based check that reads true in normal use, it aborted main
before defensives and all damage. Removed. Do not add it back.
```

---

## - quaking_palm,if=interrupt.cc.check

`FerrazGuardianElune.yaml` line 545

```
Racial/profession stuns — only one exists per character, rest never resolve.
```

---

## - growl,name="Taunt",if=target.threat<2&target.valid&target.threat!=-1&!player.inraid

`FerrazGuardianElune.yaml` line 552

```
Taunt (dungeon/M+ only). !player.inraid stops it ripping a boss off the other tank.
```

---

## - ironfur,use_off_gcd=1,delay=300,if=buff.ironfur.remains<2|rage>=80

`FerrazGuardianElune.yaml` line 560

```
Second Ironfur trigger outside `bear`, so armour tops up on GCDs the
damage lists own. Overlaps the bear-list lines on purpose.
```

---

## - call_action_list,name=cooldowns

`FerrazGuardianElune.yaml` line 566

```
--- Damage priority ---
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "1.9.1"

`FerrazGuardianElune.yaml` line 1

```
=============================================================================
Guardian Druid Ferraz M+ - spec 104 - patch 12.1.
=============================================================================

Lists (entry point: main):
  engine                  set_tank_var            defensives              cooldowns
  bear                    st                      aoe                     main

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/GuardianElune.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.
=============================================================================
```

## HotW weave: added the forward-looking gates on 2026-08-30 (1.11.0)

Reported symptom: the weave fires at bad moments — the character drops to Cat
Form right as the tank is about to be hit.

Cause: `var.hotw_weave` only asked *"am I healthy right now?"*
(`health.pct>=config.hotw_hp_pct`). Nothing in the gate looked forward. The file
already computed two damage predictors and used neither here:

- `var.heavy_incoming` (`incoming.mitigated.pct>=config.ironfur_dmg_pct`,
  defined for the rage-routing decision)
- `variable.tank_buster_remains` (Encounter Timeline, set in `set_tank_var`,
  consumed only by the Barkskin `spell_override`)

At 100% HP with a swing inbound the old gate passed, so the weave shed Bear
armour and Bear stamina at the worst possible instant.

Three checks added, one config each so any of them can be set to 0 to restore
the previous behaviour:

| Check | Config | Default | Reason |
|---|---|---|---|
| `buff.ironfur.remains>=config.hotw_ironfur_remains` | `hotw_ironfur_remains` | 4 | Was `buff.ironfur.up`, which accepts 0.3s left. The weave costs 3-4 GCDs (Cat Form, HotW, morph, Bear Form), so a nearly-expired Ironfur drops mid-weave. |
| `!var.heavy_incoming` | reuses `ironfur_dmg_pct` | 20 | Predicted damage. |
| `variable.tank_buster_remains>config.hotw_buster_window` | `hotw_buster_window` | 6 | Covers the weave duration plus a GCD of margin. `set_tank_var` is called at the top of `main`, above the weave lines, so the value is fresh on the same pass. |
| `target.time_to_die>=config.hotw_min_ttd` | `hotw_min_ttd` | 10 | HotW lasts 45s. Spending it on a pack about to die throws the cooldown away. |

**Not measured, and not measurable here.** SimC models neither
`incoming.mitigated` nor `encounter.next_tank` — it treats both as permanently
false, so `var.heavy_incoming` and the buster gate are inert in every sim this
repo can run. Only `target.time_to_die` and the Ironfur-remains check have any
sim effect at all, and both can only *reduce* weave count. This is a survival
change that is invisible to the sim and whose DPS cost is bounded by the real
time the gates spend blocking. Judge it in game, not in a profileset.

The `Bear Form (post-HotW)` escape hatch was deliberately left alone. It already
bails on HP, target validity and melee range; adding the buster check there
would be right in principle, but the escape only matters once the weave has
started, and holding the *entry* is the cheaper fix.
