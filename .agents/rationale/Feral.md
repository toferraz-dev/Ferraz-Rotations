# Feral — rationale
Every technical comment that used to live in `FerrazFeral.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "2.9.0"

`FerrazFeral.yaml` line 1

```
=============================================================================
Feral Druid — spec 103 — patch 12.1 (Midnight) — Druid of the Claw, M+.
=============================================================================

Measured with SimC 1210-01, fight_style=DungeonSlice (M+ proxy), against
the recommended string. Harness: sim/ab_test_feral.py, profile
sim/Ferraz_feral.simc (gear: SimC's own MID1 Feral preset). Baseline for
comparison is SimC's own default APL for this build, sourced from
dreamgrove (github.com/dreamgrove/dreamgrove/blob/master/sims/cat/feral.txt)
and already dungeon-tuned — not a guess.

BIGGEST FINDING: the `cooldown` list computed var.holdBerserk and the
Convoke count-remaining variables but never actually cast Berserk, Convoke
the Spirits, trinkets or a potion anywhere in the file. Adding them back
measured +18.42% DungeonSlice — by far the largest number here. Two other
candidate fixes tested and NOT applied: removing Tiger's Fury's
hold-for-Frantic-Frenzy clause (no measurable gain once Berserk is
actually cast, possibly a tiny loss) and the dotc_rake_threshold talent
fix (-0.14%, noise — fixed anyway since it costs nothing, see its own comment).

Separately from the sim: a dead `return,if=auto_combat.player` at the top of
main was silently aborting the whole rotation in-game (see the note there).
SimC never had that line, so no number here captures it.

BUILD ASSUMPTIONS — talents confirmed on the recommended string by decoding
it through the local SimC binary (sim/tools/simc-1210.01.62ca36f-win64/simc.exe).
The hero tree is DRUID OF THE CLAW (all 14 points: Ravage, Claw Rampage,
Killing Strikes, Dreadful Wound, Twin Claw, Strike for the Heart, Bestial
Strength, Aggravate Wounds, ...), plus Frantic Frenzy, Rampant Ferocity,
Primal Wrath, Double-Clawed Rake, Infected Wounds, Heart of the Wild, Fluid
Form and Unseen Predator apex maxed 4/4.

This file has now been on both hero trees (Druid of the Claw -> Wildstalker
-> back to Druid of the Claw) and the priority never had to change for any
of it: every affected line is gated on hero_tree.* or on a talent, so the
Ravage and Heart of the Wild lines simply go live or inert on their own and
the aoe_builder branches swap sides by themselves.
NOT talented on this string (harmless dead weight): Lunar Inspiration, Wild
Slashes, Panther's Guile, and every hero_tree.wildstalker check.

Two Druid-of-the-Claw candidates were measured on the new string and NOT
applied, all three inside the error bar of the current priority:
    Shred on a Sudden Ambush proc   -0.02%  (worth +2.35% on the RAID file,
                                             which is single-target; here the
                                             builder list barely runs)
    Apex Predator's Craving line     -0.04%
    both together                    -0.08%

Bite pooling (ferocious_bite with max_energy) was tested here and measured
nothing — it is worth +2.87% on the RAID build only, where Saber Jaws pays
for it. See FerrazFeralRaid.yaml.

Unseen Predator (apex): Tiger's Fury guarantees a bonus Unseen Attack on
your next 2 combo-point generators — entirely passive/automatic on the
game side, no APL line needed. Its stacking damage buff (Unseen Predator's
Craving) is not currently spent around deliberately; a finisher-pooling
window built around it is a possible future gain, not applied here.
=============================================================================
```

---

## about:

`FerrazFeral.yaml` line 70

```
Display-only build stamp — keep in sync with version:/patch: above.
```

---

## panic_bear_hp_pct:

`FerrazFeral.yaml` line 83

```
The panic Bear Form shift had a literal 25 and no name=, the only threshold
in either Feral file that was not a slider and the only defensive that did
not show up in the execution log when it fired.
```

---

## use_trinket_1:

`FerrazFeral.yaml` line 151

```
=== COOLDOWN CONFIGURATIONS ===
Defaults ON: the whole cooldown block below (Berserk/Convoke/trinkets/
potion) was entirely missing before — see the `cooldown` list comment.
```

---

## ttd_berserk:

`FerrazFeral.yaml` line 172

```
=== TIME TO DIE (TTD) CONFIGURATIONS ===
Stop a long cooldown being spent on trash that is about to die. Same shape
as FerrazBalance.yaml's TTD block, including the target.boss short-circuit
in each variable: a boss never counts as "about to die", so a boss pull
always bursts immediately no matter how these are set.

UNVALIDATED by simulation, like the Balance ones: SimC dummies live the
whole fight, so a TTD gate can only cost DPS there and never gain any.
Measured on DungeonSlice purely to confirm it costs nothing (see the
header). The actual gain is in-game, on trash that dies early.
```

---

## engine_loot_nearby:

`FerrazFeral.yaml` line 218

```
=== ENGINE & DISPEL CONFIGURATIONS ===
Inlined from Simia's _shared.yaml instead of inherited, so every piece has
a toggle. See the `engine` list for what was left out and why.
Druid removes POISON and CURSE only (remove_corruption 2782) plus enrage
offensively (soothe 2908) — simia_data_dump/_dispeldata.yaml. The .list
suffix applies Simia's own dispel_list filter.
UNVALIDATED: SimC models none of this.
```

---

## protected_channel: player.casting.spell_id=323764|player.casting.spell_id=391528

`FerrazFeral.yaml` line 307

```
The channelled ids this spec can actually produce, confirmed against client
69404: Convoke is 323764 (Night Fae) and 391528 (talent), both flagged
"Is Channelled". Tranquility (740) is deliberately absent — its spell data
says "Talent Entry: Restoration [tree=spec]", so Feral cannot cast it.

Written WITHOUT a leading player.channeling& on purpose. With it, the term
is a strict subset of the player.channeling already in the guard and
contributes nothing. Standing alone it covers the case the guard was
missing: the addon reporting Convoke through UnitCastingInfo before it
flips to UnitChannelInfo, which is the window a channel gets clipped in.
```

---

## dotc_rake_threshold: 99-94*(talent.wild_slashes&talent.merciless_claws)-91*(talent.wild_slashes&!talent.merciless_claws)

`FerrazFeral.yaml` line 322

```
Was gated on talent.infected_wounds — the real formula (dreamgrove/SimC
default APL) gates on talent.merciless_claws instead. No measured DPS
difference on this build (wild_slashes untalented -> 99 either way), but
the formula is now correct if the build changes. Fixed, not guessed:
confirmed via sim/ab_test_feral.py's dotc_fix_only variant (-0.14% ~).
```

---

## berserk_ttd_ok: (target.boss|target.time_to_die>=config.ttd_berserk|fight_remains>=config.ttd_berserk)

`FerrazFeral.yaml` line 339

```
=== TIME TO DIE (TTD) VARIABLES === (target.boss always ignores TTD)
```

---

## engine:

`FerrazFeral.yaml` line 348

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

`FerrazFeral.yaml` line 357

```
`&`, not `|`. With `|` the condition is true whenever you are not doing at
least ONE of the two things — and you are almost never casting AND
channelling at once, so it read true on essentially every pass. The queue
is meant to flush only when you are genuinely free.
```

---

## - attack_target,off_gcd=true,delay=100,if=player.combat&target.exists&target.attackable&target.alive&target.in_melee&!player.auto_attacking

`FerrazFeral.yaml` line 372

```
Melee-only, and this file IS melee: keeps auto-attack running.
target.in_melee, not target.range<=8: SIMIA_DOCUMENTATION rule 7 — range is
EDGE distance, so 'max melee' reads 4.5 on a small mob and 2.33 on a
9-reach boss. The shared list used the constant; this does not.
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazFeral.yaml` line 381

```
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## - target_enemy,delay=200,off_gcd=true,if=config.engine_auto_target.has(0)&!target.exists&enemies.combat.8y>=1

`FerrazFeral.yaml` line 393

```
Melee auto target: 8y, matching the shared melee list.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazFeral.yaml` line 398

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

## - trinket_1,if=config.use_trinket_1&trinket_1.ready&var.trinkets_ttd_ok

`FerrazFeral.yaml` line 431

```
This whole list used to be just the two finisher-CD lines below: the
file computed var.holdBerserk and the Convoke count-remaining variables
but never actually cast Berserk, Convoke the Spirits, trinkets or a
potion anywhere. Confirmed missing via sim/ab_test_feral.py against the
SimC default (dreamgrove-sourced) APL for this exact build — adding
them back measured +19.73% DungeonSlice, the single largest number in
this file.
```

---

## - convoke_the_spirits,if=var.bs_inc&var.convoke_ttd_ok&buff.tigers_fury.up&(prev_gcd.1.rip|prev_gcd.1.ferocious_bite|prev_gcd.1.primal_wrath|buff.tigers_fury.remains<=1+action.convoke_the_spirits.execute_time)

`FerrazFeral.yaml` line 448

```
Talented on the recommended string. Lines up with Berserk, on the GCD
right after a finisher so the burst window snapshots a full-CP window.
```

---

## - prowl,if=!player.combat&!buff.shadowmeld.up&(!var.rake_tf|dot.rake.refreshable)

`FerrazFeral.yaml` line 470

```
Same reasoning as the main-list Prowl: cannot be cast in combat.
```

---

## heal_support:

`FerrazFeral.yaml` line 486

```
Mark of the Wild, OOC Regrowth top-off.
```

---

## form:

`FerrazFeral.yaml` line 491

```
Emergency Bear Form, Fluid Form auto-shift, manual Cat Form entry, and
the pre-pull Prowl opener.
```

---

## - bear_form,name="Panic Bear Form",range_check=none,if=health.pct<=config.panic_bear_hp_pct&!buff.bear_form.up&player.combat&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up)

`FerrazFeral.yaml` line 494

```
Shifting to Bear costs you the Cat rotation, so it has to buy something.
In THIS file the only payoff is Heart of the Wild on the next line —
there is no Frenzied Regeneration line here at all, because Frenzied
Regeneration (22842) reads "Talent Entry: Generic [free=(Guardian)]",
a class talent Feral has to spend a point on and this build does not.

Without this gate the shift fired on health alone, so with HotW on
cooldown you left Cat Form, gained nothing, and walked back. Pure DPS
loss. Now the shift only happens when the button it exists to press is
actually available.
```

---

## - prowl,range_check=none,if=!player.combat&!var.bs_inc&buff.prowl.down&buff.shadowmeld.down&(target.attackable|enemies.40y)

`FerrazFeral.yaml` line 511

```
!player.combat added: Prowl cannot be cast in combat (Blizzard's own
restriction) — if Simia doesn't already model that as "unusable" the
same way it does cooldowns/resources/range, the buff never applies,
the condition never turns false, and this line traps priority forever
every GCD in combat, blocking Tiger's Fury/cooldown/finisher/builder
below it entirely. This is meant as the pre-pull opener only.
```

---

## predatory_swiftness:

`FerrazFeral.yaml` line 526

```
Regrowth off a Predatory Swiftness proc — deliberately called after
`defensives` in main, so a real defensive cooldown outranks a proc heal.
```

---

## - return,if=player.channeling|player.casting|var.protected_channel

`FerrazFeral.yaml` line 533

```
Convoke is a channel and nothing here ever wants to break it. Bare
player.channeling, the shape every official rotation in simia_data_dump
uses — see FerrazRestoDruid.yaml, where a narrower id-based guard failed
open often enough to clip Convoke in a real key.
```

---

## - return,if=!player.combat

`FerrazFeral.yaml` line 544

```
--- COMBAT WALL. Nothing below this line runs out of combat. ---
Allowed while idle, above the wall: the engine (loot, auto-target,
Rebirth/Revive, dispels, consumables), heal_support (Mark of the Wild,
out-of-combat Regrowth) and `form` — which owns the pre-pull Prowl and
entering Cat Form, both of which must work before the pull.

player.combat, NOT player.auto_combat. The catalog defines the second as
a "Config-based auto-combat check", not combat state; using it here is
the bug that silently disabled four rotations in this repo.
```

---

## - call_action_list,name=defensives

`FerrazFeral.yaml` line 557

```
NOTE: there used to be a `return,if=auto_combat.player` here. That
expression does not exist (it is player.auto_combat reversed), so it
never evaluated true and the line was dead — which is the only reason
the rotation worked. "Fixing" the spelling made it live, and since
player.auto_combat is a config-based check that reads true in normal
use, it aborted main before defensives/cooldowns/finishers: nothing
below this point ever fired. Removed entirely rather than re-spelled.
Do not add it back.
```

---

## - return,if=!target.valid|target.dead|!target.attackable

`FerrazFeral.yaml` line 569

```
"auto_combat.target" doesn't exist as an expression (confirmed against
expression-catalog.json) — reversed/invalid, same bug class as
auto_combat.player found elsewhere. This gate's clear intent is a
target-validity guard before the DPS lines below, matching the pattern
Balance/Guardian use ahead of their own damage lists.
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "2.12.0"

`FerrazFeral.yaml` line 1

```
=============================================================================
Feral Druid Ferraz M+ - spec 103 - patch 12.1.
=============================================================================

Lists (entry point: main):
  engine                  defensives              cooldown                finisher
  aoe_finisher            builder                 aoe_builder             heal_support
  form                    interrupts              predatory_swiftness     main

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/Feral.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.
=============================================================================
```

---

### druid_shapeshift_root: player.debuff.root.up|player.debuff.snare.up

`FerrazFeral.yaml` line 295

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

## Frenzied Regeneration added to the bear panic — 2026-09-01

```yaml
- bear_form,name="Panic Bear Form",...&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up)
- heart_of_the_wild,range_check=none,if=buff.bear_form.up&player.combat
- frenzied_regeneration,range_check=none,if=buff.bear_form.up&player.combat
```

The talent is on this build - verified by execution probe against the shipped
talent string, `talent.frenzied_regeneration` reads true - and the rotation
never cast it. The bear shift was already being paid for; the heal was not
being collected.

Placed after Heart of the Wild deliberately. HotW in Bear Form resolves to the
max-health morph (1261872, "Maximum health increased by X%"), so casting it
first means Frenzied Regeneration heals against the larger pool. Same ordering
the Balance file used while it had a bear defensive.

The condition is the same one the HotW line already carries, exactly as
requested: `buff.bear_form.up&player.combat`, with no health check of its own.

### The consequence of that condition

`Shapeshift Clear` also puts you in Bear Form - it is the root cleanse, and it
fires at any health. So both this line and the HotW line above it will fire
after a root break at full HP, spending a Frenzied Regeneration charge on
nothing.

That flaw already existed for HotW; this adds a second button to it rather than
introducing it. The narrow fix is a health gate on both lines, e.g.
`&health.pct<=config.panic_bear_hp_pct`, which is not what was asked for here
and is left as a decision rather than made silently.

### Still gated on Heart of the Wild being available

`Panic Bear Form` requires `cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up`,
so with HotW on cooldown the Feral never enters Bear at all and neither of
these lines can run - including the new heal, in exactly the windows where the
cooldown situation is worst. Loosening that gate was offered and not taken;
the bear shift still has to buy HotW to justify losing the Cat rotation.

### Follow-ups the same day

**The bear shift now fires for either payoff.** It was gated on Heart of the
Wild alone, so with HotW on cooldown the Feral never entered Bear and the new
heal could not run in the windows where cooldowns are scarcest:

```yaml
&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up|cooldown.frenzied_regeneration.ready&buff.frenzied_regeneration.down)
```

The Frenzied Regeneration leg carries `buff.frenzied_regeneration.down` so a
shift is never paid for to reapply a HoT already ticking.

**Both payoffs are now gated on the panic threshold.**

```yaml
- heart_of_the_wild,...&player.combat&health.pct<=config.panic_bear_hp_pct
- frenzied_regeneration,...&player.combat&health.pct<=config.panic_bear_hp_pct&buff.frenzied_regeneration.down
```

`Shapeshift Clear` puts you in Bear Form at any health to break a root. Without
this gate both buttons fired on the way out of a root at full health, spending
a cooldown on nothing. The bug predates the Frenzied Regeneration line — HotW
had it alone — and is fixed for both here.

`buff.frenzied_regeneration.down` on the cast: one charge, 36s recharge, and
the HoT only lasts 3s, so without the guard the line recasts over its own tick
and throws the recharge away.

The threshold is reused rather than given its own slider. It already means
"health low enough that losing the Cat rotation is worth it", which is exactly
the question both lines are asking.
