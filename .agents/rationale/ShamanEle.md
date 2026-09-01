# FerrazShamanEle.yaml — rationale

Everything the YAML does not say. Written 2026-08-31 against
`simc 1210.01.5f3ee6d` (WoW 12.1.0.69497, hotfix 2026-08-29).

---

## The build

The talent string the file ships was decoded by **execution probe**, not by
reading the string and not by trusting any JSON echo. Method: one sim per
talent, APL of exactly `actions=lightning_bolt,if=talent.X`, three outcomes.

| Outcome | Means |
|---|---|
| DPS > 0 | talented |
| ran, DPS absent | the talent exists on the 12.1 tree, not taken |
| `Talent 'X' not found` on **stderr** | not a talent in 12.1 at all |

That third case only appears if you read stderr. SimC prints the initialization
error there and still writes a normal-looking report to stdout, so a probe that
only reads stdout silently reports "not taken" for a talent that no longer
exists. Two earlier passes of this probe got the wrong answer that way.

**Talented (26):** ancestral_swiftness, ascendance, astral_shift,
call_of_the_ancestors, capacitor_totem, crackling_fury, earth_elemental,
earthquake, echo_chamber, echo_of_the_elements, elemental_blast, elemental_fury,
elemental_orbit, first_ascendant, flametongue_weapon, inferno_arc, molten_wrath,
mountains_will_fall, natures_swiftness, poison_cleansing_totem, purging_flames,
spirit_wolf, spiritwalkers_grace, stormkeeper, totemic_surge, voltaic_blaze.

**Hero tree is Farseer** — `call_of_the_ancestors` yes, `tempest` no,
`surging_totem` no.

**On the tree, not taken (15):** earth_shock, earthgrab_totem, eye_of_the_storm,
fusion_of_elements, greater_purge, healing_stream_totem, lightning_rod,
master_of_the_elements, power_of_the_maelstrom, supportive_imbuements,
surging_totem, tempest, thunderstrike_ward, tremor_totem, wind_rush_totem.

**Gone from 12.1 entirely (13):** ancestral_guidance, deeply_rooted_elements,
fire_elemental, flow_of_power, icefury, lava_surge, liquid_magma_totem,
primordial_wave, static_accumulation, stone_bulwark_totem, storm_elemental,
surge_of_power, unrelenting_calamity.

That last list matters for anyone porting an older APL: `buff.fire_elemental`,
`buff.storm_elemental` and `talent.lava_surge` are all referenced by the
official `simia_data_dump/rotation_262.yaml`, and none of them can be true here.

---

## What the missing talents delete from SimC's priority

SimC's shipped 12.1 Elemental APL is written for a Master of the Elements
build. With MotE untalented, `buff.master_of_the_elements.up` is permanently
false, which flips the meaning of a large part of that list:

- every `if=!buff.master_of_the_elements.up&...` line loses its first clause and
  becomes unconditional on that term — kept here, with the clause dropped
- every `if=buff.master_of_the_elements.up|...` line falls through to the `|`
  side — kept here, with only that side
- every `if=...&talent.master_of_the_elements` line is dead — **absent here**

Same treatment for `talent.tempest` (all Tempest lines, and the Stormkeeper
Lightning Bolt line), `talent.lightning_rod` (the AoE Earthquake gate), and
`earth_shock` (not talented, so **Elemental Blast is the only Maelstrom
spender** — every `earth_shock` line is gone and its Elemental Blast twin kept).

The file carries the live branch of each, not the branch plus a dead guard.
Comparing it line-by-line against SimC's default APL will look like lines are
missing; they are missing on purpose, and the header says which talents did it.

---

## Fight styles: this spec has no dungeon style at all

**Elemental supports neither DungeonSlice nor DungeonRoute.**

```
Severe: Player 'Ferraz_Shaman_Ele' does not support fight style DungeonRoute,
results are inaccurate and should not be used.
```

Verified with a control, because the repo has been burned by exactly this once
before: the same command on `sim/Tassiana_gear.simc` (Balance, which does
support DungeonRoute) prints the warning **zero** times, and SimC's own stock
`MID2_Shaman_Elemental.simc` prints it **once**. It is the spec module, not
this profile and not these talents.

### The trap that nearly hid it

Probing fight-style support with `fight_style=DungeonRoute` and **no route
file** reports no warning at all. The validation only runs once `raid_events`
pull entries exist. A support check without a route is not a support check —
it returns a false pass. Always probe with the route file attached and grep the
output.

Nor does argument order rescue it: putting `fight_style=DungeonRoute` before
the route file on the command line gives the same warning.

So M+ numbers for this spec come from **multi-target Patchwerk**
(`desired_targets=N`), which is supported. That models a static pull of N mobs.
It does not model pull cadence, cooldown budgeting across a route, or travel —
which is exactly what DungeonRoute was bought for on the druid files. Any claim
here that depends on pull-to-pull behaviour is unmeasurable for Elemental and
must be marked as such.

---

## Measurement

`sim/Ferraz_shaman_ele.simc` vs `sim/apl_shaman_ele_mplus.simc`, `target_error=0.2`,
Patchwerk at 1/3/5 targets. Significance is `2*sqrt(e1²+e2²)`.

**The gear in that profile is not the user's** — no character export was
supplied, so it carries SimC's own MID2 Elemental gear verbatim and only the
talent string is theirs. Every number below is a statement about the priority,
not about their character.

| Targets | SimC default | this file | Δ | significant? |
|---|---|---|---|---|
| 1 | 220,056 ± 421 | 218,804 ± 435 | −0.57% | yes, barely (1252 vs 1211) |
| 3 | 414,638 ± 793 | 412,003 ± 793 | −0.64% | yes, barely (2635 vs 2243) |
| 5 | 752,644 ± 1449 | 750,292 ± 1452 | −0.31% | no |

### The gap is the trinket policy, not the priority

The rotation fires trinkets on TTD alone; SimC's default holds them for
Ascendance. Re-running this file's APL with SimC's trinket condition and
nothing else changed:

| Targets | this file + trinket sync | vs default | significant? |
|---|---|---|---|
| 1 | 219,622 ± 421 | −0.20% | no (434 vs 1191) |
| 3 | 412,482 ± 807 | −0.52% | no (2156 vs 2262) |

Both gaps collapse into the noise. The damage priority is at parity with SimC's
default at every count tested; what the first table measured was the trinket
decision.

That decision is deliberate and comes from the Guardian file — see
`GuardianElune.md`, "Trinkets: dropped `.sync` for a plain TTD gate". On
Patchwerk a TTD gate can only lose, because nothing ever dies early and there
is no held burst to miss. In a key the tradeoff runs the other way. Keeping the
sim's preferred condition here would be optimising for the fight style that
this spec cannot even simulate properly.

---

## Choices that are judgement, not measurement

Unmeasured, and marked at their config entries too:

- the whole `defensives` list — SimC has no damage-intake model
- `dispels`, `interrupts` — no model
- `moving_st` / `moving_aoe` — SimC never moves
- `mouseover_dots` — no mouseover model
- every `ttd_*` slider — sim dummies live the whole fight

### `enemies.combat.40y`, not `enemies_around_target`

The official `rotation_262.yaml` translates SimC's
`spell_targets.chain_lightning` as `enemies_around_target`. This file uses
`enemies.combat.40y`, matching `FerrazBalance.yaml`, for two reasons: the combat
filter keeps unpulled mobs out of the count, and it is the same expression every
other ranged file here already uses, so the AoE threshold means the same thing
across the set. `enemies_around_target` has no entry in
`expression-catalog.json` beyond the bare name.

### `buff.1300222` for the tier window

SimC's APL calls it `buff.overcharge_tier`, which is an internal label with no
Simia equivalent. `rotation_262.yaml` resolves it to spell **1300222**
(`sc_shaman.cpp:12831`) and this file uses the same id. Those two lines are dead
until the set bonus is on, and harmless while it is not.

### Ascendance and Stormkeeper are offset, never stacked

`var.sk_ready` requires `cooldown.ascendance.remains>10` or `<gcd`;
`var.asc_ready` requires `cooldown.stormkeeper.remains>15`. This mirrors what
SimC's own priority does with the pair and is the one piece of cooldown
sequencing carried over verbatim.

### Poison Cleansing Totem instead of a targeted dispel

Elemental's only dispel on this build is the totem, which is a ground effect on
its own timer — it cannot be pointed at a person. The line therefore fires on
`player.dispelable.list|cycle.dispelable.list` and lets the totem sort out who
it reaches. `greater_purge` is not talented; plain `purge` is offensive only
(magic buff off an enemy) and ships **OFF**, because most trash buffs are not
worth a global.

The Devouring Rift affix line uses Purge's dispel path with a direct spell-id
check on 440313, the same shape the druid files use — type matching would skip
it.

---

## Untested in game

Everything. This file has never been loaded in Simia. The specific things most
likely to be wrong on first contact:

- `poison_cleansing_totem` as an action name, and whether Simia accepts
  `cycle.dispelable.list` outside a `cycle=` step
- `mainhand.enchant.remains` for the Flametongue refresh
- `capacitor_totem.player` as the AoE stun (copied from the official rotation)
- whether `movement_allowed: buff.spiritwalkers_grace.up` behaves as the moving
  lists assume
