# FeralRaid — rationale
Every technical comment that used to live in `FerrazFeralRaid.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "1.8.0"

`FerrazFeralRaid.yaml` line 1

```
=============================================================================
Feral Druid — spec 103 — patch 12.1 (Midnight) — Wildstalker, RAID.
=============================================================================

Measured with SimC 1210-01, fight_style=Patchwerk (the raid proxy, unlike
the M+ file which uses DungeonSlice), against the recommended string.
Harness: sim/ab_test_feral_raid.py, profile sim/Ferraz_feral_raid.simc
(gear: SimC's own MID1 Feral preset). Baseline for comparison is SimC's own
default APL for this build, sourced from dreamgrove.

THIS IS NOT THE M+ FILE WITH A DIFFERENT STRING. The raid build drops
Frantic Frenzy, Primal Wrath, Apex Predator's Craving, Rampant Ferocity and
Double-Clawed Rake, and picks up Panther's Guile, Saber Jaws, Focused
Frenzy, Coiled to Spring, Tireless Energy, Lunar Inspiration, Infected
Wounds and Circle of Life and Death.

HERO TREE HISTORY: this file was Druid of the Claw until 1.1, when the raid
build moved to WILDSTALKER — the mirror of what the M+ file did at the same
time, in the opposite direction. Two of the three gains the 1.0 header
advertised died with that move, and the priority needed no edit for it:
every affected line is gated on a talent or on hero_tree.*, so they went
inert on their own. Re-measured on the Wildstalker string against the same
baseline (Patchwerk, rip_tf pinned to 1):

  Ferocious Bite pooled to full energy    +2.50%   still live (Saber Jaws)
  Lunar Inspiration Moonfire line         +1.78%   NEW: LI was untalented
                                                   on Druid of the Claw
  Convoke outside Berserk                 +0.04%   dead: no Ashamane's
                                                   Guidance on this string
  Shred on a Sudden Ambush proc           -0.03%   dead: gated on
                                                   hero_tree.druid_of_the_claw

The two dead lines are kept, gated as they are, so a respec back to Druid
of the Claw revives them without an edit.

Dropping the cooldown block entirely measures -21.47%, so the same
missing-cooldowns bug the M+ file had would cost even more here.

TESTED AND REJECTED: simplifying the Rip condition (removing its two
Tiger's Fury re-snapshot clauses) appeared to be worth +23.7%, but that was
an artifact of the harness pinning var.rip_tf to 0 — with it pinned to 1,
the way the game actually behaves once Rip is applied under Tiger's Fury,
the current condition and the simplified one land within the error bar of
each other. The clauses stay.

NOT validated (SimC models none of it): every defensive, Regrowth healing,
and the Predatory Swiftness lines.
=============================================================================
```

---

## about:

`FerrazFeralRaid.yaml` line 60

```
Display-only build stamp — keep in sync with version:/patch: above.
```

---

## panic_bear_hp_pct:

`FerrazFeralRaid.yaml` line 73

```
The panic Bear Form shift had a literal 25 and no name=, the only threshold
in either Feral file that was not a slider and the only defensive that did
not show up in the execution log when it fired.
```

---

## predatory_swiftness_heal_hp_pct:

`FerrazFeralRaid.yaml` line 109

```
Raid default is lower than the M+ file's: in a raid you are rarely the one
who has to top yourself, and a Regrowth is a lost finisher.
```

---

## use_trinket_1:

`FerrazFeralRaid.yaml` line 135

```
=== COOLDOWN CONFIGURATIONS ===
Defaults ON: dropping the whole cooldown block measures -21.47% here.
```

---

## engine_loot_nearby:

`FerrazFeralRaid.yaml` line 155

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

`FerrazFeralRaid.yaml` line 251

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

## engine:

`FerrazFeralRaid.yaml` line 279

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

`FerrazFeralRaid.yaml` line 288

```
`&`, not `|`. With `|` the condition is true whenever you are not doing at
least ONE of the two things — and you are almost never casting AND
channelling at once, so it read true on essentially every pass. The queue
is meant to flush only when you are genuinely free.
```

---

## - attack_target,off_gcd=true,delay=100,if=player.combat&target.exists&target.attackable&target.alive&target.in_melee&!player.auto_attacking

`FerrazFeralRaid.yaml` line 303

```
Melee-only, and this file IS melee: keeps auto-attack running.
target.in_melee, not target.range<=8: SIMIA_DOCUMENTATION rule 7 — range is
EDGE distance, so 'max melee' reads 4.5 on a small mob and 2.33 on a
9-reach boss. The shared list used the constant; this does not.
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazFeralRaid.yaml` line 312

```
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## - target_enemy,delay=200,off_gcd=true,if=config.engine_auto_target.has(0)&!target.exists&enemies.combat.8y>=1

`FerrazFeralRaid.yaml` line 324

```
Melee auto target: 8y, matching the shared melee list.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazFeralRaid.yaml` line 329

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

## - feral_frenzy,if=!talent.frantic_frenzy&combo_points<=2+(2*var.bs_inc)

`FerrazFeralRaid.yaml` line 370

```
Frantic Frenzy is NOT on the raid string, so the first line is the live
one here and the second is inert. Both kept so the file survives a
respec either way.
```

---

## - convoke_the_spirits,if=(var.bs_inc|talent.ashamanes_guidance&(var.bs_inc_cd_remains>45|var.holdBerserk))&buff.tigers_fury.up&(prev_gcd.1.rip|prev_gcd.1.ferocious_bite|prev_gcd.1.primal_wrath|buff.tigers_fury.remains<=1+action.convoke_the_spirits.execute_time)

`FerrazFeralRaid.yaml` line 375

```
The talent.ashamanes_guidance clause fires Convoke OUTSIDE the Berserk
window when Berserk is far away. It was worth +5.19% while the raid
build carried Ashamane's Guidance; the Wildstalker string does not, so
the clause is inert (re-measured: +0.04%, noise). Kept for a respec.
```

---

## - return,if=combo_points>=5&energy<50

`FerrazFeralRaid.yaml` line 383

```
RAID-SPECIFIC (+2.50% on the Wildstalker string, +2.87% on the old Druid
of the Claw one): Ferocious Bite spends up to 25 extra energy for up to
100% extra damage, and Saber Jaws — which both raid builds carry — raises
that payoff further, so it is pooled to the full 50-energy cost instead
of being fired at the 25-energy floor. This `return` is the pooling gate.
```

---

## - primal_wrath,name="Primal Wrath (Refresh)",if=combo_points>=5&enemies.combat.8y>1&(dot.rip.remains<6.5&!var.bs_inc|dot.rip.refreshable)

`FerrazFeralRaid.yaml` line 393

```
Primal Wrath and Rampant Ferocity are NOT on the raid string, so the
lines gated on them are inert and the Rip/Bite fallbacks are the live
path. Kept so the list still works on an AoE respec.
```

---

## - shred,name="Shred (Sudden Ambush)",if=buff.sudden_ambush.up&hero_tree.druid_of_the_claw

`FerrazFeralRaid.yaml` line 408

```
dreamgrove keeps a Druid-of-the-Claw-only Shred on a Sudden Ambush proc,
ahead of the Rake refresh. Worth +2.35% while this file was Druid of the
Claw; inert on Wildstalker (re-measured: -0.03%). Kept for a respec.
```

---

## - moonfire,if=talent.lunar_inspiration&(buff.tigers_fury.up|dot.moonfire.remains<cooldown.tigers_fury.remains)&(dot.moonfire.refreshable&(buff.tigers_fury.up|!var.moonfire_tf)|dot.moonfire.remains<2|buff.tigers_fury.up&!var.moonfire_tf)

`FerrazFeralRaid.yaml` line 413

```
Lunar Inspiration, live for the first time on the Wildstalker string:
worth +1.78% over the plain `refreshable` version below it. The extra
clauses re-snapshot Moonfire under Tiger's Fury, same shape as the Rake
and Rip lines.
```

---

## - shred,if=combo_points<=1&enemies.combat.8y=2&talent.panthers_guile

`FerrazFeralRaid.yaml` line 427

```
Panther's Guile IS on the raid string, so this line is live here.
```

---

## heal_support:

`FerrazFeralRaid.yaml` line 431

```
Mark of the Wild, OOC Regrowth top-off.
```

---

## form:

`FerrazFeralRaid.yaml` line 436

```
Emergency Bear Form, Fluid Form auto-shift, manual Cat Form entry, and
the pre-pull Prowl opener. Heart of the Wild is NOT on the raid string,
so that line is inert here.
```

---

## - bear_form,name="Panic Bear Form",range_check=none,if=health.pct<=config.panic_bear_hp_pct&!buff.bear_form.up&player.combat&(cooldown.heart_of_the_wild.ready|buff.heart_of_the_wild.up)

`FerrazFeralRaid.yaml` line 440

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

`FerrazFeralRaid.yaml` line 457

```
Prowl cannot be cast in combat — pre-pull opener only. See the M+ file
for the full note on why this needs an explicit !player.combat.
```

---

## predatory_swiftness:

`FerrazFeralRaid.yaml` line 468

```
Regrowth off a Predatory Swiftness proc. Called after `defensives` so a
real defensive cooldown outranks a proc heal.
```

---

## - return,if=player.channeling|player.casting|var.protected_channel

`FerrazFeralRaid.yaml` line 474

```
Convoke is a channel and nothing here ever wants to break it. Bare
player.channeling, the shape every official rotation in simia_data_dump
uses — see FerrazRestoDruid.yaml, where a narrower id-based guard failed
open often enough to clip Convoke in a real key.
```

---

## - return,if=!player.combat

`FerrazFeralRaid.yaml` line 485

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

`FerrazFeralRaid.yaml` line 498

```
NOTE: do NOT add a `return,if=player.auto_combat` here. It is a
config-based auto-combat-driver check, not combat state, and it aborts
the whole rotation before defensives and damage. See the M+ file.
```

---

## - ferocious_bite,if=buff.apex_predators_craving.up

`FerrazFeralRaid.yaml` line 516

```
Apex Predator's Craving is NOT on the raid string — these two are inert
here, kept so a respec back to the M+ build still works.
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "1.11.0"

`FerrazFeralRaid.yaml` line 1

```
=============================================================================
Feral Druid Ferraz Raid - spec 103 - patch 12.1.
=============================================================================

Lists (entry point: main):
  engine                  defensives              cooldown                finisher
  aoe_finisher            builder                 aoe_builder             heal_support
  form                    interrupts              predatory_swiftness     main

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/FeralRaid.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.
=============================================================================
```

---

### druid_shapeshift_root: player.debuff.root.up|player.debuff.snare.up

`FerrazFeralRaid.yaml` line 249

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
