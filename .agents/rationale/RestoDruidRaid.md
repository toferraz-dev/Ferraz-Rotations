# RestoDruidRaid — rationale
Every technical comment that used to live in `FerrazRestoDruidRaid.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "1.12.0"

`FerrazRestoDruidRaid.yaml` line 1

```
=============================================================================
Restoration Druid — spec 105 — patch 12.1 (Midnight) — Wildstalker, raid.
=============================================================================

LISTS
  main              entry point: plumbing -> defensives -> cooldowns ->
                    active healing -> DPS weaving.
  out_of_combat     Mark of the Wild + post-combat cleanup on genuine HP
                    need only.
  defensives        Ironbark -> Barkskin -> Bear Form + Frenzied Regen.
  racials           Shadowmeld, Thorn Bloom.
  utility           Root cleanse, Innervate.
  cooldowns         NS -> trinkets/potion -> Convoke -> Tranquility ->
                    Swiftmend -> Clearcasting Regrowth.
  mouseover_healing_emergency   unit-frame mouseover heals.
  moving            instant-only priority while moving.
  active_healing    SotF consumption -> self Efflorescence/Lifebloom/Rejuv
                    loop -> tank Lifebloom fallback -> forced spread ->
                    Abundance Regrowth -> Wild Growth/Rejuv/Germ/Regrowth.
  ranged_dps / catweave* / bearweave   DPS weaving, secondary to healing.

NOT SimC-validated: SimC has no raid-damage/incoming-heal model, so this
priority is manual raid-healer theorycraft, not benchmarked numbers. Tune
thresholds to your own team.

The self Efflorescence/Lifebloom/Swiftmend/Rejuvenation loop (current
class-guide's recommended playstyle) was checked against the decoded
talent string via the local SimC binary (sim/tools/simc-.../simc.exe,
talents= profile field), not guessed. Everbloom is maxed at 4/4.

talent.X gates confirmed on the string: germination, heart_of_the_wild,
efflorescence, everbloom, photosynthesis, power_of_the_archdruid.
fluid_form/swipe are checked but NOT on this
string — harmless dead weight unless the build changes.
=============================================================================
```

---

## config:

`FerrazRestoDruidRaid.yaml` line 46

```
=============================================================================
CONFIG — thresholds below are untested defaults, tune to your team.
=============================================================================
```

---

## about:

`FerrazRestoDruidRaid.yaml` line 51

```
Display-only build stamp — keep in sync with version:/patch: above.
```

---

## recommended_talents:

`FerrazRestoDruidRaid.yaml` line 58

```
String the talent.X checks below assume.
```

---

## raid_barkskin_threshold:

`FerrazRestoDruidRaid.yaml` line 65

```
=== DEFENSIVE CONFIGURATIONS ===
```

---

## raid_convoke_threshold:

`FerrazRestoDruidRaid.yaml` line 101

```
=== COOLDOWN CONFIGURATIONS ===
```

---

## raid_use_mouseover:

`FerrazRestoDruidRaid.yaml` line 140

```
=== AOE / GROUP HEALING CONFIGURATIONS ===
```

---

## raid_cancel_overheal_pct:

`FerrazRestoDruidRaid.yaml` line 155

```
Cancels a heal mid-cast if the target got topped off by someone else.
```

---

## raid_lifebloom_threshold:

`FerrazRestoDruidRaid.yaml` line 180

```
=== SINGLE TARGET (ST) HEALING CONFIGURATIONS ===
```

---

## raid_catweave_group_hp:

`FerrazRestoDruidRaid.yaml` line 213

```
=== DAMAGE & CATWEAVING CONFIGURATIONS ===
```

---

## raid_innervate_threshold:

`FerrazRestoDruidRaid.yaml` line 256

```
=== UTILITY CONFIGURATIONS ===
Season 2: flat 25% mana restore, so use early and often (guide: ~75%).
```

---

## raid_thorn_bloom_threshold:

`FerrazRestoDruidRaid.yaml` line 266

```
=== RACIAL CONFIGURATIONS ===
```

---

## raid_use_trinket_1:

`FerrazRestoDruidRaid.yaml` line 283

```
=== TRINKET & CONSUMABLE CONFIGURATIONS ===
```

---

## engine_loot_nearby:

`FerrazRestoDruidRaid.yaml` line 315

```
=== ENGINE & DISPEL CONFIGURATIONS ===
Inlined from Simia's _shared.yaml instead of inherited. `sanity_checks` is
not just guards: it also calls auto_dispel, affix, auto_purge_enrage,
auto_brez, auto_rez and auto_combat_potion. Two consequences here:
  - Nature's Cure was already firing on the raid with no line in this file
    and no way to tune it;
  - auto_combat_potion fought this file's own combat_potion line.
UNVALIDATED, like everything else in this file: SimC has no healing model.
```

---

## auto_dispel_group:

`FerrazRestoDruidRaid.yaml` line 379

```
Nature's Cure removes MAGIC, curse and poison — the healer dispel, far more
valuable than the DPS one. Defaults ON for the party/raid, unlike the DPS
files, because dispelling IS your job here.
```

---

## variables:

`FerrazRestoDruidRaid.yaml` line 408

```
=============================================================================
VARIABLES
=============================================================================
```

---

## protected_channel: player.casting.spell_id=740|player.casting.spell_id=323764|player.casting.spell_id=391528

`FerrazRestoDruidRaid.yaml` line 413

```
The channelled ids this spec can actually produce, confirmed against client
69404: Tranquility is 740 and Convoke is 323764 (Night Fae) and 391528
(talent), all three flagged "Is Channelled". Tranquility's 157982 and
1236573 are heal components, not the channel, so they are left out.

Written WITHOUT a leading player.channeling& on purpose. With it, the term
is a strict subset of the player.channeling already in the guard and
contributes nothing. Standing alone it covers the case the guard was
missing: the addon reporting Convoke through UnitCastingInfo before it
flips to UnitChannelInfo, which is the window a channel gets clipped in.
```

---

## lists:

`FerrazRestoDruidRaid.yaml` line 429

```
=============================================================================
LISTS
=============================================================================
```

---

## engine:

`FerrazRestoDruidRaid.yaml` line 434

```
Everything spell_queue / sanity_checks / auto_target / auto_heal used to do,
inlined so each piece is configurable. The five return guards are copied
verbatim — dropping any of them lets the rotation fire while dead or mounted.
Not copied (nothing a Druid can use): anti_cc, auto_freedom, auto_feign_death,
auto_death_grip, special_actions_combat (melee auto-attack), and
auto_combat_potion (this file drives its own potion, tied to Nature's
Swiftness).
```

---

## - queue_spell,if=!player.casting&!player.channeling

`FerrazRestoDruidRaid.yaml` line 442

```
`&`, not `|`. With `|` the condition is true whenever you are not doing at
least ONE of the two things — and you are almost never casting AND
channelling at once, so it read true on essentially every pass. The queue
is meant to flush only when you are genuinely free.
```

---

## - natures_cure,delay=500,cycle=members,name="Nature's Cure",if=config.auto_dispel_group&cycle.dispelable.list

`FerrazRestoDruidRaid.yaml` line 458

```
Nature's Cure: cycle=members (the healer form), not cycle=party.
```

---

## - target_enemy,delay=200,off_gcd=true,if=player.combat&config.engine_auto_target.has(0)&!target.exists&enemies.combat.40y>=1

`FerrazRestoDruidRaid.yaml` line 470

```
player.combat on all three. As a healer you are constantly OUT of combat
while the group is IN it, and you do not target enemies — so
`!target.exists & enemies.combat.40y>=1` was satisfied on essentially
every pass between pulls and this fired every 200ms forever.

It never resolved itself because the two halves measure different things:
enemies.combat.40y is a nameplate count, but WoW's TargetNearestEnemy
only picks up enemies in front of you. The count says an enemy exists,
the targeting call cannot reach it, and the condition stays true. With
off_gcd=true that is a visible suggestion spamming out of combat.

Nothing is lost by gating it: the only thing in this file that wants an
enemy target is the damage half, and that already requires
var.can_catweave, which is group_healthy AND player.combat.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazRestoDruidRaid.yaml` line 488

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

## interrupts:

`FerrazRestoDruidRaid.yaml` line 513

```
Soothe (enrage purge) + AoE CC assist.
```

---

## - target_enemy,delay=100,name="Search Interrupt",if=!interrupt.target.check&interrupt.8y.any

`FerrazRestoDruidRaid.yaml` line 515

```
REMOVED: a `target_enemy,if=...&enemies.combat.any(cycle.purgeable.enrage)`
search line. No predicate form `.any(EXPR)` exists for enemies — the only
predicate helper in the catalog is group.count(EXPR), and that iterates
ALLIES. The condition never evaluated true, so the line was dead and
Soothe below only ever fired when you were already on the enraged mob.
Simia cannot pick an enemy by criteria (target_enemy is 'nearest enemy',
no filter), so this is not fixable — target the mob yourself.
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazRestoDruidRaid.yaml` line 524

```
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## out_of_combat:

`FerrazRestoDruidRaid.yaml` line 529

```
Mark of the Wild, plus post-combat
cleanup on genuine HP need — (player.inraid|player.indungeon) avoids
misreading a phantom "member" when solo/ungrouped.
```

---

## - mark_of_the_wild,name="Mark of the Wild",range_check=none,if=config.raid_use_mark_of_the_wild&(buff.mark_of_the_wild.down.any|action.mark_of_the_wild.overlayed)&lastcast.mark_of_the_wild>=10

`FerrazRestoDruidRaid.yaml` line 533

```
config.raid_use_mark_of_the_wild was defined but no line read it, so the
checkbox did nothing at all. Wired up here.
```

---

## - lifebloom,name="OOC Lifebloom",cycle=members,if=(player.inraid|player.indungeon)&!talent.everbloom&cycle.health.effective.pct<config.raid_lifebloom_threshold&cycle.buff.lifebloom.down&(group.count(cycle.buff.lifebloom.up)=0|tank1.buff.lifebloom.up|tank2.buff.lifebloom.up)&!player.combat

`FerrazRestoDruidRaid.yaml` line 536

```
NO Symbiotic Relationship. Removed at request for the raid file; the
M+ file keeps it. Nothing else here reads the bond, so the config
raid_symbiotic_target went with it.
```

---

## defensives:

`FerrazRestoDruidRaid.yaml` line 545

```
Ironbark -> Barkskin -> Bear Form + Frenzied Regen.
```

---

## racials:

`FerrazRestoDruidRaid.yaml` line 553

```
Shadowmeld aggro drop, Thorn Bloom group heal.
```

---

## cooldowns:

`FerrazRestoDruidRaid.yaml` line 558

```
NS -> trinkets/potion -> Convoke (needs Abundance up, caster form) -> NS
Regrowth -> Tranquility -> self Swiftmend (Archdruid) -> reactive
Swiftmend -> Clearcasting Regrowth.
```

---

## - rejuvenation,name="Shift Out For Convoke",cycle=members,if=cooldown.convoke_the_spirits.ready&group.count(cycle.health.effective.pct<config.raid_convoke_threshold)>=config.raid_convoke_members&(buff.cat_form.up|buff.bear_form.up)

`FerrazRestoDruidRaid.yaml` line 562

```
CONVOKE IS FORM-DEPENDENT. In Cat Form it deals damage; only in caster
form does it heal. So the healing chain has to get you out of the form
FIRST — any heal does that on its own, which is what this line is for.
Without it the chain dead-ends: Nature's Swiftness fires, then
"Convoke (Heal)" below refuses because of its !cat_form gate, and the NS
is burned for nothing.
```

---

## - swiftmend.player,name="Self Swiftmend (Archdruid)",range_check=none,if=talent.power_of_the_archdruid&player.combat&cooldown.swiftmend.ready&(buff.rejuvenation.up|buff.regrowth.up|buff.wild_growth.up)

`FerrazRestoDruidRaid.yaml` line 576

```
Power of the Archdruid loop: Swiftmend on CD, spreads Rejuv to 3 targets.
```

---

## - regrowth,name="Clearcasting Regrowth",cycle=members,if=player.combat&buff.clearcasting.up&cycle.health.effective.pct<99

`FerrazRestoDruidRaid.yaml` line 579

```
NO `|pred.cycle.buff.regrowth.down` branch. That half carried no health
gate at all, so a tank at 100% with no Regrowth HoT satisfied the line on
its own — and in the M+ file, which had no player.combat either, that
made it the ONE Regrowth reachable out of combat that fires on a full
target. Omen of Clarity procs Clearcasting by itself, so between pulls
the proc sat there, this line saw a tank without the HoT, and spent it
into pure overheal.
Spending a free proc early is still the intent; `<99` keeps it, and
player.combat keeps it from burning during downtime.
```

---

## active_healing:

`FerrazRestoDruidRaid.yaml` line 590

```
SotF consumption -> self Efflorescence/Lifebloom(Everbloom)/Rejuvenation
(Photosynthesis) loop -> tank Lifebloom fallback -> forced spread ->
Abundance Regrowth -> Wild Growth/Rejuv/Germination/Regrowth.
```

---

## - rejuvenation.player,name="Emergency Self Rejuvenation",range_check=none,if=buff.rejuvenation.down&health.effective.pct<config.raid_rejuvenation_threshold

`FerrazRestoDruidRaid.yaml` line 594

```
Self-target fallback (bare health, not cycle.*) so solo content still
gets reactive healing. Runs first so it's never starved.
```

---

## - efflorescence,name="Efflorescence (Self)",range_check=none,if=talent.efflorescence&cooldown.efflorescence.ready

`FerrazRestoDruidRaid.yaml` line 606

```
Everbloom self loop: auto-stacks to 3, cleaves 40% to 6 allies. Falls
through to tank Lifebloom below if untalented.
```

---

## - lifebloom.player,name="Self Lifebloom (Everbloom)",range_check=none,after=300,if=talent.everbloom&(buff.lifebloom.down|buff.lifebloom.remains<4.5)

`FerrazRestoDruidRaid.yaml` line 609

```
after=300 debounces Everbloom's own restack tick; remains<4.5 refreshes
before falling off so it keeps its built-up stacks.
```

---

## - lifebloom,name="Lifebloom",cycle=members,if=!talent.everbloom&cycle.health.effective.pct<config.raid_lifebloom_threshold&cycle.buff.lifebloom.down&(group.count(cycle.buff.lifebloom.up)=0|tank1.buff.lifebloom.up|tank2.buff.lifebloom.up)

`FerrazRestoDruidRaid.yaml` line 614

```
Tank Lifebloom only when untalented — with Everbloom, the self line
above owns the single charge; fighting it over it ping-pongs forever.
```

---

## - regrowth,name="Abundance Regrowth",cycle=members,if=buff.abundance.up&cycle.health.effective.pct<config.raid_regrowth_threshold

`FerrazRestoDruidRaid.yaml` line 623

```
Abundance window: cheap/crit Regrowth, spend before Wild Growth.
```

---

## utility:

`FerrazRestoDruidRaid.yaml` line 631

```
Root cleanse (Bear/Cat shift), Innervate.
```

---

## - innervate.player,name="Innervate",off_gcd=true,ignore_queue=true,range_check=none,if=mana.pct<config.raid_innervate_threshold

`FerrazRestoDruidRaid.yaml` line 635

```
innervate.player, not bare innervate. Without an explicit cast target the
addon needs a target to fire it and simply does nothing when you have
none — which is most of the time between pulls, exactly when you want the
mana back. As a healer you innervate YOURSELF anyway (Season 2 made it a
flat 25% mana restore), so pinning the target loses nothing.
range_check=none for the same reason: it is a self-cast, so there is no
range to check.
```

---

## catweave_st:

`FerrazRestoDruidRaid.yaml` line 644

```
Cat Form single-target DPS.
```

---

## catweave_aoe:

`FerrazRestoDruidRaid.yaml` line 652

```
Cat Form AoE DPS.
```

---

## catweave:

`FerrazRestoDruidRaid.yaml` line 662

```
Entry into physical DPS (Fluid Form auto-shift or manual), then hands off
to catweave_st/catweave_aoe.
```

---

## ranged_dps:

`FerrazRestoDruidRaid.yaml` line 673

```
Ranged DoT maintenance in caster form while group is healthy.
```

---

## bearweave:

`FerrazRestoDruidRaid.yaml` line 681

```
Bear Form bleed maintenance before handing off to catweave.
```

---

## moving:

`FerrazRestoDruidRaid.yaml` line 687

```
Convoke if ready and safe, otherwise instant HoTs only.
```

---

## - rejuvenation,name="Rejuvenation (Moving)",cycle=members,if=cycle.buff.rejuvenation.down&cycle.health.effective.pct<config.raid_rejuvenation_threshold

`FerrazRestoDruidRaid.yaml` line 694

```
config.raid_rejuvenation_threshold, not a literal 95. The stationary
Rejuvenation lines already read the slider; this one did not, so moving
was silently stricter than standing and the slider could not reach it.
```

---

## mouseover_healing_emergency:

`FerrazRestoDruidRaid.yaml` line 699

```
Unit-frame mouseover heals, HP-gated from main. No mouseover.buff.*
expression exists, so usability is left to the engine's own check.
```

---

## main:

`FerrazRestoDruidRaid.yaml` line 707

```
Entry point. First matching line wins the GCD: defensives -> cooldowns ->
emergency -> active healing outrank DPS weaving.
```

---

## - return,if=player.channeling|player.casting|var.protected_channel

`FerrazRestoDruidRaid.yaml` line 710

```
`player.channeling`, bare. This is what every official rotation in
simia_data_dump uses, and the compound guard it replaces had two ways to
fail open:

  1. Both spell_id clauses need player.casting.spell_id populated during
     a CHANNEL. In the WoW API that is UnitChannelInfo, a different call
     from UnitCastingInfo; if the addon reads only the latter the field
     is empty mid-channel and both clauses go false together.
  2. buff.convoke_the_spirits.up resolves by NAME — the exact pattern
     that silently never matched for Symbiotic Relationship.

  The raid file was narrower still: it listed 323764 but not 391528, so
  on the talent version of Convoke its id check could never match.

That combination explains a channel that is protected MOST of the time
and occasionally clipped: only one clause was really working, and it
depended on when the client registered the channel. Heavy healing is
when a hardcast is always queued behind, so that is when the gap shows —
Nature's Swiftness fires off-GCD (harmless), then "Nature Swift Regrowth"
becomes the suggestion and clips Convoke.

Nothing in this file uses interrupt=true, so no line ever wants to break
its own channel. The narrow guard bought nothing.

`|player.casting` added on 4.5.4 / 1.9.4. Both Balance files have guarded
cast AND channel since they were written; the two Resto files guarded
only the channel, and that is the one asymmetry left after the bare
guard went in.

It matters because UnitCastingInfo and UnitChannelInfo are separate API
calls. If the addon reports Convoke or Tranquility as a CAST at any
instant — on the wind-up, before it flips to a channel — then
player.channeling is false and player.casting is true, and the channel
sits unprotected for exactly that window. This closes it.

Free to add: nothing in either file uses interrupt=true, so no line ever
wants to act during your own cast either.

NOT the fix suggested on the Simia forum, and worth writing down why.
That advice was `return,if=player.channeling&!var.sm_channeling` with
`sm_channeling: player.channeling&player.casting.spell_id=115175`. 115175
is Soothing Mist — that clause is a Mistweaver EXCEPTION, a way to keep
acting through one's own channel. It loosens the guard. This file already
had the strict half of that advice since 4929112.
```

---

## - call_action_list,name=engine

`FerrazRestoDruidRaid.yaml` line 756

```
--- Engine plumbing. Must stay at the top. ---
```

---

## - stop_casting,name="Cancel Overheal",casting_check=any,if=casting_target.health.pct>=config.raid_cancel_overheal_pct

`FerrazRestoDruidRaid.yaml` line 760

```
NOTE: a `return,if=!player.auto_combat` used to sit here. Despite the
name, player.auto_combat is NOT "am I in combat" — the catalog defines
it as a config-based auto-combat-driver check, which reads false in
normal play. Negated, that made this abort main on every pass and
nothing below ever fired. Use player.combat for combat state. Removed.

Cancels a heal mid-cast if the target got topped off by another source.
```

---

## - call_action_list,name=interrupts

`FerrazRestoDruidRaid.yaml` line 769

```
--- Survival, then utility, then the healing cooldown window ---
```

---

## - call_action_list,name=ranged_dps,if=config.raid_ranged_dps&var.can_catweave&target.exists&target.alive&!target.friendly&((config.raid_melee_dps&!target.in_melee)|!config.raid_melee_dps)

`FerrazRestoDruidRaid.yaml` line 780

```
--- DPS weaving. Only while the group is topped and healthy. ---
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "1.16.0"

`FerrazRestoDruidRaid.yaml` line 1

```
=============================================================================
Restoration Druid Ferraz Raid - spec 105 - patch 12.1.
=============================================================================

Lists (entry point: main):
  engine                  interrupts              out_of_combat           defensives
  racials                 cooldowns               active_healing          utility
  catweave_st             catweave_aoe            catweave                ranged_dps
  bearweave               moving                  mouseover_healing_emergency  main

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/RestoDruidRaid.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.
=============================================================================
```

---

### druid_shapeshift_root: player.debuff.root.up|player.debuff.snare.up

`FerrazRestoDruidRaid.yaml` line 425

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
