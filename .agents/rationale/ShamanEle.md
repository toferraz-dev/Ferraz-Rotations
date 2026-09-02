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

---

## Compared against the two Elemental rotations in the dump — 1.1.0

The data dump holds exactly two: `rotation_262.yaml` (Simia's own, a mechanical
conversion of an older SimC APL) and `community_TeK_GOAT_Elemental.yaml` (TeK,
hand-written, for **12.0**).

TeK's file is written to run on *any* Elemental build — every branch is guarded
by `talent.X`, including talents this build does not have. This file is written
for one build and drops the dead branches. Neither approach is wrong; they
answer different questions.

Reading it found three things this file had wrong. All are targeting mistakes,
not priority mistakes, and none of them is visible to SimC — the sim has no
concept of where a ground effect lands.

### 1. Earthquake is ground-targeted

```
Earthquake (id=61882) ... Range: 40 yards
Causes the earth within $a1 yards of the target location to tremble
```

Three lines said `earthquake`; they now say `earthquake.cursor`. Without the
suffix the addon has no location to give it. TeK uses `.cursor` on every
Earthquake in the file.

### 2. Capacitor Totem at your own feet

Was `capacitor_totem.player`, copied from the official `rotation_262.yaml`.
That drops the totem on the caster — fine for a melee spec, useless for one
standing at 40 yards, which is where this rotation puts you. Now:

```yaml
- capacitor_totem.cursor,if=interrupt.stun.aoe.check&target.range<=30
- capacitor_totem.mouseover,if=interrupt.stun.mouseover.check&mouseover.combat
```

The official file being a straight APL conversion is exactly why it carries
this: SimC does not model totem placement, so nothing in the conversion could
have caught it.

### 3. Elemental Orbit was talented and unused

```
Elemental Orbit (id=383010): Increases the number of Elemental Shields you
can have active on yourself by 1.
```

It is on this build, and the file only maintained Lightning Shield. Earth
Shield now goes up alongside it, gated on `talent.elemental_orbit` so the line
is dead on a build without it.

Also taken from TeK: `skyfury,cycle=members`, to buff a party member who is
missing it. Out of combat only.

### Deliberately not taken

- **`aoe_mode: active_enemies>=2`.** TeK splits AoE at 2, SimC's own priority at
  3. This file keeps 3 as the default but exposes it as a slider from 2 to 6,
  so the disagreement is the user's to settle rather than baked in.
- **The whole interrupt-timing system** (`interrupt_timing_min/max`,
  `target.casting.elapsed` windows). It is the most interesting thing in TeK's
  file — it delays the kick into a window instead of firing on sight, which
  defeats fake-casting. It is also a large subsystem with its own failure modes
  and no way to validate it here. Worth revisiting on its own, not smuggled in
  with a targeting fix.
- **Thunderstorm as a backup interrupt.** Knocks mobs away from the tank; TeK
  ships it OFF by default and so would this file, which makes it dead weight.
- **`trinket_X.has_stat` / `trinket_X.cd`.** Neither is in
  `expression-catalog.json`, though both appear in the official
  `rotation_260.yaml`, so they are real. They would let the trinket lines tell a
  stat-stick from a proc trinket. The current lines are TTD-only by choice and
  this would be a genuine refinement rather than a fix — left for when the
  trinket policy is revisited with a real character's trinkets in hand.
- **`nameplates.debuff.flame_shock.count`** in place of `active_dot.flame_shock`.
  Both are real; `active_dot` is the SimC-native spelling and is what
  `rotation_262.yaml` uses. No reason to churn it.

---

## Interrupt timing — 1.2.0

### Simia already had one, and it is better than TeK's

Before writing anything, `_common.yaml` was read. `interrupt.target.check` —
which this file already used — expands to, among much else:

```
&target.casting.elapsed>=0.2
&(... target.casting.important
      &target.casting.elapsed*100>=config.interrupt_important_pct*(target.casting.remains+target.casting.elapsed)
    | !target.casting.important
      &target.casting.elapsed*100>=config.interrupt_pct*(target.casting.remains+target.casting.elapsed))
&(!target.incoming_cast.kickable.min50.up|target.casting.elapsed*100>=50*(...))
```

So the shared system already ships:

| Knob | Where | Default |
|---|---|---|
| hard 200ms minimum before any kick | hardcoded in the check | 0.2s |
| `interrupt_pct` — "Interrupt After Cast %" | `_shared.yaml` `config_shared` | 25 |
| `interrupt_important_pct` | same | 50 |
| `interrupt_all`, `interrupt_target/mouseover/focus` | same | false / true |
| per-spell forced ≥50% completion | `incoming_cast.kickable.min50` | — |
| Spell Reflection guard | in the check | — |

Those sliders appear in the Simia UI already; a rotation does not declare them.

**Percentage of cast beats fixed milliseconds.** A 1.5s cast and a 4s cast need
very different absolute delays to mean the same thing, and TeK's system —
`interrupt_timing_min`/`max` in flat ms — treats them alike. It also bypasses
the shared check entirely: TeK's lines gate on `interrupts.target.ready`, not
`interrupt.target.check`, so the reflect guard, the important-cast split and
the min50 rule are all lost. It is a reimplementation of a system that already
existed, with less in it.

### What was actually missing

One thing, and it is real: **nothing in the shared check stops you from
pressing the kick into a cast that is about to finish.** With
`interrupt_pct` at 25, a cast 90% complete still satisfies every clause. Press
it and the kick lands after the cast resolved — spell goes off, kick is on
cooldown, and the next cast in that pack is now unkickable.

So 1.2.0 adds a **latency margin**, plus a minimum delay for anyone who wants
more anti-fake room than the built-in 200ms without touching the percentages:

```yaml
kick_min: config.interrupt_min_delay/1000
kick_margin: config.interrupt_latency_margin/1000
kick_ok_target: !config.interrupt_timing|target.channeling|(target.casting.elapsed>=var.kick_min&target.casting.remains>=var.kick_margin)
```

ANDed onto `interrupt.target.check`, never replacing it:

```yaml
- wind_shear,if=interrupt.target.check&var.kick_ok_target
```

Three properties this shape buys:

- **It can only ever be stricter.** Every guard the shared check performs still
  runs first. A bug here can suppress a kick; it cannot cause a bad one.
- **`!config.interrupt_timing` short-circuits the whole thing**, so the file
  falls back to stock Simia behaviour with one checkbox. That escape exists
  because this is unverifiable outside the game.
- **Channels are exempt from the margin.** `casting.remains` on a channel is
  not a cast bar racing your kick, and gating on it would refuse to kick
  channels near their end for no reason.

Defaults: 150ms minimum (below Simia's own 200ms floor, so it is inert until
raised — deliberately, so the shipped behaviour is unchanged), 250ms margin.

### Untested, and the failure mode to watch for

Not verified in game. If kicks stop happening entirely, the first suspects are
`target.casting.remains` returning 0 or something odd for a spell type this
assumed, or the `/1000` division not producing a fraction. Turn **Extra
Interrupt Timing** off; if kicks resume, it is this layer and not the rotation.

Not taken from TeK, still: the `_late` fallback window. In that file
`safe_interrupt_window_late` re-permits everything past the max as long as
`remains>0.3`, which makes the max slider almost decorative — the pair reduces
to "wait at least min". Two sliders that collapse into one are worse than one.

---

## Reference string swapped — 2026-09-01 (1.2.1)

`recommended_talents` and `sim/Ferraz_shaman_ele.simc` now carry the most-used
Elemental string from the logs sites, replacing the one the file was originally
written against.

**It is a different string that resolves to the same loadout.** They agree on
only 61 of 105 characters and diverge completely in the tail, so this was
checked rather than assumed:

| Check | Result |
|---|---|
| 157 talent names — 57 class, 51 Elemental spec, 52 hero — boolean | no differences |
| the 76 talented nodes at `rank>=2` and `rank>=3` | no differences |
| tree coverage | `class` 57 + `spec elemental` 51 + `hero` 52, complete |

The tree list came from `spell_query=talent.class=shaman` (253 entries; the six
`Tree: selection` nodes are the unnamed hero-subtree picks, already settled by
`call_of_the_ancestors` being true in both).

### The control, because "no differences" is also what a broken probe returns

Corrupting the tail of the string makes SimC reject it outright:

```
Error: Hash '...XXXXXXXX': 58 ranks selected for node 94892, 1 ranks max.
```

and the corrupted build then reports `call_of_the_ancestors`, `stormkeeper` and
`ascendance` all false. So the parser genuinely reads the tail, and the probe
genuinely detects a changed loadout. It found nothing here because there is
nothing to find.

**Every measurement in this file still stands** — same talents, so the
1/3/5-target numbers and the trinket-sync control were measured on this build.

Why the tails differ is unknown. SimC reads both identically, so whatever
differs is something it ignores — PvP talents, loadout metadata, or an
equivalent serialisation from a different exporter. Not worth guessing at.

---

## Mouseover interrupt system — 1.3.0

Modelled on `community_TeK_GOAT_Elemental.yaml`: hover the caster's nameplate,
nothing swaps your target, and the kick has two fallbacks behind it.

```
Wind Shear  ->  Capacitor Totem  ->  Thunderstorm
```

```yaml
- wind_shear,if=interrupt.target.check&var.kick_ok_target
- wind_shear.mouseover,if=interrupt.mouseover.check&var.kick_ok_mouseover
- wind_shear.focus,if=interrupt.focus.check&var.kick_ok_focus

- capacitor_totem.mouseover,name="Cap Totem (Mouseover)",if=config.mo_cap_totem&!var.kick_ready&interrupt.stun.mouseover.check&mouseover.combat&mouseover.range<=40
- capacitor_totem.cursor,name="Cap Totem (AoE)",if=config.cap_totem_aoe&!var.kick_ready&interrupt.stun.aoe.check

- thunderstorm,name="Thunderstorm (Interrupt)",range_check=none,if=config.mo_thunderstorm&!var.kick_ready&interrupt.stun.target.check&target.range<=10
```

`kick_ready: cooldown.wind_shear.ready` gates both fallbacks, so neither spends
a global while the kick itself is available.

### Where this departs from TeK's version, and why

**It keeps Simia's shared checks.** TeK gates on `interrupts.target.ready`;
these lines gate on `interrupt.target.check` and `interrupt.stun.*.check`. The
shared ones carry the Spell Reflection guard, the important-vs-ordinary cast
split, the per-spell forced-50% rule, and the instanced-PvE filtering. Dropping
them to hand-roll the same thing loses all four.

**No duplicate "Mouseover Interrupt" switch.** Simia's `config_shared` already
ships `interrupt_mouseover`, and `interrupt.mouseover.check` is gated on it.
Adding a second checkbox here would let the two disagree, with the rotation
appearing to ignore whichever the user set last. TeK needs his own switch only
because he bypassed the shared check. Three new configs cover what is genuinely
this file's to decide: `mo_cap_totem`, `cap_totem_aoe`, `mo_thunderstorm`.

**Thunderstorm is not a mouseover ability.** TeK files it under the mouseover
system, but the spell is centred on the caster:

```
Thunderstorm (51490): ...dealing Nature damage to all enemies within X yards,
reducing their movement speed, and knocking them away from the Shaman.
```

So `target.range<=10` is the distance to **you**, not to the mouseover, and no
`.mouseover` suffix would change that. It reaches a caster already standing on
top of you and nothing else. It also knocks the whole pack off the tank, which
is why it ships **OFF**, same as TeK's.

It is baseline, not a talent — it does not appear anywhere in
`spell_query=talent.class=shaman`, so the line is live on any build.

### `kick_ready` and the comment in `_common.yaml`

`_common.yaml` says each rotation defines `kick_ready: "action.<its kick>.ready"`
and that the stun aliases are gated on `interrupt.kick.soon`. Only three files
in the whole dump define `kick_ready`, and `interrupt.kick.soon` turns out to be
self-contained — it enumerates every class kick, Wind Shear included, as
`usable.wind_shear&cooldown.wind_shear.remains<0.2`, and `usable.X` returns 0
for a spell the player does not have.

So the shared stun checks already know when this spec's kick is up, without the
rotation telling them. `kick_ready` is defined here for **this file's own**
fallback ordering, not to feed the shared system. Read that comment as legacy
wording rather than a requirement.

### Untested

None of it is verified in game. The stun path is the least certain: whether
`capacitor_totem.mouseover` places the totem at the hovered unit rather than at
the player, and whether `mouseover.range<=40` is the right placement limit, are
both assumptions taken from TeK's file rather than from documentation.

---

## Re-measured on the shipped string — 2026-09-01

Everything above was measured before the reference string was swapped and
before 1.3.0. Re-run on the string the file now ships, same profile, same
`target_error=0.2`, Patchwerk. No `Severe`, no unsupported fight style, no
unknown talent.

| Targets | SimC default | this file | Δ | diff vs threshold | significant? |
|---|---|---|---|---|---|
| 1 | 220,086 ± 436 | 218,545 ± 434 | −0.70% | 1542 vs 1230 | yes |
| 3 | 414,425 ± 792 | 411,485 ± 817 | −0.71% | 2940 vs 2276 | yes |
| 5 | 753,839 ± 1486 | 749,298 ± 1438 | −0.60% | 4541 vs 4136 | yes |

Same APL with SimC's trinket condition swapped in and nothing else changed:

| Targets | this file + trinket sync | Δ | diff vs threshold | significant? |
|---|---|---|---|---|
| 1 | 219,467 ± 412 | −0.28% | 619 vs 1199 | no |
| 3 | 413,259 ± 812 | −0.28% | 1166 vs 2269 | no |
| 5 | 751,532 ± 1483 | −0.31% | 2307 vs 4199 | no |

Cleaner than the first pass: the gap is a flat ~0.3% at every count and
significant at none of them once the trinket condition matches. The earlier run
had 5 targets already inside the error; this one has it outside until the
trinket line is changed, and inside after. Same conclusion, better separated —
the trinket policy is the whole measured difference and the damage priority is
at parity.

### What this run does NOT say

Nothing about 1.3.0. SimC models no interrupts, no mouseover, no totem
placement and no knockback, so the entire mouseover interrupt system — and the
interrupt timing layer from 1.2.0 under it — is invisible to every number
above. The APL mirror carries a bare `wind_shear` line purely so the sim does
not error on its absence.

These numbers confirm two narrower things: the priority still measures at
parity on the string the file now ships, and 1.3.0 changed nothing in the
damage lists. Both worth having. Neither is evidence that the interrupt work
is correct.


---

## Stormkeeper before Ascendance — 2026-09-01 (1.4.0)

From a player report: the rotation casts Stormkeeper **inside** an active
Ascendance. It should never do that — Stormkeeper goes first, Ascendance
follows, and the two are meant to be one window.

Both halves of the pairing were wrong.

### `sk_ready` checked the cooldown when it meant the buff

```yaml
sk_ready: ...&(cooldown.ascendance.remains>10|cooldown.ascendance.remains<gcd)
```

That reads as "Ascendance is not about to come up", and it was standing in for
"I am not in Ascendance". It cannot do that job: while the buff is **up** the
cooldown reads ~180s, which satisfies `>10`, so the line was at its most
permissive exactly when it needed to be closed. Stormkeeper fired mid-window.

```yaml
sk_ready: var.burst_ok&var.cd_ttd_ok&!buff.ascendance.up
```

A cooldown is not a proxy for a buff. `cooldown.X.remains` is large both when
the spell was just used and when the buff from that use is still running, and
those are opposite situations.

### `asc_ready` was separating them, not pairing them

```yaml
asc_ready: ...&cooldown.stormkeeper.remains>15
```

This holds Ascendance until Stormkeeper is far from ready — the exact inverse
of "Stormkeeper first". The old comment claimed the two were "deliberately
offset, never stacked", which was a misreading of SimC's priority carried over
when this file was written.

```yaml
asc_ready: var.burst_ok&var.cd_ttd_ok&(buff.stormkeeper.up|lastcast.stormkeeper<=config.sk_asc_gap)
```

Ascendance can now only follow Stormkeeper: while the buff is up, or within
`sk_asc_gap` seconds of the cast. The player put that window at 8s.

### Why the hold is correct rather than a loss

Stormkeeper is 60s, Ascendance 180s. Ascendance holding for a Stormkeeper
therefore waits at most one Stormkeeper cycle, and the two align on every third
one. Stormkeeper itself is never held — it goes on cooldown as usual, it just
refuses to go out during Ascendance.

`sk_asc_gap` at 0 tightens this to "only while the Stormkeeper buff is still
up"; raising it lets the pair drift.

### Not touched

The player also described syncing the trinket to Ascendance. The trinket lines
here are TTD-only on purpose — see the Guardian rationale, `.sync` was dropped
because the burst it waited on was itself being held. Changing that back is a
policy decision, not part of this fix, and it has already been changed twice.

Unmeasured: SimC's Elemental priority does not model this pairing, and this
spec has no dungeon fight style at all, so the ordering cannot be checked
against a profileset.


## The burst no longer trusts TTD on the pull — 1.5.0

`cd_ttd_ok` is meant to hold Stormkeeper and Ascendance off a pack that dies
too fast. On the **first GCD of a pull it cannot do that job**: no damage has
landed, so there is no history to estimate from, `target.time_to_die` comes out
huge, the gate passes, and the burst goes into a pack that dies in 8 seconds —
the exact case the slider exists to prevent.

```yaml
pull_engaged: player.combat&player.standing.time>=config.burst_min_standing_time&dot.flame_shock.up
```

ANDed into both `sk_ready` and `asc_ready`.

Two independent proofs, and each covers a different failure:

- **Flame Shock ticking** proves damage has landed, so the TTD estimate has
  something to work from. This is the half that fixes the bug above.
- **Standing still** proves the pull is parked rather than still being gathered.
  Bursting while running to the pack wastes the window on travel time.

Lifted from `FerrazBalance.yaml`, which has carried the same guard on
Incarnation since 4.x using its own DoTs (`debuff.moonfire.up|debuff.sunfire.up`).
The Elemental file was written without it, which is what left the TTD sliders
looking unreliable.

### Why Flame Shock is safe to require in both lists

`st` casts Flame Shock directly, and `aoe` reaches it through Voltaic Blaze,
which applies it and sits **above** Ascendance in the list. So the guard costs
at most one global at the start of a pull, and never blocks the burst
indefinitely. Had `aoe` had no path to Flame Shock, this would have silently
disabled the AoE burst entirely — worth checking before adding a DoT
requirement to any gate.

`burst_min_standing_time` defaults to 2s and can be set to 0, which leaves the
Flame Shock half alone.

Unmeasured. SimC dummies live the whole fight, so every TTD gate is inert
there, and this spec has no dungeon fight style to model a pull sequence with.
