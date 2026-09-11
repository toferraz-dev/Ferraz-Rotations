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
