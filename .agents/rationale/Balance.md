# Balance — rationale
Every technical comment that used to live in `FerrazBalance.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "4.0.2"

`FerrazBalance.yaml` line 1

```
=============================================================================
Balance Druid — spec 102 — patch 12.1 (Midnight) — Elune's Chosen, M+.
=============================================================================

── LISTS, in the order `main` calls them ────────────────────────────────────
  main            entry point. Plumbing, target guards, form, then delegates.
  heal_support    Mark of the Wild, Thorn Bloom.
  defensives      Barkskin, Bear Form/HotW/Frenzied Regen, root cleanse.
  interrupts      Solar Beam (target/mouseover/focus).
  dispels         Remove Corruption (self/party), Soothe. All three toggled.
  trinkets        trinkets + combat potion, tied to the burst window.
  moving_st/aoe   instant-only priority while moving.
  ec_st / aoe     stationary damage priority, 1 / 2+ enemies.
  mouseover_dots  called from `aoe`; spreads DoTs without changing target.

── PRIORITY ─────────────────────────────────────────────────────────────────
  ST   DoT uptime -> Eclipse -> Incarnation -> Fury of Elune -> free procs
       -> Starsurge (Eclipse-aware AP floor) -> Starfire.
  AoE  anti-cap Starfall -> DoTs (target, then mouseover) -> Eclipse ->
       Incarnation -> Fury of Elune -> free procs -> Starfall -> Starsurge
       weaving -> Starfire.

── HOW THE NUMBERS WERE MADE ────────────────────────────────────────────────
READ THIS BEFORE TRUSTING ANY PERCENTAGE BELOW.

Every inline number in this file was measured with fight_style=DungeonSlice,
and SimC does not support that style for Balance Druid. It says so on every
run:

  Severe: Player does not support fight style DungeonSlice, results are
  inaccurate and should not be used.

Verified 2026-08-27: the warning appears with SimC's own stock APL and on the
previous binary too, so it is the spec module talking, not this repo's APL,
and it was never new — nothing had grepped for it. Balance supports Patchwerk
and DungeonRoute only.

So the DungeonSlice percentages quoted throughout are SUSPECT, not void. They
were consistent with each other and several were confirmed against Patchwerk,
but none of them has been re-measured on a supported style. Treat every one as
provisional until it is.

Current M+ setup (supported): fight_style=DungeonRoute with the pull events in
sim/dungeon_route.simc, gear sim/Tassiana_gear.simc (addon export 2026-08-27,
client 69497), APL mirror sim/apl_mplus_current.simc, target_error=0.15.
Route DPS is route-wide and includes travel delay, so it reads well below
Patchwerk on the same gear (100.6k vs 144.1k) — compare deltas, never levels.

Older harness: sim/ab_test_balance.py, table sim/BALANCE_AB_RESULTS.md, gear
sim/Ferraz_balance.simc (export 2026-08-21: 12.52% crit / 32.64% haste). Both
still default to DungeonSlice and carry the caveat above.

Baseline note for anyone re-running the harness: DEFAULTS there carries
wrath_filler=True, but this file ships it OFF — so the variant that matches
this file is `no_wrath`, NOT `ferraz`.

── WHAT THE SIM CANNOT SEE ──────────────────────────────────────────────────
Everything below is judgement, not measurement, and is marked at its own
config entry too:
  defensives, Heart of the Wild, Thorn Bloom, both HP sliders
  both moving_* lists            SimC never moves
  the dispels list               no dispel model
  inc_min_standing_time          player.standing.time is infinite in the sim
  swap_off_dying                 no retargeting model
  every ttd_* slider             sim dummies live the whole fight

── COUNTING ENEMIES ─────────────────────────────────────────────────────────
This file uses enemies.combat.40y everywhere and active_enemies NOWHERE.
The catalog defines active_enemies as a NAMEPLATE count, which includes mobs
that are merely on screen — idle dummies, a pack the tank has not reached.
That silently disabled the Moonfire lines near training dummies and fired
Incarnation into an ungathered pull. enemies.combat.40y counts only enemies
actually in combat and inside cast range.

── THE TALENT STRING ────────────────────────────────────────────────────────
4.0.0 replaced the reference string with the one from Jeannelin's +18 (The
Blinding Vale, 26.4 min, 1216 casts). Verified node by node against the old
string with a SimC execution probe, not an HTML scrape: five nodes moved.
  gained: Fluid Form, Orbit Breaker, Elune's Guidance
  lost:   Stellar Amplification, Sundered Firmament
Everything else matched, hero tree included (Elune's Chosen).

Carried: Lunar Calling, Lunation, Boundless Moonlight, Atmospheric Exposure,
The Eternal Moon, Incarnation: Chosen of Elune, Whirling Stars, Fury of Elune,
Touch the Cosmos, Umbral Embrace, Rattle the Stars, Meteorites, Aetherial
Kindling, Radiant Moonlight, Fluid Form, Orbit Breaker, Elune's Guidance.

NOT carried, so those lines are harmless dead weight (flagged inline):
Starweaver, Force of Nature, Convoke the Spirits, New/Half/Full Moon,
Wild Mushroom, Power of Goldrinn.

WHAT THIS INVALIDATES. Every measured constant below was tuned against the
OLD string and has NOT been re-measured on this one. Elune's Guidance shortens
the Incarnation cooldown enough that Jeannelin got one every ~113s against a
3-minute base, so var.inc_ready_to_cast now fires far more often than when the
AP floors were fitted. Treat these as provisional until the A/B is re-run:
  - the astral_power>=50 / deficit<20 floors in ec_st
  - the Starfall 40/80 floors in aoe
  - the 2-enemy AoE threshold
No rotation line reads Stellar Amplification or Sundered Firmament, so
dropping them changes nothing structurally. Fluid Form does flip live
behaviour: the "Back to Moonkin (Fluid Form)" line now wins over the explicit
moonkin_form shift, which is a free global instead of a spent one.
=============================================================================
```

---

## about:

`FerrazBalance.yaml` line 116

```
==========================================================================
BUILD STAMP — display only. Keep in sync with version:/patch: above.
==========================================================================
```

---

## recommended_talents:

`FerrazBalance.yaml` line 125

```
==========================================================================
RECOMMENDED BUILD — every number in this file was measured against this
  exact string. Changing it invalidates the AP floors and the Incarnation
  alignment before anything else.
==========================================================================
```

---

## inc_min_standing_time:

`FerrazBalance.yaml` line 136

```
==========================================================================
COOLDOWNS — when Incarnation and the burst window are allowed.
==========================================================================
Log-driven: 6 of 15 Incarnations in a real +11 run went out with ZERO
enemies being damaged — the tank was still gathering the pull. Versions
2.1-2.3 gated that on an engaged-enemy count plus a combat-time delay,
both short-circuited for bosses. 2.4 replaces all of it with a single
standing-still timer: while you are repositioning behind the tank you are
by definition moving, and once the pull is actually parked you stop. It
reads the real state directly instead of proxying it through enemy counts,
and it needs no boss exception — you stand still on a boss too.

SimC cannot measure this at all: it never moves, so player.standing.time
is effectively infinite there and the gate is always open. In-game only.
```

---

## use_trinket_1:

`FerrazBalance.yaml` line 173

```
==========================================================================
TRINKETS & CONSUMABLES — all three ride the burst window.
==========================================================================
Default ON: off measured -7.4% DungeonSlice, the largest number here.
```

---

## ttd_incarnation:

`FerrazBalance.yaml` line 195

```
==========================================================================
TIME TO DIE — stop a long cooldown being spent on trash that is
  about to die. target.boss short-circuits every one of them.
  UNVALIDATED: SimC dummies live the whole fight.
==========================================================================
```

---

## wrath_filler:

`FerrazBalance.yaml` line 245

```
==========================================================================
SINGLE TARGET — gear-dependent knob, re-test after a big gear change.
==========================================================================
Re-confirmed 2026-08-27 on DungeonRoute with the 4.0.0 talent string and the
2026-08-27 gear: Wrath filler ON measured -1.02% against this file's OFF
baseline, comfortably outside the noise bar. OFF stays right on the new
build, so the conclusion below survives even though the style it was
originally measured on does not.

Gear-dependent, measured at three points on DungeonSlice — the value of
keeping Wrath tracks crit almost linearly:
    12.5% crit / 32.6% haste  ->  -2.26% to keep it   (CURRENT gear)
    15.4% crit / 31.2% haste  ->  -5.28% to keep it
    18.8% crit / 29.4% haste  ->  -4.04% to keep it
    22.5% crit / 21.6% haste  ->  +1.44% to keep it
Break-even sits near ~22% crit and the current gear is well under it, so
OFF is right by a clear margin. Re-test only if a gear change adds a large
chunk of crit at once.
```

---

## enable_mouseover_dots:

`FerrazBalance.yaml` line 270

```
==========================================================================
AOE — DoT spreading and target swapping.
==========================================================================
Largest AoE gain in the file: +2.1% DungeonSlice, +9.8% at 5 targets.
```

---

## swap_off_dying:

`FerrazBalance.yaml` line 281

```
Swap off a target that will die before a hardcast Starfire lands, instead
of feeding the cast to a corpse. Simia has NO "pick the enemy with the most
HP": the only targeting action is target_enemy, and the catalog defines it
as "Target nearest enemy", full stop. So this hops to whatever is closest
and relies on the condition clearing itself once the new target outlives
the cast.

TRAP RISK — read before enabling. If the nearest enemy IS the dying target,
the swap is a no-op, the condition stays true, and the line wins the GCD
every pass forever. That is the same failure mode as the Prowl line in
FerrazFeral.yaml, which is why this ships OFF and carries three guards:
2+ enemies engaged in range, a 250ms delay so it cannot fire every frame,
and placement in `aoe` only (in `ec_st` there is nothing to swap to).

UNMEASURABLE: SimC has no retargeting model, and DungeonSlice enemies do
not die in cascade the way real trash does. There is no number for this
one — it is judgement, not measurement. Report back if it misbehaves.
```

---

## engine_loot_nearby:

`FerrazBalance.yaml` line 305

```
==========================================================================
ENGINE — the plumbing this file used to inherit from Simia's _shared.yaml.
  `sanity_checks` there is NOT just guards: it also calls auto_dispel,
  affix, auto_purge_enrage, auto_brez, auto_rez and auto_combat_potion.
  Inheriting it meant none of that could be switched off, and the potion
  call fought this file's own combat_potion line in `trinkets`.
  It is inlined in the `engine` list below so every piece has a toggle.
  One exception: the `dispels` list is called from `main` after defensives
  and interrupts, not from `engine`, so a real defensive or a kick still
  outranks a dispel.
  The five return guards were copied verbatim — do not drop any of them.

  Deliberately NOT copied, because they contain nothing a Druid can use:
    anti_cc          Human/DK/Warrior/Undead racials only
    auto_freedom     Blessing of Freedom, Tiger's Lust, Master's Call,
                     Escape Artist. The Druid answer (shapeshift out of a
                     root) already lives in this file's `defensives`.
    auto_feign_death Hunter only
    auto_death_grip  Death Knight only
    special_actions_combat   melee auto-attack, gated on player.melee
    auto_combat_potion       superseded by this file's own potion line
==========================================================================
```

---

## engine_auto_combat:

`FerrazBalance.yaml` line 334

```
cfg.auto_combat was READ by two lines in sanity_checks but defined nowhere
in this file, so it fell back to Simia's shared _shared.yaml copy. Two
problems with that: the header of this file claims it owns all of its own
plumbing, and an inherited default can change under you without any commit
here. Defined locally now, with the same options and the same default
[1, 2] the shared file uses, so behaviour is unchanged.

Worth knowing what that default means: "Off" is option 0 and is NOT
selected, so `config.engine_auto_combat.has(0)` is false and the second guard below
is inert out of the box. It only does anything if you tick Off yourself.
```

---

## auto_dispel_self:

`FerrazBalance.yaml` line 410

```
==========================================================================
DISPELS — inlined from Simia's shared lists so each piece is
  switchable on its own. UNVALIDATED: SimC has no dispel model.
==========================================================================
Lifted out of Simia's shared _shared.yaml (auto_dispel at :255,
auto_purge_enrage at :400) and inlined here so every piece is switchable.
The shared lists are NOT called from main — inheriting them would give you
all-or-nothing behaviour, which is exactly what these three toggles avoid.

What Balance can actually remove, from simia_data_dump/_dispeldata.yaml:
  friendly   remove_corruption (2782) — POISON and CURSE only, no magic
  offensive  soothe (2908) — enrage
The `.list` suffix on every condition below applies Simia's own dispel_list
filter, so a debuff flagged not-worth-dispelling is skipped automatically.

Every one of these costs a GCD, and none of it is measurable in SimC (no
dispel model). Defaults are deliberately timid: self only.
```

---

## barkskin_dmg_pct:

`FerrazBalance.yaml` line 455

```
==========================================================================
DEFENSIVES — UNVALIDATED: SimC has no M+ damage-intake model.
  Two different scales here: incoming.mitigated.pct is post-defensives,
  so 40 on a Dmg% slider is NOT 40 on an HP% slider.
==========================================================================
Barkskin: proactive trigger. incoming.mitigated.pct is post-defensives,
so NOT comparable to the HP slider below (40 here != 40 there).
```

---

## barkskin_hp:

`FerrazBalance.yaml` line 470

```
Reactive floor, unmeasured like everything defensive here.
```

---

## frenzied_regen_hp:

`FerrazBalance.yaml` line 479

```
Lower than Barkskin: Bear Form costs two full GCDs to enter.
```

---

## hotw_bear_defensive:

`FerrazBalance.yaml` line 488

```
HotW inside Bear Form: extra Stamina/Ironfur/Frenzied Regen charge. Sole
use of the button now — party-heal use was removed to free the CD.
```

---

## thorn_bloom_threshold:

`FerrazBalance.yaml` line 505

```
==========================================================================
RACIALS — Thorn Bloom is a heal, not damage (0.13% dps, costs a GCD).
==========================================================================
Thorn Bloom: heal only, not damage — its DPS is 0.13% and costs a GCD.
Every damage placement tested measured +0.02% to -0.41% (nothing or worse).
```

---

## discord_button:

`FerrazBalance.yaml` line 526

```
==========================================================================
HELP
==========================================================================
```

---

## eclipse_down: buff.eclipse_solar.down&buff.eclipse_lunar.down

`FerrazBalance.yaml` line 537

```
No Eclipse active — filler switch and AP-floor switch (ec_st/aoe).
```

---

## burst_ok: config.auto_burst|config.burst_toggle

`FerrazBalance.yaml` line 541

```
Burst allowed: auto or manual toggle. Drives Incarnation + both trinkets + potion.
```

---

## pull_engaged: player.combat&player.standing.time>=config.inc_min_standing_time&(debuff.moonfire.up|debuff.sunfire.up)

`FerrazBalance.yaml` line 544

```
A pull is actually underway. Three conditions, all required:
  player.combat                  obvious floor.
  player.standing.time >= N      the pull is parked. Catalog: "Seconds
                                 spent standing still" — it resets the
                                 moment you move, so this is the current
                                 uninterrupted stand, not a total.
  a DoT is on the target         something has actually been hit. This is
                                 what stops the burst firing at a pack the
                                 tank has not reached yet.
No boss exception is needed here, unlike every TTD var below: standing
still is not a trash-only state, so a boss pull passes the same gate.
```

---

## inc_waiting_to_stand: var.burst_ok&talent.incarnation_chosen_of_elune&cooldown.incarnation_chosen_of_elune.charges>0&var.inc_ttd_ok&!var.cd_active&player.combat&(debuff.moonfire.up|debuff.sunfire.up)

`FerrazBalance.yaml` line 557

```
Incarnation is ready and the ONLY thing missing is the stand. This is
var.pull_engaged without its standing-time clause, plus the readiness
checks. It exists to stop the moving_* lists spending Fury of Elune out
from under the burst: FoE lasts 8s on a 60s cooldown, and Incarnation
requires FoE up or <2s away, so a Fury fired while running means the
burst waits up to ~58s for the next one if you do not park within 8s.
While this is true, the moving lists hold FoE. It clears the moment
Incarnation actually goes out (var.cd_active).
```

---

## inc_ready_to_cast: var.burst_ok&talent.incarnation_chosen_of_elune&cooldown.incarnation_chosen_of_elune.charges>0&var.inc_ttd_ok&var.pull_engaged&!var.cd_active&(cooldown.fury_of_elune.remains<2|buff.fury_of_elune.up)

`FerrazBalance.yaml` line 567

```
Incarnation ready: burst allowed, talented+charge, TTD ok, not already in
a burst window, aligned with Fury of Elune (up or <2s away — skipping that
alignment measured -0.47% DungeonSlice), and a real pull is underway.
```

---

## cd_active: buff.celestial_alignment.up|buff.incarnation_chosen_of_elune.up

`FerrazBalance.yaml` line 572

```
Celestial Alignment/Incarnation active — trinkets/potion ride this window.
```

---

## inc_ttd_ok: (target.boss|target.time_to_die>=config.ttd_incarnation|fight_remains>=config.ttd_incarnation)

`FerrazBalance.yaml` line 575

```
=== TIME TO DIE (TTD) VARIABLES === (target.boss always ignores TTD)
```

---

## interrupts:

`FerrazBalance.yaml` line 583

```
Solar Beam on target/mouseover/focus. interrupt.*.check = Simia's own
kick filters (interruptible, important, in range, not already kicked).
```

---

## trinkets:

`FerrazBalance.yaml` line 590

```
Ride along with Incarnation, delayed until Fury of Elune is spent (that's
where the real window is — dropping this clause measured -0.23%).
Tested alternative (rejected): firing on cooldown regardless of burst is
+0.28% but loses a trinket use per fight and gives up the aligned burst.
```

---

## - combat_potion,delay=150,name="Combat Potion",if=var.burst_ok&config.use_potion&combat_potion.ready&player.combat&(var.potion_ttd_ok&cooldown.fury_of_elune.remains>0&var.cd_active|fight_remains<=30)

`FerrazBalance.yaml` line 597

```
fight_remains<=30 lets a potion that would otherwise be wasted at the end
of a fight go out anyway. Measured +0.61% DungeonSlice on its own against
this file's current baseline; a pre-pot on top of it measured +0.11%
(noise) and made the pair worse than this clause alone, so only the
end-of-fight half is here.
```

---

## engine:

`FerrazBalance.yaml` line 604

```
Everything `spell_queue`, `sanity_checks` and `auto_target_ranged` used to
do, inlined. Order matches the shared file so behaviour is unchanged except
where a toggle says otherwise. See the ENGINE config block for what was
deliberately left out and why.
```

---

## - queue_spell,if=!player.casting&!player.channeling

`FerrazBalance.yaml` line 609

```
`&`, not `|`. With `|` the condition is true whenever you are not doing at
least ONE of the two things — and you are almost never casting AND
channelling at once, so it read true on essentially every pass. The queue
is meant to flush only when you are genuinely free.
```

---

## - return,if=!state.rotation

`FerrazBalance.yaml` line 615

```
--- The five guards, copied verbatim from _shared.yaml sanity_checks.
Dropping any of these lets the rotation fire while dead or mounted.
```

---

## - interact_target,delay=350,if=config.engine_loot_nearby&target.lootable&target.range<=5

`FerrazBalance.yaml` line 623

```
--- Looting (was special_actions; combat half was melee-only, dropped).
```

---

## - remove_corruption,delay=500,cycle=party,cycle_order=player_first,name="Devouring Rift (Affix)",if=config.engine_affix_devour&cycle.debuff.440313.up.any

`FerrazBalance.yaml` line 628

```
--- Devour affix. Direct spell-id check, not cycle.dispelable: the affix
debuff is removable by every dispel type, so type matching would skip it.
player_first so you clear yourself before anyone else.
```

---

## - pool_resource,resource=rage,for_next=1,if=config.engine_auto_brez&mouseover.dead&mouseover.friendly&mouseover.unitframe&buff.bear_form.up&cooldown.rebirth.ready

`FerrazBalance.yaml` line 633

```
--- Rebirth / Revive on a hovered unit frame.
```

---

## - healthstone,delay=250,if=healthstone.ready&health.pct<=config.engine_healthstone

`FerrazBalance.yaml` line 638

```
--- Consumables (was auto_heal). No mana potion line: Balance does not
run out of mana in a dungeon.
```

---

## - target_enemy,delay=200,off_gcd=true,if=config.engine_auto_target.has(0)&!target.exists&enemies.combat.40y>=1

`FerrazBalance.yaml` line 643

```
--- Auto target (was auto_target_ranged), 40y like the shared ranged list.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazBalance.yaml` line 648

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

## dispels:

`FerrazBalance.yaml` line 673

```
Dispels, inlined from _shared.yaml rather than inherited. Self first: it is
the cheapest and the one you always want. The party line uses cycle=party
(the 5-man), matching what the shared list does for non-healer specs.
Soothe is last — an enrage is rarely as urgent as a debuff on a player.
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazBalance.yaml` line 680

```
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## defensives:

`FerrazBalance.yaml` line 685

```
Ahead of interrupts, so survival outranks utility. Unvalidated by sim.
```

---

## - barkskin,range_check=none,name="Barkskin (predicted)",if=incoming.mitigated.pct>=config.barkskin_dmg_pct

`FerrazBalance.yaml` line 687

```
Proactive: off-GCD, incoming.mitigated.pct already discounts running defensives.
```

---

## - bear_form,name="Panic Bear Form",if=!buff.bear_form.up&((health.effective.pct<=config.frenzied_regen_hp&cooldown.frenzied_regeneration.ready&buff.frenzied_regeneration.down)|(config.hotw_bear_defensive&health.effective.pct<=config.hotw_bear_hp&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up)))

`FerrazBalance.yaml` line 690

```
Reactive: shift to Bear first (own step so it doesn't reshift mid-heal).
Two reasons to be in Bear, not one. The old gate required Frenzied
Regeneration to be ready, which meant that with Frenzy on cooldown but
Heart of the Wild up, the shift was refused — and the HotW bear
defensive two lines below became unreachable exactly when it was the
only defensive left. Either payoff now justifies the shift; neither
being available leaves you in Moonkin, which is where the damage is.

Each reason carries its OWN health threshold, and its own preconditions.

Before this the whole line sat behind frenzied_regen_hp (30) while the
HotW defensive below triggers at hotw_bear_hp (35). Between 30 and 35
HotW wanted to fire and the shift that makes it reachable refused, so
one of the two sliders quietly did nothing in that band.

Aligning the numbers would have been the wrong fix — they measure
different things. Shifting for Frenzied Regeneration is worth a deeper
health hole than shifting for HotW, because Frenzy is a heal and HotW is
stamina plus a Frenzy charge. Splitting the branches keeps both sliders
meaningful and independent.

buff.frenzied_regeneration.down moved INTO the Frenzy branch, where it
belongs: it exists to stop re-shifting to re-apply a HoT you already
have, which has nothing to say about whether HotW is worth pressing.

Each branch of the `|` now stands on its own — health gate, readiness
check and preconditions all inside it. A branch without its own gate is
how three separate bugs got into this repo.
```

---

## - heart_of_the_wild,name="HotW (Bear defensive)",range_check=none,ignore_cds_toggle=true,if=config.hotw_bear_defensive&buff.bear_form.up&health.effective.pct<=config.hotw_bear_hp&!buff.heart_of_the_wild.up

`FerrazBalance.yaml` line 720

```
HotW before the heal so Frenzied Regen lands on the bigger (Stamina)
pool. Cast by name AND by the bear morph id (1261872) — only one
resolves per form, the other is a no-op. Costs the Moonkin-form
empowered-Starfall use of the same button.
```

---

## - bear_form,name="Root Cleanse (to Bear)",if=debuff_list.freedom.up&!buff.bear_form.up

`FerrazBalance.yaml` line 730

```
Root cleanse. TWO lines, because breaking a root needs a form CHANGE and
one line cannot cover both starting states.

A single `bear_form,if=freedom.up&(moonkin.up|bear.up)` loops: rooted
while already in Bear, it suggests Bear again, the state does not move,
the condition stays true, and the line takes every GCD until the root
expires. Shifting to the form you are already in cleanses nothing.

Bear first — it is the tankier place to be while stuck — with Cat as the
way out when Bear is where you already are.
```

---

## heal_support:

`FerrazBalance.yaml` line 743

```
Party utility, called before target guards. Unmeasured (not damage).
```

---

## - thorn_bloom,name="Thorn Bloom",if=group.count(cycle.health.effective.pct<config.thorn_bloom_threshold)>=config.thorn_bloom_members&target.valid&target.enemy&!target.dead&target.range<=40

`FerrazBalance.yaml` line 746

```
Heart of the Wild deliberately absent: the whole CD now belongs to the
Bear-form defensive in `defensives` instead of double-dipping as a heal.
```

---

## mouseover_dots:

`FerrazBalance.yaml` line 750

```
The Moonfire target cap is GONE as of 2.6, and both halves of it were wrong.

It used to read `active_enemies<6`. First problem: active_enemies is a
NAMEPLATE count per the catalog, so a training-dummy area — or any spot
with idle mobs on screen — reads 6+ and silently disabled every Moonfire
line while Sunfire, which never had the gate, kept working. That is the
same trap fixed on the Incarnation gate in 2.2; these lines were missed.

Second problem, found while verifying the threshold on the current gear:
the number 6 was wrong too. Moonfire measured better at EVERY count above
the old cap (Patchwerk, current gear, wrath off):

     5 targets   343000 vs 342710   control — cap already allowed it
     6 targets   352575 vs 390125   +10.65%
     8 targets   441949 vs 480547    +8.73%
    10 targets   515452 vs 556722    +8.01%

The cap came from the dreamgrove reference list, never from a measurement
on this character. Removed entirely. The mouseover spread line below keeps
its own cap — spreading is a different cost profile and was not measured.

Spreads DoTs without changing target. Addon-side stand-in for SimC's
target_if: +2.1% DungeonSlice, +9.8% at 5 targets.

Until 3.2 both lines gated on cluster.debuff.SPELL.count<enemies.around_target,
on the belief that Simia could not read a mouseover's debuffs. It can —
mouseover.debuff.SPELL.PROPERTY is used by Simia's own rotation_104 and
rotation_256, and by FerrazGuardianElune.yaml. The cluster proxy asks
"is the pack around MY TARGET fully dotted", which is the wrong question:
the spell lands on the MOUSEOVER, which may not even be in that pack. On a
dotted cluster the line refused to fire at an undotted mob under the mouse.
Now each line checks the actual unit it casts at.

Three other changes that came with it:
  - the 1.5s lockout is gone; it existed to cover the proxy being slow to
    update, and it blocked legitimate casts at a second mob within 1.5s.
    Simia's own rotations carry no lockout here. Put it back if you see
    double-casts.
  - the enemies.combat.40y<6 cap is gone from Moonfire, matching the cast
    lines: Moonfire measured better at 6, 8 and 10 targets, so capping the
    spread contradicted the cast priority.
  - mouseover.combat added: hovering an unpulled mob no longer pulls it,
    the same reason the pre-pull Wrath was removed in 3.1.
```

---

## moving_st:

`FerrazBalance.yaml` line 797

```
Instant casts only, <2 enemies. Unmeasured (SimC never moves).
```

---

## - starsurge,name="Starsurge (Proc or AP Dump)",if=buff.starweavers_warp.up|buff.touch_the_cosmos.react

`FerrazBalance.yaml` line 803

```
Starweaver clause is dead on the recommended string; kept for when it returns.
```

---

## - fury_of_elune,if=var.foe_ttd_ok&!var.inc_waiting_to_stand

`FerrazBalance.yaml` line 806

```
Held while the burst is only waiting for you to stand still — see
var.inc_waiting_to_stand. Also picks up the TTD gate the stationary
lists already had. UNMEASURABLE: SimC never moves.
```

---

## moving_aoe:

`FerrazBalance.yaml` line 813

```
Instant casts only, 2+ enemies. Unmeasured.
```

---

## - fury_of_elune,if=var.foe_ttd_ok&!var.inc_waiting_to_stand

`FerrazBalance.yaml` line 821

```
Held while the burst is only waiting for you to stand still — see
var.inc_waiting_to_stand. Also picks up the TTD gate the stationary
lists already had. UNMEASURABLE: SimC never moves.
```

---

## ec_st:

`FerrazBalance.yaml` line 828

```
Single target, standing still. DoTs -> Eclipse -> Incarnation -> Fury of
Elune -> spend AP -> fillers.
```

---

## - moonfire,if=debuff.moonfire.remains<2|debuff.moonfire.refreshable

`FerrazBalance.yaml` line 831

```
DoTs first — cooldowns ahead of them measured -3.60%, the worst reorder tested.
```

---

## - lunar_eclipse,if=var.eclipse_down&cooldown.lunar_eclipse.ready&!var.inc_ready_to_cast

`FerrazBalance.yaml` line 835

```
Yields to a ready Incarnation so the burst doesn't land on a window
about to be replaced (casting anyway measured -0.33%).
```

---

## - starfall,name="Starfall (Proc or AP Dump)",if=buff.starweavers_weft.up|buff.touch_the_cosmos.react

`FerrazBalance.yaml` line 841

```
Free procs (Starweaver dead on this string, kept for when it returns).
```

---

## - starsurge,name="Starsurge (Eclipse Down)",if=!var.eclipse_down&astral_power>=50

`FerrazBalance.yaml` line 845

```
AP floor follows the Eclipse (spend early inside, hold near cap
outside) — replaced a flat astral_power>60, measured +0.79%.
```

---

## - wrath,if=config.wrath_filler&var.eclipse_down&enemies.combat.40y<=1

`FerrazBalance.yaml` line 850

```
Wrath filler: worth keeping only on crit-heavy gear. See the
wrath_filler config block for the three measured data points — the
break-even is around ~22% crit. Default OFF: no Wrath filler.
```

---

## aoe:

`FerrazBalance.yaml` line 856

```
2+ enemies, standing still.

The 2-enemy threshold is RIGHT, but the old justification here was not: it
cited "-1.48% DungeonSlice", a style Balance does not support. Re-measured
2026-08-27 on the supported one, by forcing each list at a fixed target
count (Patchwerk, desired_targets=N, target_error=0.1). This asks the real
question — at N enemies, which list is better? — and does not depend on any
invented dungeon route:

     2 targets   ec_st 197169   aoe 204374    aoe +3.65%
     3 targets   ec_st 232799   aoe 266447    aoe +14.45%
     4 targets   ec_st 265939   aoe 325297    aoe +22.32%
     5 targets   ec_st 297875   aoe 383130    aoe +28.62%

aoe already wins at 2, so raising the threshold would hand 2- and 3-target
packs to the worse list.

One caveat recorded honestly: on the DungeonRoute route file, thresholds of
3 and 4 read +0.21% and +0.36% — the opposite sign. That is an order of
magnitude smaller than +3.65%, and it comes from an effect the fixed-target
test cannot see: astral power carries ACROSS pulls in a route, so dumping it
into Starfall on a two-mob pack that dies quickly leaves less for the boss
behind it. Real effect, but the route's pack sizes are invented, so it is
not evidence enough to move the threshold. Revisit with a route built from
an actual key.
```

---

## - lunar_eclipse,if=var.eclipse_down&cooldown.lunar_eclipse.ready&!var.inc_ready_to_cast

`FerrazBalance.yaml` line 888

```
Same cooldown block as ec_st.
```

---

## - starsurge,if=buff.starfall.up&(buff.starweavers_warp.up|buff.touch_the_cosmos.react)

`FerrazBalance.yaml` line 897

```
Starsurge weaves only under active Starfall + free proc — never
competes with Starfall for AP.
```

---

## - target_enemy,delay=250,name="Swap Off Dying Target",if=config.swap_off_dying&enemies.combat.40y>=2&target.time_to_die<action.starfire.execute_time

`FerrazBalance.yaml` line 901

```
Last thing before the hardcast filler: if the current target dies before
Starfire can land, swap rather than waste the cast. See swap_off_dying in
config for the trap risk and why the guards are there. Everything above
this line — DoTs, cooldowns, free procs, Starfall — still outranks it, so
the swap only ever costs the GCD a filler would have taken anyway.
```

---

## main:

`FerrazBalance.yaml` line 910

```
Entry point: first matching line wins the GCD, everything above the
damage lists outranks damage.
```

---

## - call_action_list,name=engine

`FerrazBalance.yaml` line 915

```
--- Engine plumbing. Must stay at the top. ---
```

---

## - return,if=!player.combat

`FerrazBalance.yaml` line 920

```
--- COMBAT WALL. Nothing below this line runs out of combat. ---
Everything above it is what the rotation is allowed to do while idle:
the engine (loot, auto-target, rez, dispels, consumables) and
heal_support (Mark of the Wild, Thorn Bloom). Below is damage, defensives,
interrupts and cooldowns — all of it combat-only.

player.combat, NOT player.auto_combat. The catalog defines the second as
a "Config-based auto-combat check", not combat state; using it here is
the bug that silently disabled four rotations in this repo.
```

---

## - return,if=!target.valid&!((config.engine_auto_combat.has(1)&target.quest_mob&target.enemy&!target.dead)|(config.engine_auto_combat.has(2)&target.combat&target.enemy&!target.dead)|(config.engine_auto_combat.has(3)&target.targeting_party&target.enemy&!target.dead))

`FerrazBalance.yaml` line 931

```
--- Target guards ---
```

---

## - starfire,name="Back to Moonkin (Fluid Form)",if=talent.fluid_form&buff.moonkin_form.down&health.effective.pct>config.frenzied_regen_hp&!buff.frenzied_regeneration.up

`FerrazBalance.yaml` line 936

```
Back to Moonkin. Two lines, split on Fluid Form, so this is correct on
either build.

Fluid Form (449193) does more than SimC's spell data says. The in-game
tooltip carries THREE lines:

  Shred, Rake, and Skull Bash ... shift you into Cat Form
  Mangle ... shifts you into Bear Form
  Wrath and Starfire shift you into Moonkin Form, if known.

SimC's Description field for that id only reproduces the first line, so
`spell_query` reads as though Starfire were not covered. It is. Treat
SimC descriptions as unreliable; its Attributes and Talent Entry fields
have held up, the prose has not.

So with Fluid Form talented, Starfire returns you to Moonkin AND deals
damage in the same global — strictly better than spending a GCD on the
form. Without it, the explicit shift is the only way back.
```

---

## - call_action_list,name=defensives

`FerrazBalance.yaml` line 956

```
NOTE: a pre-pull `wrath,if=!player.combat&!player.moving&target.distance<=40`
used to sit here. It auto-started combat on any attackable target within
40y, which in a dungeon means pulling whatever you happen to have clicked
— the tank decides the pull, not the rotation. It was also the wrong
spell: with Lunar Calling, Starfire carries +120% on the primary target
and Wrath no longer flips Eclipse, which is why the filler is pure
Starfire. Removed. Pull by hand.

--- Survival, then utility, then the burst window ---
```

---

## - call_action_list,name=moving_aoe,if=player.moving&enemies.combat.40y>1

`FerrazBalance.yaml` line 970

```
NOTE on out-of-combat pulling: the guard is target.valid, three lines up.
The docs define it as "Comprehensive check: exists, enemy, alive, IN
COMBAT (PvE)", and `return,if=!target.valid|target.dead|!target.attackable`
halts the rotation whenever it is false. A mob nobody has pulled is not a
valid target, so the damage lists never see it.
Do NOT add player.combat to these calls. It looks like the same guard and
is not: casting is what puts YOU in combat, so requiring it first means
the rotation can never take the first action, and it also blocks joining
a pull the tank started, where target.combat is true and player.combat is
not yet.

--- Damage priority: moving first (instant-only), then stationary. ---
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "4.9.0"

`FerrazBalance.yaml` line 1

```
=============================================================================
Balance Druid - spec 102 - patch 12.1 (Midnight) - Elune's Chosen, M+.
=============================================================================

Lists, in the order `main` calls them:
  main            entry point: plumbing, target guards, form, then delegates
  heal_support    Mark of the Wild, Thorn Bloom
  defensives      Barkskin, Bear Form/HotW/Frenzied Regen, root cleanse
  interrupts      Solar Beam (target/mouseover/focus)
  dispels         Remove Corruption, Soothe (target and mouseover)
  trinkets        trinkets + combat potion, tied to the burst window
  moving_st/aoe   instant-only priority while moving
  ec_st / aoe     stationary damage priority, 1 / 2+ enemies
  mouseover_dots  called from `aoe`, spreads DoTs without changing target

Priority:
  ST   DoTs -> Eclipse -> Incarnation -> Fury of Elune -> free procs
       -> Starsurge -> Starfire
  AoE  anti-cap Starfall -> DoTs -> Eclipse -> Incarnation -> Fury of Elune
       -> free procs -> Starfall -> Starsurge weave -> Starfire

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/Balance.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.

REFERENCE BUILD, 4.6.0: the most-used Balance build on WarcraftLogs. It
replaced Jeannelin's +18 build and moved five nodes:
  gained  Sundered Firmament, Stellar Amplification, Meteorites
  lost    Orbit Breaker, Elune's Guidance
Fluid Form stays, hero tree stays Elune's Chosen, Starweaver is still absent
so the lines flagged dead for it remain dead.

Losing Elune's Guidance is the change that matters: it shortened the
Incarnation cooldown, so the charge budget and the useful ttd_incarnation
both moved. Anything tuned against Incarnation frequency needs re-measuring
after a build change, not carrying over.

Sundered Firmament is now talented and this file deliberately does NOT gate
Fury of Elune on it, unlike the raid file. Measured three ways on this build
and all three lost: the raid's own condition -0.64% AoE-only and -1.42%
applied to both lists, a bare atmospheric_exposure check -0.79%, and the loss
holds at 1, 3 and 5 fixed targets. Fury of Elune on cooldown is correct here.

Percentages older than 4.6.0 in .agents/rationale/Balance.md were measured on
fight_style=DungeonSlice, which Balance does not support - see
.agents/SIMC_METHODOLOGY.md - and against the previous build. Treat them as
provisional.
=============================================================================
```

---

### ttd_incarnation:

`FerrazBalance.yaml` line 120

```
Don't spend a long cooldown on trash about to die. Bosses ignore these.
Re-measured on the 4.6.0 build, 8 seeds, counting Incarnations PER PULL
rather than just total DPS:

    15s   -          40% of pulls with none, 0% doubled, 0% boss missed
    20s   +0.37%     40%                     0%          0%
    25s   +0.61%     40%                     0%          0%
    30s   +0.75%     41%                     1%          0%

25 is the last value that gains without reintroducing a double. The 40% of
pulls that get no Incarnation at all is not a gate problem and no condition
fixes it: 6 casts across 10 pulls is a charge budget, not a decision.

This was briefly set to 20 off the same measurement run against the PREVIOUS
build, which carried Elune's Guidance. That talent shortened the Incarnation
cooldown, so charges came back fast enough to double up on a pull; without
it they no longer do, and the useful value moved.
```

---

### bear_defensive_active: health.effective.pct<=config.frenzied_regen_hp|(config.hotw_bear_defensive&health.effective.pct<=config.hotw_bear_hp&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up))

`FerrazBalance.yaml` line 442

```
The Bear defensive still wants you in Bear. Mirrors both branches of the
Panic Bear Form line, so the exit gate below can never contradict it.

Effective health (healthPct - healAbsorbPct + incomingHealsPct), restored in
4.7.2. It was swapped to real health in 4.7.0 to stop the rotation shifting
to Bear constantly - but that turned out to be the Root Cleanse pair, not
this. The swap fixed nothing and was reverted.

Entry and exit must keep reading the SAME metric. Mismatching them is what
produced the Bear/Moonkin loop in 189c467.
```

---

### druid_shapeshift_root: player.debuff.root.up|player.debuff.snare.up

`FerrazBalance.yaml` line 455

```
Debuffs a DRUID SHAPESHIFT actually removes: roots and snares, and nothing
else.

debuff.root and debuff.snare are Simia's own mechanic categories. Neither is
in expression-catalog.json, but both are used by the shipped rotations -
community_Holy.yaml gates Blessing of Freedom on
(cycle.debuff.snare.up|cycle.debuff.root.up) - and debuff.curse is the same
mechanism with 10 uses. Absent from the catalog is not evidence of invalid;
see section 12 of SIMIA_DOCUMENTATION.md.

NOT debuff_list.freedom. _casts.yaml documents that tag as "Needs
freedom/root break", which is what a Blessing of Freedom clears. Four of its
36 entries are neither root nor snare and a shift does nothing to them -
Ritual Sacrifice (1259789) is a Stun, Hearty Bellow (1235125), Fel Beam
(1218187) and Gravitic Orbs (1223298) carry no mechanic at all. Any of them
left the gate true after the shift, so the rotation kept paying globals to
break a root it could not break. Caught in game by snapshot on the Balance
file: debuff_list.freedom.up = 1 [PASS] with nothing shapeshiftable.

This replaced a hand-built list of the 32 root/snare ids from that same
audit (see 2f141fe). The categories cover new content on their own; the list
would have needed editing every patch.

UNVERIFIED IN GAME. If these do not resolve the variable is simply false and
the cleanse stops firing - no loop, just a lost utility. Confirm with
/simia snapshot while rooted: the trace should show the gate PASS.
```

---

### - bear_form,name="Root Cleanse (to Bear)",line_cd=8,if=config.root_cleanse&var.druid_shapeshift_root&!player.stunned&!buff.bear_form.up

`FerrazBalance.yaml` line 583

```
Root cleanse needs a form CHANGE, so two lines: one line would loop when
you are already in the form it suggests.

player.rooted, NOT debuff_list.freedom.up. _casts.yaml documents that tag
as "Needs freedom/root break" - a list of debuffs a Blessing of Freedom
would clear, which is NOT the same as what a shapeshift clears. Ethereal
Shackles is tagged [tank, magical, freedom]; shifting does nothing to a
magical root. So the gate stayed true after the shift, the two lines
ping-ponged Bear/Cat, and in game it read as turning into a bear
constantly. Confirmed from a snapshot: debuff_list.freedom.up = 1 [PASS]
on Root Cleanse (to Bear) with nothing to cleanse.

line_cd caps the damage if it happens anyway. player.rooted is tighter but
still cannot tell a magical root from a physical one, so a root the shift
cannot break would loop again - at one attempt every 8s instead of every
global.

!player.stunned because a stun blocks the shift outright. Copied from
FerrazRestoDruidRaid.yaml, which already had this right.
```

---

### - return,if=buff.bear_form.up&var.bear_defensive_active

`FerrazBalance.yaml` line 730

```
Nothing below may cast while the Bear defensive is holding you in Bear.
Every damage spell cancels the form, and Panic Bear Form then pays another
global to re-enter it.

This sits directly under `defensives` and ABOVE interrupts on purpose.
It used to sit under `trinkets`, which left Solar Beam free to cancel the
form the shift had just paid for - the fuzzer found that in the current
file after the first version of this guard was supposed to have fixed it.
Dispels cancel the form the same way. Inside the Bear window survival
outranks the kick; the window is short and health-gated.
```

## HotW: Bear defensive removed, Moonkin party heal put in its place — 2026-08-30 (4.10.0)

Heart of the Wild pressed in **Moonkin Form** lands a healing HoT on all five
party members. The file was spending the cooldown on a Bear-form defensive
instead: it shifted out of Moonkin, took the stamina/max-health morph, and
healed nobody but the player.

Removed:

```yaml
- heart_of_the_wild,name="HotW (Bear defensive)",...&buff.bear_form.up&...
- 1261872,name="HotW (Bear morph)",...&buff.bear_form.up&...
```

`1261872` is the Bear morph — its tooltip is "Maximum health increased by
$s1%", which is the whole of what that branch bought.

Replaced by one line, no form change at all:

```yaml
- heart_of_the_wild,name="HotW (Party Heal)",range_check=none,ignore_cds_toggle=true,if=config.hotw_party_heal&buff.moonkin_form.up&group.count(cycle.health.effective.pct<config.hotw_hp)>=1
```

Three things fell out with it:

- `Panic Bear Form` loses its second branch. Bear is now entered only for
  Frenzied Regeneration, so the two-branch structure that 4.x built up (each
  branch carrying its own health gate and preconditions) collapses back to one.
- `bear_defensive_active` loses the HotW clause for the same reason. It still
  mirrors Panic Bear Form exactly, which is the invariant that matters: entry
  and exit must read the same metric.
- `heal_support`'s note that "the whole CD now belongs to the Bear-form
  defensive" is gone — it was describing the arrangement this change undoes.

### Config rename

`hotw_bear_defensive` → `hotw_party_heal`, `hotw_bear_hp` → `hotw_hp`. The keys
changed because the meaning did; leaving "bear" in the name of a line that never
touches Bear Form would be worse than the reset. **Saved values for the old keys
do not carry over** — the new toggle starts at its default of ON, where the old
one was OFF.

### Not measured, and not measurable

SimC has no party-healing model for this, and the deeper problem is that it does
not model the ability at all for Balance: adding `heart_of_the_wild` to the M+
APL fires it (2.88 executes on a Patchwerk run) while producing **no buff and no
DPS change** — 146,952 → 147,000, inside the ±291 error. The action exists in the
sim and does nothing. Nothing about this line can be judged from a profileset.

### A spell-data trap, recorded so it is not walked into twice

Two live spells share the name Heart of the Wild:

| id | CD | What the data says |
|---|---|---|
| 108291 | 300s | "Damage of your Balance spells increased by 30%, and Starsurge is instant" |
| 1261867 | 120s | "Perform a powerful off-role ability depending on your currently active shapeshift form" |

Only **1261867** carries a `Talent Entry` (class tree, row 10, col 5) — it is the
one on the 12.1 tree. 108291 is the older version still sitting in the DBC, and
reading it first suggests HotW is a +30% damage cooldown for Balance, which it is
not on this patch. The form morphs hang off 1261867: `1261868` Cat (what the
Guardian file weaves for), `1261870` Moonkin, `1261872` Bear.

`_morphs.yaml` has `heart_of_the_wild: 1261868` **commented out**, which is why
this file and the Guardian one cast HotW by name rather than relying on Simia to
resolve the morph. The new line casts by name only — the Moonkin morph id was
not verified in game, and guessing an id here buys nothing.

## Burst toggle: one Incarnation per flip — 2026-09-01 (4.11.0)

Asked for: turn the Burst toggle on, let it fire Incarnation once, then have it
switch itself off and wait to be turned on again.

**The switching-itself-off half is not possible.** Nothing in Simia writes to a
config. `actionTypes` in `expression-catalog.json` lists 24 special actions and
none of them touch config; a scan of all 112 files in `simia_data_dump/` finds
no rotation setting one either. `config.X` is read-only to a rotation.

What is possible is the behaviour, via a latch:

```yaml
  burst_latch:
    - variable,name=inc_spent,value=0,if=!config.burst_toggle
    - variable,name=inc_spent,value=1,if=var.cd_active
```

```yaml
burst_ok: config.auto_burst|(config.burst_toggle&(!config.burst_once|variable.inc_spent=0))
```

Toggle off zeroes the latch; the burst window going up sets it. So one flip
buys exactly one window, and flipping OFF then ON is the rearm gesture.

`burst_latch` is called from `main` directly above `heal_support`, i.e. above
the combat wall, so the reset lands the moment the toggle goes off rather than
waiting for the next pull.

It latches on `var.cd_active` (`buff.celestial_alignment.up|buff.incarnation_chosen_of_elune.up`)
rather than on the Incarnation cast, so it works whichever of the two talents is
on the build and cannot miss the cast it was watching for.

`config.burst_once` ships **OFF**, and the whole thing only matters with
`auto_burst` off — the auto path never consults the toggle.

### The part the user has to live with

The toggle keeps showing **ON** after it is spent. There is no way to grey it
out or flip it. The switch reads as active while granting nothing, which is a
genuine wart; the alternative was not building the feature.

### Unverified: whether an action-assigned variable persists between ticks

The whole design rests on `variable,name=X,value=1` still reading 1 on the next
tick. That is SimC's semantics, and `set_tank_var` in `FerrazGuardianElune.yaml`
is written as though it holds — it resets `tank_buster_remains` to 999 at the
top of every pass, which is only necessary if values carry over.

But Simia's documentation says of the `variables:` block only that it is
"evaluated every tick", and says nothing at all about the assignment action.
Neither `expression-catalog.json` nor `SIMIA_DOCUMENTATION.md` states the
lifetime, and no rotation in the dump depends on persistence in a way that would
prove it.

**Answered in game on 2026-09-01: assignments DO persist between ticks.** The
latch holds — one flip of the toggle buys one Incarnation and no second window
is offered while it stays on. That settles a question the Simia documentation
does not answer anywhere: `variable,name=X,value=1` still reads 1 on later
ticks, matching SimC semantics. Anything else in this repo that wants a latch
can rely on it.


## Pressing the burst toggle off — 2026-09-01 (4.12.0)

The latch works but leaves the switch lit while spent, which reads as active
and grants nothing. Nothing in Simia writes a config or an app state flag —
checked against the catalog's `actionTypes`, the extension's special-action
list, and a scan of all 112 dump files for write patterns; all 26 hits are
reads inside conditions.

One indirect path exists. `type: toggle` is documented as *"Ephemeral boolean
toggle. State always starts OFF and is never saved. Shows spell icon on overlay
when active. **Can be hotkeyed.**"* And `hotkey=` overrides the scan code a line
presses. So the rotation can press the toggle's own key.

```yaml
- mark_of_the_wild,name="Burst Toggle Off (key press)",hotkey=config.burst_toggle_hotkey,modifier=config.burst_toggle_modifier,off_gcd=true,ignore_queue=true,ignore_usable=true,ignore_cooldown=true,line_cd=2,if=config.burst_once&config.burst_toggle&config.burst_toggle_hotkey>0&variable.inc_spent=1
```

**No reset variable is needed.** The press switches the toggle off, which zeroes
`inc_spent` on the next tick through the line above it, which makes this line
false. The toggle going off is its own reset. `line_cd=2` covers the window
while the key registers — without it the line could fire again before the
toggle state updates and flip it straight back on.

`hotkey=config.X` is not invented: `delay=config.interrupt_timing` appears in
`community_LPOutlaw_V1.yaml` and `community_TeK_s_Kidneyspears_outlaw.yaml`, so
step modifiers do accept config values.

### Why this ships at 0 and is labelled experimental

**`hotkey=` has zero uses across all 112 files in the dump.** Not one rotation
has ever used it. Everything above is read off the documentation and a
same-shaped precedent, not off anything anyone has run.

The failure mode is bounded but real: if the redirect does not happen, the
carrier spell is cast instead. Mark of the Wild was picked for that reason —
an accidental cast is a rebuff and one global, nothing worse. A carrier like
Moonkin Form would have cancelled the form, and Entangling Roots would have
broken crowd control.

`burst_toggle_hotkey` defaults to **88** (X, the key this character has the
toggle bound to). That is safe to ship enabled because the line also requires
`config.burst_once`, which defaults **false** — nobody who has not opted in can
have a key pressed for them. Set the code to 0 to disable the line outright.

The modifier config takes the raw code (16 Shift, 17 Ctrl, 18 Alt) rather than
a dropdown, because a dropdown returns its index and would need a mapping the
DSL cannot express cleanly.

### They are scan codes after all — and how that was settled

An earlier version of this section claimed the opposite, confidently and
wrongly: that the numbers were Windows virtual-key codes, reasoned from the
documentation's "1 is 49" example. A snapshot log settled it with real data.

`snapshot=true` writes a `=== BINDINGS ===` block listing every keybind Simia
knows. The modifiers it stores are **29, 42 and 56** — LCtrl, LShift and LAlt
as *scan* codes (0x1D, 0x2A, 0x38). As virtual-key codes those numbers are
meaningless. And every toggle in the table sits on a function key, which decodes
cleanly only as scan codes:

```
60=F2  61=F3  63=F5  64=F6  67=F9  68=F10  87=F11  88=F12   82=Numpad0
```

**Do not derive these from a table. Read them.** Put `snapshot=true` on any
line, trigger it, open the log, and take the number Simia itself recorded.

### What the first attempt was actually pressing

The config shipped at 88, chosen from a virtual-key table as "X". In scan
codes 88 is **F12**, which the bindings block shows belongs to pseudo-spell
`1000000019` — a *different* toggle. So for six firings, two seconds apart, the
rotation was flipping some other switch of the user's on and off. It failed
safe only by luck.

The burst toggle is `1000000074`, on **68 (F10) with no modifier**. It is the
only id outside the `1000000001`–`1000000020` block, which is what a
rotation-defined toggle looks like against Simia's built-in ones. Scan code 45,
X, is bound to nothing in all 71 entries.

### What the snapshot proved about the mechanism

Six logs, at exactly two-second intervals matching `line_cd=2`. **The line
fires.** Everything about "is it being suggested" is settled: it is, reliably.

`Mark of the Wild`'s last cast in the same log was 284s earlier, so the carrier
was never cast either — meaning the press did go somewhere other than the
carrier's own keybind. That is consistent with `hotkey=` working and hitting the
wrong key, which is the reading this change acts on.

Untested in game.


## The hotkey experiment is dead — 2026-09-01 (4.14.0)

Removed: the `Burst Toggle Off (key press)` line, `burst_toggle_hotkey` and
`burst_toggle_modifier`. The latch stays; it works.

`snapshot=true` settled it with three facts from one log.

**The line fires.** Eight snapshots across twelve seconds, at the `line_cd`
interval. Whether the condition was reached was never the problem.

**No key was ever pressed.** `LAST CASTS` covers the preceding 10.4 seconds and
holds only Starfall, Sunfire, Starfire and Moonfire. No Mark of the Wild — and
the carrier is bound, `1126 -> keybind=79 modifier=0`. Neither the overridden
key nor the carrier's own key went out. Nothing was pressed at all.

**And the reason:**

```
OneButtonRotation: 194153     (Starfire)
AutoCast: enabled=YES
```

That field tracks the suggestion: an earlier log shows `93402` (Sunfire). It is
the spell currently mapped to the single button. At the instant Simia wrote a
snapshot *for Mark of the Wild*, the one button was still pointing at Starfire.

So the line evaluated true and produced a log, but **never became the
suggestion**. With One Button Rotation active every press is delivered through
that one button, and a line's own `hotkey=` is not part of that path.

### What this cost, and the rule that comes out of it

Four attempts: wrong key encoding (virtual-key instead of scan), wrong target
(F12, which is a different toggle of the user's, flipped every two seconds for
six firings), `off_gcd` removed on a hunch, then the right key. Only the fourth
produced evidence, and only because the third added `snapshot=true`.

**Instrument first.** The snapshot was available from the start and would have
answered "does this press anything" before any of the guesses. Every attempt
before it was theory against a black box.

Recorded for anyone who tries this again: `hotkey=` still has zero working uses
anywhere. It may do something in a non-one-button setup; that is untested and
not worth chasing.

### Where the burst toggle ends up

The latch is the ceiling. One flip of the toggle grants one Incarnation, and
OFF then ON rearms it. The switch stays lit while spent — no config can be
written by a rotation, and pressing its key from a rotation does not work
either. That is a UI wart with no fix available from inside a rotation file.


## The latch broke the trinkets — 2026-09-01 (4.14.1)

Reported after the latch was confirmed working: Incarnation fires once as
intended, and the trinkets and combat potion stopped coming out entirely.

The latch and the trinkets were reading the same variable for two different
questions.

```
toggle on          -> inc_spent=0 -> burst_ok true
Incarnation up     -> cd_active true
latch fires        -> inc_spent=1 -> burst_ok FALSE
trinket lines need    burst_ok AND cd_active  -> never both true
```

`variable,name=inc_spent,value=1,if=var.cd_active` is spent by the buff going
up, and the trinket and potion lines all end in `&var.cd_active` because they
are meant to ride that window. So the latch closed the gate at the exact
instant those three lines wanted it open. They were dead from 4.11.0 onward,
and nothing in the file said so.

Split into two variables:

```yaml
burst_armed: config.auto_burst|config.burst_toggle
burst_ok: var.burst_armed&(!config.burst_once|variable.inc_spent=0)
```

- **`burst_armed`** — may the burst be used at all. Trinkets and potion read
  this. They ride a window that is already open; whether another one may be
  opened is none of their business.
- **`burst_ok`** — may a NEW window be opened. Only `inc_waiting_to_stand` and
  `inc_ready_to_cast` read it, and both are about casting Incarnation.

The lesson is narrower than "test more": `burst_ok` was a name that answered
two questions, and the latch changed the answer to one of them. Any gate that
several unrelated lines read should be checked against each of those lines when
its meaning changes, not just against the line it was written for.
