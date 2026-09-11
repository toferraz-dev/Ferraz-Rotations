# Assassination Rogue Ferraz Raid — why each line is the way it is

Created 2026-09-10 from a talent string supplied by the user, SimulationCraft
1210-01 c1935b9, and one Warcraft Logs export:
`WarcraftLogs/Rogue/Assassination/Nekzali the Soulcoiler/Lassitude_f5_log_6rxcJzf2kvbRDYtg.json`
— 416s, 224 759 DPS, 16 730 events.

## The build

Hero tree is **Fatebound**, confirmed by decoding the string through SimC's
HTML Talent Tables (73 talents). The load-bearing ones:

| group | talents |
| --- | --- |
| windows | Deathmark, Kingsbane, Thistle Tea, Vanish + Improved Garrote + Shrouded Suffocation |
| poisons | **Dragon-Tempered Blades**, Deadly Poison, Amplifying Poison, Atrophic Poison, Master Poisoner, Virulent Poisons, Lethal Dose, Rapid Injection, Zoldyck Recipe |
| bleeds | Venomous Wounds, Deep Cuts, Caustic Spatter, Crimson Tempest, Poison Bomb |
| combo points | Deeper Stratagem, Sanguine Stratagem, Seal Fate, Alacrity, Tight Spender |
| Fatebound | Hand of Fate, Deal Fate, Edge Case, Tempted Fate, Fate Intertwined, Delivered Doom, Lucky Coin, Overflowing Purse, Mean Streak, Regicide's Reward |

**Not** in the build, and this decides several lines below: no Darkest Night,
no Blindside, no Improved Ambush, no Exsanguinate, no Indiscriminate Carnage.

## What the log actually shows

Damage, 416s:

| source | share | note |
| --- | ---: | --- |
| Envenom | 16.31% | the single biggest button |
| Rupture | 15.06% | all ticks |
| Garrote | 13.84% | all ticks |
| Melee | 13.72% | free |
| Kingsbane | 6.00% | 6 casts |
| Fatebound Coin (Tails) | 4.99% | **a proc, not a button** |
| Deadly Poison | 4.35% + 2.24% | instant + DoT |
| Amplifying Poison | 3.99% | second lethal poison |
| Caustic Spatter | 3.81% | |
| Crimson Tempest | 1.89% | 30 casts — this fight has adds |
| Mutilate | 1.70% + 0.81% | MH + OH |
| Deathmark | 0.76% | it is a multiplier, not a nuke |

Uptimes:

| aura | uptime |
| --- | ---: |
| Slice and Dice | **98.5%** |
| Garrote | 98.0% |
| Deadly Poison | 97.6% |
| Amplifying Poison | 97.4% |
| Rupture | 96.8% |
| Envenom | 90.9% |
| Kingsbane | 20.2% |
| Deathmark | 11.5% |
| Improved Garrote | 5.8% |

Three things fall straight out of this and shaped the file.

**Slice and Dice is at 98.5% with zero casts of it in the log.** Envenom
refreshes it on this build. So there is no Slice and Dice maintenance line
anywhere in the rotation — only a single opener line gated on
`buff.slice_and_dice.down`, which can realistically only fire at the pull.
A maintenance line would spend combo points on a buff that is already free.

**Fatebound Coin is a proc.** It shows up in the log's *cast* list 62 times,
which is how Warcraft Logs records it, and it is 5% of damage. It is not a
button and there is nothing to press. Spell id 452538, adjacent to Hand of
Fate's 452536 — matched by pulling the id→name map out of a SimC JSON run
rather than guessing from the number.

**Both bleeds together are 28.9% of damage and every point of it is ticks.**
That is why `core_dot` outranks everything except the Deathmark window itself,
and why `ttd_dots` exists at all: a Garrote refresh onto something that dies in
four seconds is a global spent on nothing.

## The priority

Taken from SimC's maintained Assassination list, read out of the report rather
than from memory, then adapted.

**Deathmark is the anchor.** It wants Garrote and Rupture already ticking,
Envenom already up, and Kingsbane within 2s of ready — the two are cast as a
pair, not opportunistically. Trinkets, racials, Shiv and the potion all key off
`var.burst_now` (`debuff.deathmark.up|dot.kingsbane.ticking`) so the whole kit
lands in one window.

The trinkets carry **no off-window escape** beyond `fight_remains<=20`. Both
Deathmark and Kingsbane are roughly two minutes, which is also a typical
trinket cooldown, so once locked they stay locked and an escape leg would only
let them drift out of phase. The end-of-fight leg stays because holding a
trinket into a kill wastes it outright.

**Kingsbane's `cooldown.deathmark.remains>52`** is SimC's number, kept as-is.
It is what remains of Deathmark's cooldown after Kingsbane's own has run, so
firing Kingsbane outside the window is only allowed when doing so cannot break
the next pairing.

**Vanish is a damage cooldown here, not an escape.** With Improved Garrote it
re-applies Garrote at a buffed multiplier. Default on, with a config to turn it
off for fights where Vanish is a mechanic answer.

## Lines that are deliberately inert on this build

Kept rather than deleted, each behind its own talent guard, so the file
survives a talent change instead of silently missing a button:

- `shiv` on `talent.darkest_night` — SimC's own Shiv line. Never fires on this
  build; a second, non-SimC Shiv line covers the real case, see below.
- `fan_of_knives` on `buff.darkest_night.up` — same reason.
- `ambush` on Blindside — not talented; SimC's own run casts Ambush 0.0 times.
- the terminal `fan_of_knives` fallback — only reachable without a dagger pair.

## Two judgement calls worth revisiting

**`finisher_cp` defaults to 5, not 7.** Deeper Stratagem plus Sanguine
Stratagem raise the cap to 7, so spending at 5 looks like waste. It is not what
the maintained list does: SimC calls its spend list at `combo_points>=5` while
simulating this exact talent pair, because holding for 6 or 7 costs more energy
throughput than the larger finisher returns. Exposed as a slider (4–7) rather
than hardcoded, because it is the one number in this file most likely to be
wrong for a build variation.

**`aoe_threshold` defaults to 2.** Assassination switches to Fan of Knives
early on a dagger build. The reference log casts Fan of Knives 23 times and
Crimson Tempest 30 times on what is nominally a single-target boss, so
Nek'zali has adds and the AoE half of this file matters more than a raid
rotation usually implies.

## Second log: Whostolerice, and what it changed

`Whostolerice_f18_log_XJD34VNTWfqZpLgx.json` — 593s, **352 231 DPS**, filed in
the Nek'zali folder but actually an **Ula'tek** pull (Blightscale Rawling,
Venomous Heart, Weakened Doomscale, Gore Rattle). The folder name is wrong.

Most of the gap to Lassitude's 224 759 is the fight, not the player: Fan of
Knives goes from 3.3 to 9.0 casts per minute and Caustic Spatter from 3.81% to
**11.02%** of damage. But two things in it are genuinely worth copying.

### Multi-dotting, which is most of the difference

Garrote and Rupture are applied or refreshed on **nine distinct enemies**.
Boss uptime drops to 63.8% Garrote and 66.8% Rupture — that is not sloppiness,
it is the correct trade: spreading beats maintaining when the adds are worth
more than the tail of a single bleed.

Simia **cannot cycle enemy targets**. `SIMIA_DOCUMENTATION.md` line 787 says so
outright and points at `target_enemy` instead, which means swapping your actual
target mid-fight — not acceptable in a raid. The workable answer is
`.mouseover`, the same mechanism the Resto files use for emergency healing:
hovering an add IS the target picker.

So `multidot` carries `garrote.mouseover` and `rupture.mouseover`, called
**after** `core_dot` so the target actually being hit keeps its bleeds first
and only then does a hovered add get one. Guarded by `var.mo_enemy_valid`, so
hovering a friendly unit, a corpse, or nothing at all cannot divert the list.
The lines do nothing until the player hovers something, which is the honest
behaviour — there is no way to automate this.

### Shiv, which SimC does not cast on this build

SimC gates Shiv on `talent.toxic_stiletto&talent.darkest_night`. This build has
Toxic Stiletto but not Darkest Night, so that line is dead — and Lassitude
casts Shiv exactly once in 416s, agreeing with it.

Whostolerice casts it **14 times in 593s** with no Darkest Night buff anywhere
in his log. That is roughly one per 40s against a 25s recharge on two charges,
so it is opportunistic rather than a priority.

Added as `Shiv (Burst Window)`, gated on `var.burst_now&energy.pct>40` and
behind a config toggle. Window-gated rather than on cooldown, because at one
cast per 40s it clearly is not being pressed on cooldown, and putting it above
Mutilate on cooldown would displace a builder every recharge.

### Also noted, not acted on

Whostolerice's build is **not** the one this file targets — he has Scent of
Blood, which is absent from the supplied string. His Envenom uptime is 68.8%
against Lassitude's 90.9%, which is what heavy AoE does to a single-target
buff, not a mistake. Slice and Dice is 98.8% for him too, with no Slice and
Dice casts, which independently confirms the Envenom-refreshes-it reading.

## Not measured

SimC runs its own action list, not this YAML, so nothing here has been A/B
tested. The damage shares, uptimes and cast counts above are measured from the
log; the priority is SimC's maintained list adapted to this build; the config
defaults are reasoning. `sim/Lassitude_rogue_assa.simc` holds the gear read
out of the log's `combatantinfo` event if a baseline is ever wanted — it sims
187 497 DPS on Patchwerk, which is not comparable to the log's 224 759 because
the log fight has adds.

## 2026-09-10 — the rotation froze at 5 combo points (v1.0.0 → 2.0.0)

Reported from play: at 5 combo points with plenty of energy the rotation
would stall for a second or two and not spend Envenom.

Real bug, and mine. `spend` was copied from SimC verbatim and **every Envenom
in it is conditional**:

```yaml
- envenom,if=buff.envenom.remains<=1|debuff.deathmark.up
- envenom,if=energy.pct>70|fight_remains<15
- envenom,if=energy.pct>30&(target.time_to_die<12|spell_targets.fan_of_knives>=4)
```

Meanwhile `main` gates the generator off above the threshold:

```yaml
- call_action_list,name=generate,if=combo_points<config.finisher_cp
- call_action_list,name=spend,if=combo_points>=config.finisher_cp
```

So on a boss at 5 combo points, with the Envenom buff still above 1s,
Deathmark down, energy between 30% and 70% and fewer than 4 targets, **every
line in the file evaluates false**. Garrote and Rupture were fresh, generate
was gated off, and all three Envenoms failed. Nothing to suggest.

In SimC that state is deliberate pooling and the actor simply waits. In a live
assistant it reads as a freeze, and at low energy it is genuinely bad — from
25% energy the wait is around six seconds of doing nothing at all.

### Fix, in three parts

**The wait is no longer idle.** A second `generate` call runs when the spend
list declined to act and the bar is not capped:

```yaml
- call_action_list,name=generate,if=combo_points>=config.finisher_cp&combo_points<combo_points.max
```

This is the right use of that time rather than a workaround: the build has
Deeper Stratagem and Sanguine Stratagem, so the cap is 7, and combo points 6
and 7 are free damage on the Envenom that follows.

**A terminal Envenom at the cap.** At `combo_points>=combo_points.max` there is
nothing left to build, so pooling is pure standing still, and a Seal Fate proc
onto a capped bar is thrown away. This is what guarantees the list can never
dead-end again.

**The pool threshold is a slider now**, `envenom_pool_pct`, default 70 to match
SimC. Dropping it to 40–50 spends on sight; the comment in the config says so,
because the correct value here depends on how the pause feels in play rather
than on anything the sim can settle.

### Worth remembering

`finisher_cp` and the generate gate are the same number, so any list reachable
only between that number and the combo point cap is dead air unless something
explicitly fills it. Adding a conditional-only finisher list above a gated
generator is a dead-end pattern, not a pooling pattern.

## 2026-09-10 — three more from play (v2.0.1 → 3.0.0)

**Auto Stealth was missing entirely.** Added out of combat only, in the stock
Simia shape: `stealth_mode` dropdown with Enemy Around / Always / Never,
default Enemy Around, which uses `range_check=mob_count_40y` so you do not
re-stealth while standing around between pulls. Placed after the poison lines
— a poison application breaks nothing, but stealthing first and then applying
a poison would waste the Stealth. Guarded on `!buff.vanish.up` so it cannot
step on a Vanish window.

**Garrote and Rupture were slow to refresh.** `var.dots_ttd_ok` was defined in
`variables:` and then never used — the two bleed lines carried the raw form
instead:

```yaml
target.time_to_die-dot.garrote.remains>config.ttd_dots
```

That has no `target.boss|` bypass, unlike every other TTD gate in the file. So
any moment Simia's time-to-die estimate dipped — a shield, an immunity, a
phase transition, all of which Ula'tek has — the refresh was blocked outright
and the bleed was allowed to fall off a boss. Now both lines use
`var.dots_ttd_ok`, so a boss can never gate its own bleeds.

**The trinket fired with a lone Kingsbane.** `items` was keyed on
`var.burst_now`, which is `debuff.deathmark.up|dot.kingsbane.ticking`.
Kingsbane comes back roughly twice per Deathmark, so the trinket rode a
Kingsbane with no Deathmark behind it and was then on cooldown when the real
window opened. Observed with the 90s Ula'tek trinket.

Trinkets and the potion now key on **Deathmark specifically**. The trinkets
also get SimC's `cooldown.deathmark.remains>20` escape back, which was removed
on 2026-09-10 when the ask was "trinkets in the burst window" — that tightening
was right for a 120s trinket and wrong for a 90s one, because 90 against 120
cannot pair every cycle and the alternative to spending is idling it. The
potion keeps no such escape: at 5 minutes it is the rarest cooldown in the kit
and should only ever ride Deathmark.

`var.burst_now` still drives Shiv and the racials, which are cheap enough that
a lone Kingsbane is a fine home for them.

---

## Three bugs found against the Maxroll Fatebound guide, and two false alarms (2026-09-11)

Ferraz reported two symptoms in play: Garrote slow to reapply, and the trinket
firing the instant it comes off cooldown instead of syncing to Deathmark.
Cross-checked the file against maxroll.gg's Assassination Rogue guide
(Fatebound single-target and multi-target sections) and SimC's own bundled
`profiles/MID2/MID2_Rogue_Assassination_Fatebound.simc`.

### Garrote (Improved Window) was cutting its own snapshot short

`buff.improved_garrote` (spell id 392401) is a **player** buff, 6 seconds,
active after breaking Stealth/Vanish - not a flag carried by the DoT. A
Garrote cast inside that window snapshots +50% damage for the DoT's entire
duration, which the guide calls out explicitly: with Shadow Dance gone from
Assassination, Garrote-via-Improved-Garrote is the *only* bleed left that can
still snapshot. Its own rule: "If your current Garrote is buffed with Improved
Garrote, do not overwrite it and instead apply Garrote as soon as the buffed
one expires."

The line here did the opposite - `dot.garrote.remains<=14+6*talent.razor_wire
+4*!var.single_target` cut a freshly-snapshotted DoT short on almost every
Vanish, since that threshold sits close to the DoT's own base duration. The
recast is equally snapshotted, so nothing is lost in damage - the cost is a
GCD spent refreshing a bleed that had 10+ good seconds left, instead of on
Mutilate/Envenom/whatever else was next in line. Fixed: the line now only
fires on `buff.improved_garrote.up&dot.garrote.refreshable` - spend the window
on a refresh only when one was coming anyway.

### Garrote's plain refresh line was gated on the wrong resource

`combo_points.deficit>=1` sat on the non-Improved-Window Garrote line. Garrote
is a combo point *generator* - it needs no combo points to cast, and gating
its DoT-refresh on "not already capped" meant the refresh was skipped
whenever the player sat at the CP cap, which is most of the time energy is
being pooled for Envenom (`envenom_pool_pct`, 70% by default - a real wait).
Garrote is 13.84% of the reference log's damage, all ticks. Losing one
overcapped combo point costs nothing; losing the whole bleed for however long
CP sits capped is the "slow to reapply" Ferraz reported. Gate removed - the
line is now just `dot.garrote.refreshable&var.dots_ttd_ok`.

### Trinket sync: two bugs in one condition

Old line: `if=...&(debuff.deathmark.up|cooldown.deathmark.remains>20|
fight_remains<=20)`, same on both trinket slots.

1. **The opener was structurally impossible.** `cooldown.SPELL.remains` reads
   the literal "seconds until cooldown expires" - 0 for a spell that is simply
   ready but has never been cast. Early in a pull, Deathmark sits at
   `remains=0` because it hasn't been cast yet (blocked on its own
   `var.dots_ready`, not on cooldown), and `0>20` is false, and
   `debuff.deathmark.up` is false too. Every reference opener - both
   single-target and multi-target, confirmed against maxroll - has a trinket
   use several GCDs before the first Deathmark. The old condition could never
   satisfy that.
2. **The 20s window is "close" for about a sixth of a 120s Deathmark cycle.**
   The other five-sixths, the escape just waves the trinket through
   immediately - which is exactly "fires the instant it's off cooldown."

Root cause of both: the file tried to make ONE symmetric condition do the job
of syncing, when SimC's own default APL for this build does something
smarter - `profiles/MID2/MID2_Rogue_Assassination_Fatebound.simc:95-96` picks
whichever on-use trinket has the LONGER base cooldown (`trinket.
1.cooldown.duration>=trinket.2.cooldown.duration` in precombat) and makes
*only that one* wait strictly for `debuff.deathmark.up`. The other trinket
fires on cooldown, unheld - its shorter cooldown resyncs with Deathmark on its
own, so holding it too just doubles the wasted-window risk for no reason.

Simia has no `trinket_1.cooldown.duration` equivalent in the expression
catalog - only `.cd` (seconds *remaining*), which cannot tell two on-use
trinkets' base cooldowns apart the way SimC does. It CAN read
`trinket_X.has_onuse` - whether a slot holds a button at all versus a passive
stat stick or proc - and that alone resolves the common case: Ferraz's own
gear has exactly one on-use trinket (Ula'tek), so `config.trinket_sync_slot`
defaults to Auto (0) and `var.trinket_1_syncs` / `var.trinket_2_syncs` pick
it out with no config needed:
`config.trinket_sync_slot=1|(config.trinket_sync_slot=0&trinket_1.has_onuse&!trinket_2.has_onuse)`.
Manual 1/2 selection is still there for the day a second on-use trinket shows
up and Auto can't tell them apart; "Neither" fires both on cooldown, same as
before this pass entirely.

**Not measurable in SimC**, same reason as the Guardian gates: this is a
config choice about which physical trinket the player equips, not something a
profileset resolves. Confirm in game by checking which of the two trinkets in
the log actually shows up paired with `debuff.deathmark.up` every time.

### Two things checked and found NOT broken

**Crimson Tempest in `generate`.** Looked wrong on sight - Crimson Tempest is
a combo point *finisher* in most people's memory of the spec. It is not, in
this talent kit: `spell_query=spell.name=crimson_tempest` shows `Resource: 60
Energy`, `Energize Power: +1 combo point`, and "Copy the longest Garrote and
Rupture on the enemies you hit onto up to 2 other enemies." It is a generator
that also multi-dots bleeds as a side effect, on-list, in the right place.

**Caustic Spatter has no action line, and needs none.** `spell_query` shows it
is a passive: "Envenom or Kingsbane apply Caustic Spatter for 10s. Limit 1." -
automatically refreshed by casting Envenom, which the rotation already does
on a tight cadence. The guide's "keep track of it, refresh before it runs
out" is really just "don't let your Envenom cadence lapse for 10+ seconds,"
already covered by the existing pooling logic. Nothing to add.

### Left open: Rupture's flexible pandemic table

The guide gives an exact table for Rupture refresh timing, scaled by the
combo points of the *new* cast rather than a flat 30%: 1 CP -> 2.4s, 2 -> 3.6s,
up through 7 CP -> 9.6s (linear, 1.2s per CP). `dot.rupture.refreshable` here
uses Simia's generic 30%-of-current-duration pandemic check instead, which is
based on whatever CP the *currently ticking* Rupture was cast with, not the
CP available for the next cast. These may already coincide in practice since
Rupture is gated at `combo_points>=config.finisher_cp` (5) either way, giving
7.2s under the guide's own table - close to a 30% pandemic window on typical
Rupture durations. Not verified precisely, and not changed this pass -
flagged for whoever looks at Rupture refresh timing next.

### Deathmark/Kingsbane could open on a bleed about to fall off

Maxroll, verbatim: "Always refresh your bleeds before using Deathmark if they
have 18 seconds or less at the moment that you press it." `var.dots_ready`
only checked `.ticking` - true the instant a bleed exists, with no floor on
how much of it is left. Since `cds` is called before `core_dot` in `main`,
Deathmark or Kingsbane could win the GCD on a Garrote or Rupture with, say, 3
seconds left, opening a 120s-cooldown window on ticks that stop almost
immediately - exactly the case both abilities exist to amplify.

Added `config.deathmark_bleed_fresh` (slider, default 18, matches the guide's
number exactly) to `var.dots_ready`:
`dot.garrote.remains>config.deathmark_bleed_fresh&dot.rupture.remains>
config.deathmark_bleed_fresh`. When a bleed is stale at the moment Deathmark
would otherwise fire, `dots_ready` now reads false, `cds` falls through with
nothing to say, and `core_dot` picks up the refresh on the same or a
following GCD - Simia's own pandemic window (`dot.garrote.refreshable`, ~30%
of duration) is narrower than 18s on a typical Garrote/Rupture duration, so
the refresh happens a beat later on its own schedule, remains jumps back up,
and `dots_ready` passes on the very next pass. No deadlock: a Deathmark that
comes off cooldown while bleeds are already fresh still fires immediately,
same as before - the gate only holds the moment bleeds are genuinely about
to expire.

Not measurable in SimC for the same reason as every other TTD-shaped gate
here: `dots_ready` is a real quantity there, but nothing in the harness
reproduces "Deathmark came off cooldown mid-bleed" often enough to compare
variants on it. Judge in game - the tell is the Deathmark cast landing right
after a Garrote/Rupture refresh instead of on a stale one.
