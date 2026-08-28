# RestoDruid — rationale
Every technical comment that used to live in `FerrazRestoDruid.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "5.3.0"

`FerrazRestoDruid.yaml` line 1

```
=============================================================================
Restoration Druid — spec 105 — patch 12.1 (Midnight) — Wildstalker, M+.
=============================================================================

Build decoded through the local SimC binary. The pieces that shape the
priority: Everbloom 4/4, Efflorescence, LIFETREADING (Efflorescence follows
your Lifebloom target on its own), Photosynthesis, Power of the Archdruid,
Soul of the Forest, Germination, Abundance, Grove Guardians, Verdancy,
Intensity, Nature's Bounty, Omen of Clarity and Overgrowth (new in 12.1:
Nature's Swiftness makes the next Regrowth also apply Lifebloom, Rejuvenation
and Wild Growth to that target).
NOT talented: Cenarion Ward, Nourish, Verdant Infusion, Flourish, Incarnation:
Tree of Life, Flash of Clarity.

BUILD CHANGED on 2026-08-24 to the string a reference +15 druid ran (Kireya,
Murder Row). Against the previous string it trades:

  GAINED   Moonkin Form, Starfire, Sunfire, Ursine Vigor
  LOST     Innervate, Matted Fur, Swipe

Sunfire is the whole point: it is 29.3% of that druid's damage, the single
largest source, and the old build could not cast it at all. Three lines moved
with the build — ranged_dps gained Sunfire, catweave_aoe gates Swipe on the
talent, and Innervate gates on its own. None were deleted, so reverting the
string reverts the behaviour with no edit.

THE HEALING HALF IS NOT SimC-VALIDATED. SimC has no usable healing model, so
nothing here is measured the way the damage half is.

What it DOES have is three reference logs from the same dungeon (Murder Row,
27-30 min each): Crazyshiftz, Crohot and Kireya. Where all three agree, treat
it as a target. Where they disagree, it is a choice, not a rule.

                       Crazyshiftz    Crohot    Kireya
  Abundance uptime          86.8%      82.1%     58.2%
  Overheal                  62.7%      59.9%     48.6%
  HPS                     148,920    163,206   136,842
  DPS                       9,429     10,207    19,427
  damage casts                14%         5%       29%

THEY AGREE ON:

  ~20 Rejuvenation-family casts a minute. Rejuvenation + Germination runs
  24.1 / 20.4 / 16.0 per minute, and Abundance uptime tracks it exactly:
  82% / 87% / 58%. Five Rejuvenations at ~15s each needs ~20 applications a
  minute to stay saturated, so that is the line. This is why
  rejuvenation_threshold is 100 and must stay permissive.

  Swiftmend on cooldown. 4.5 / 3.7 / 3.9 per minute — the tightest agreement
  in the whole comparison.

  Wild Growth is rare. 2.0 / 3.0 / 2.5 per minute. A moment spell, not
  maintenance.

  ~60% OVERHEAL IS THE TARGET, NOT A DEFECT. The two highest-HPS players
  overheal MORE, not less. Overheal is what the Abundance engine costs, and
  trying to tune it down starves the buff and lowers HPS. Do not "fix" it.

THEY DISAGREE ON: how much damage to weave — 5%, 14% and 29% of casts, and
the one who weaves least has the highest HPS while the one who weaves most
has the highest DPS by double. See catweave_group_hp for the dial.

THE DAMAGE HALF IS. Harness sim/ab_test_resto_dps.py, profile
sim/Ferraz_resto_mplus.simc, 3 targets. Gear is SimC's MID1 Balance preset
(there is no Restoration one), so absolute DPS is meaningless and only the
deltas mean anything. The current weaving priority wins every comparison:

    current (bearweave -> catweave, HotW, Convoke)   38107 DPS
    without the Bear opener                          31964   -16.12%
    without Heart of the Wild                        35280    -7.42%
    without offensive Convoke                        35097    -7.90%
    caster only, never shifting                      20278   -46.79%
    AoE list at 2 targets instead of 3               37978    -0.34%
    AoE list at 4 targets                            38036    noise

So: the Bear opener earns its place, both cooldowns earn theirs, and the
3-target AoE threshold is already the right cut. Nothing in the damage half
needed changing.

Read those numbers as "which weaving shape does more damage", never as "this
heals better" — SimC never lets the group take damage, so it never charges
you for the globals a form swap costs.
=============================================================================
```

---

## about:

`FerrazRestoDruid.yaml` line 98

```
==========================================================================
BUILD STAMP — display only. Keep in sync with version:/patch: above.
==========================================================================
Display-only build stamp — keep in sync with version:/patch: above.
```

---

## recommended_talents:

`FerrazRestoDruid.yaml` line 108

```
==========================================================================
RECOMMENDED BUILD — the string the talent.X gates below assume.
==========================================================================
```

---

## use_mouseover:

`FerrazRestoDruid.yaml` line 117

```
==========================================================================
HEALING — the core thresholds. Every one of these is judgement:
  SimC has no healing model, so none of it is measured.
==========================================================================
```

---

## lifebloom_target:

`FerrazRestoDruid.yaml` line 135

```
Everbloom 4/4 + Lifetreading decide this, and 1.6 flips the default to the
tank on three independent grounds:
  - Lifetreading grows Efflorescence under the Lifebloom target. In a
    dungeon the melee cluster stands on the tank, so that is where a
    ground-anchored heal is worth the most.
  - Everbloom cleaves 40% of Lifebloom's healing to six allies, and it
    cleaves FROM the holder — again, better centred on the pile.
  - The reference M+ log keeps Lifebloom on one partner for 101 of 111
    applications, never on the caster.
method.gg's M+ page says tank; its general page says yourself. Set to Self
if you are the one taking the damage.
```

---

## ooc_heal_hp_pct:

`FerrazRestoDruid.yaml` line 157

```
Out-of-combat healing floor. The OOC lines used to run on the in-combat
thresholds, and rejuvenation_threshold defaults to 100 — so anyone at 99.9%
qualified and the rotation healed full-health people between pulls. Heal out
of combat only when somebody genuinely needs it.
```

---

## ooc_abundance:

`FerrazRestoDruid.yaml` line 170

```
Padding Abundance before a pull is real value, but the list has no natural
stopping point: Rejuvenation expires in ~15s, so out of combat it recasts
forever and drains mana while you stand still. OFF by default — turn it on
if you want a pre-pull ramp and are willing to pay for it.
```

---

## spell: 207640

`FerrazRestoDruid.yaml` line 178

```
207640 (the Abundance buff), not 207383 (the talent): the talent carries
"Do Not Display (Spellbook, Aura Icon, Combat Log)" in its spell data and
has no icon to render. 207640 is the one you actually see on your bar.
```

---

## wild_growth_threshold:

`FerrazRestoDruid.yaml` line 183

```
Lowered 95 -> 85. The reference log casts Wild Growth 2.5x/min and still
overheals 49.4% with it. At 95 effective — and effective ADDS incoming
heals, so it reads high while your HoTs roll — this fired far more often
than that, on people who were never in danger.
```

---

## natures_swiftness_threshold:

`FerrazRestoDruid.yaml` line 203

```
Measured against RAW health, not effective health — see the comment on the
Nature's Swiftness line. 70 raw is roughly where 60 effective was MEANT to
sit before incoming HoTs inflated it.
Also worth raising further: Overgrowth (new in 12.1) makes the NS Regrowth
apply Lifebloom, Rejuvenation and Wild Growth too, so NS is a ramp tool now
and not only a panic button. The reference M+ log fires it every 1.5 min,
near its 60s cooldown.
```

---

## regrowth_emergency_threshold:

`FerrazRestoDruid.yaml` line 218

```
Raised 50 -> 60 alongside restoring the Rejuvenation blanket to 100. With
the blanket back at full width this line is the real safety net — the one
thing above the HoT maintenance that reacts to someone genuinely dropping —
so it gets room rather than sitting at the floor.

Still RAW health, not effective. Effective adds incoming heals, so with
your HoTs rolling it reads high exactly when you need it to read low. 60
raw is roughly 80 effective on a covered target.
```

---

## rejuvenation_threshold:

`FerrazRestoDruid.yaml` line 250

```
REVERTED to 100 on 5.1.0, one version after lowering it. The reference +15
log says the blanket IS the Abundance engine and lowering this starves it.

Abundance needs 5 Rejuvenations up at once and Rejuvenation lasts ~15s, so
holding five people covered costs roughly 20 casts a minute. That druid
runs 16/min (263 Rejuvenation + 166 Germination in 26.9 min) and lands
58.2% Abundance uptime — 121 of his 176 Regrowths, 69%, go out inside the
window at -60% cost and +60% crit. He has no separate "build Abundance"
behaviour; the uptime is a by-product of blanketing hard.

5.0.0 dropped this to 90 on the argument that someone falling fast collected
Rejuvenation, then Germination, then finally a Regrowth. That argument was
wrong: "Regrowth Emergency" is the SECOND line of active_healing, above all
of this, on RAW health. Anyone actually dying is caught there. The case in
the example was a player at 60% real health, who is not dying and for whom
the instant blanket is the right answer.
```

---

## convoke_threshold:

`FerrazRestoDruid.yaml` line 274

```
==========================================================================
HEALING COOLDOWNS — Convoke, Tranquility and their gates.
==========================================================================
```

---

## barkskin_incoming_pct:

`FerrazRestoDruid.yaml` line 316

```
==========================================================================
DEFENSIVES — personal and Ironbark.
==========================================================================
The predicted-damage half of the defensives was hardcoded while the health
half had sliders, so tuning one left the other stuck. incoming.pct is the
biggest predicted incoming hit as a % of effective health — a different
question from "how hurt are they right now", which is why each defensive
reads both.
```

---

## auto_dispel:

`FerrazRestoDruid.yaml` line 377

```
==========================================================================
DISPELS — Nature's Cure removes MAGIC, curse and poison.
==========================================================================
Nature's Cure removes MAGIC, curse and poison. It had no toggle before —
the line was hardcoded into sanity_checks.
```

---

## catweave_group_hp:

`FerrazRestoDruid.yaml` line 401

```
Lowered 95 -> 85 off a reference +15 log (Kireya, Murder Row, 26.9 min).
var.group_healthy reads group.lowest — the MOST hurt member — so at 95
the gate needed the whole party essentially topped. In a real key that is
almost never true, so var.can_catweave stayed false all fight and the
weaving never opened. Every global went to healing, and since the healing
lines fire at <100 and <95 they always found somebody: a HoT treadmill
that casts constantly and fixes nothing.

The reference druid weaves 7.5 melee swings a minute and spends 29% of
his casts on damage. This file was spending 0%.
```

---

## melee_dps:

`FerrazRestoDruid.yaml` line 428

```
The file had NO way to stop weaving. On a fight where you must never leave
caster form, or while learning a key, these are the switches.
```

---

## stampeding_roar_usage:

`FerrazRestoDruid.yaml` line 448

```
==========================================================================
MOVEMENT — Stampeding Roar.
==========================================================================
```

---

## auto_prowl:

`FerrazRestoDruid.yaml` line 474

```
==========================================================================
UTILITY — Innervate, Symbiotic Relationship, HoT spread toggle.
==========================================================================
```

---

## thorn_bloom_threshold:

`FerrazRestoDruid.yaml` line 491

```
==========================================================================
RACIALS — Thorn Bloom is a heal, not damage.
==========================================================================
```

---

## use_trinket_1:

`FerrazRestoDruid.yaml` line 510

```
==========================================================================
TRINKETS & CONSUMABLES — tied to the Convoke window.
==========================================================================
```

---

## loot_nearby:

`FerrazRestoDruid.yaml` line 531

```
==========================================================================
ENGINE — plumbing this file owns instead of inheriting.
==========================================================================
Everything the file used to inherit. auto_heal and auto_target_ranged were
the last two shared lists; 5.2 inlines both, so this rotation now owns all
of its plumbing.
```

---

## mana_potion_pct:

`FerrazRestoDruid.yaml` line 579

```
A healer is the one spec that actually runs dry. The shared auto_heal list
has no mana potion line at all.
```

---

## discord_button:

`FerrazRestoDruid.yaml` line 589

```
==========================================================================
HELP
==========================================================================
```

---

## protected_channel: player.casting.spell_id=740|player.casting.spell_id=323764|player.casting.spell_id=391528

`FerrazRestoDruid.yaml` line 600

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

## group_healthy: group.lowest.health.effective.pct>=config.catweave_group_hp

`FerrazRestoDruid.yaml` line 611

```
True if the lowest health group member is healthy enough for Catweaving
```

---

## can_catweave: var.group_healthy&player.combat

`FerrazRestoDruid.yaml` line 613

```
Safe to enter Cat Form for DPS (group healthy and in combat)
```

---

## in_dps_form: buff.cat_form.up|buff.bear_form.up

`FerrazRestoDruid.yaml` line 615

```
Player is currently in a DPS form (Cat or Bear)
```

---

## mo_friendly_valid: mouseover.exists&mouseover.alive&mouseover.friendly&mouseover.unitframe

`FerrazRestoDruid.yaml` line 617

```
Friendly and valid mouseover target
```

---

## hotw_pending: config.use_heart_of_the_wild&talent.heart_of_the_wild&cooldown.heart_of_the_wild.ready

`FerrazRestoDruid.yaml` line 619

```
Heart of the Wild is ready and enabled. While this is true the bearweave
list yields, so the rotation goes straight to Cat Form and fires it.
```

---

## has_soul: buff.soul_of_the_forest.up

`FerrazRestoDruid.yaml` line 622

```
Soul of the Forest proc is active
```

---

## use_stampeding_roar: moving.time>=config.stampeding_roar_movement_time&buff.stampeding_roar.down&((config.stampeding_roar_usage=1&player.combat)|(config.stampeding_roar_usage=2&!player.combat)|(config.stampeding_roar_usage=3))

`FerrazRestoDruid.yaml` line 624

```
Stampeding Roar conditions based on the interface
```

---

## interrupts:

`FerrazRestoDruid.yaml` line 628

```
Interrupts and Dispel: Automatic Soothe and AoE CCs
```

---

## - soothe.mouseover,name="Soothe Enrage (Mouseover)",range_check=mouseover,if=config.soothe_mouseover&mouseover.exists&mouseover.enemy&mouseover.attackable&!mouseover.dead&mouseover.combat&mouseover.purgeable.enrage

`FerrazRestoDruid.yaml` line 631

```
REMOVED: a target_enemy "Search Soothe" line gated on
enemies.combat.any(cycle.purgeable.enrage). No predicate form `.any(EXPR)`
exists for enemies — group.count(EXPR) is the only one and it iterates
ALLIES. The line was dead, so Soothe below only fired when you already
had the enraged mob targeted. Not fixable: target_enemy is "nearest
enemy" with no filter.
Hovering is the only way to Soothe a mob you are not targeting — see
the soothe_mouseover config for why a search line is impossible.
```

---

## out_of_combat:

`FerrazRestoDruid.yaml` line 642

```
Out of Combat: Mark of the Wild, Symbiotic Relationship, and healing prep.

Every cycle= line here carries (player.inraid|player.indungeon). Without it
`cycle=members` reads a PHANTOM MEMBER while you are solo or ungrouped —
it reports 0% health, the threshold passes, and the rotation heals nobody
forever. FerrazRestoDruidRaid.yaml has carried this guard since the same
bug was reported there; this file never got it.
```

---

## - symbiotic_relationship,cycle=tanks,range_check=none,name="Symbiotic (Tank)",if=talent.symbiotic_relationship&cycle.buff.474750.down&buff.474754.down&lastcast.symbiotic_relationship>=60

`FerrazRestoDruid.yaml` line 651

```
Symbiotic Relationship. Out of combat only — the spell refuses to cast in
combat, which is why it must never appear in an in-combat list.

THE BOND PRODUCES NO TRACKABLE AURA. Checked against a 26-minute M+ log:
the bond heal (474760) fires on both partners 2935 times, and there is
NOT ONE applybuff event for Symbiotic on either of them. So
buff.symbiotic_relationship never registers, .down stays true forever,
and any condition built on it re-casts every pass. That is the "casting
it nonstop" bug, and it survived two attempts to fix it with buff gates.

The buff checks are kept in case they resolve in-game where the log shows
nothing, but lastcast is what actually bounds it: at worst the bond is
re-established once a minute, out of combat, which costs one global.

No target chooser: in a 5-man there is only ever tank1.
buff.474750, NOT buff.symbiotic_relationship. A snapshot settles it: the
player carries "[474750] (Symbiotic Relationship) mine=yes" for the full
hour, and in the very same trace the rotation evaluated
`buff.symbiotic_relationship.down = 1 [PASS]`. The name does not resolve
to that aura, so every condition built on it re-cast the bond on a target
that already had it.
474760, which 1.9 guessed at, is the bond HEAL — it fires thousands of
times a fight and is never an aura. Wrong id, and it read .down forever.
lastcast stays as the backstop in case the aura id changes again.
Two auras, one per side of the bond. A snapshot shows them together:
  [PLAYER]    474754 (Symbiotic Relationship) rem=3466.3 mine=no
  [PARTY[4]]  474750 (Symbiotic Relationship) rem=3466.2 mine=yes
474750 sits on the TANK and is applied by you. 474754 sits on YOU and is
applied by the tank. 3.4 claimed the player carried 474750 — that was a
misread of the same snapshot, and it is why the line kept re-casting.

`cycle.buff`, not `buff`. Bare `buff.X` reads the PLAYER's auras, but
this line cycles tanks, so it has to ask about the CYCLED unit. Every
other cycle= line in this file already uses the cycle. prefix; this one
was the lone exception.

buff.474754.down is the second half: you may only hold one bond, so if
you already carry the healer-side aura, do not bond a different tank.

474760, guessed at in 1.9, appears nowhere in any snapshot. The bond's
heal is 439530 (Symbiotic Blooms), an 8s aura that lands on the group.
```

---

## - lifebloom,name="OOC Lifebloom (Tank)",cycle=tanks,if=(player.inraid|player.indungeon)&(cycle.buff.lifebloom.down|cycle.buff.lifebloom.refreshable)

`FerrazRestoDruid.yaml` line 693

```
NO "cast Rejuvenation to leave the form" line, in or out of combat.
Any healing spell drops you out of Cat/Bear on its own — confirmed in
game on 12.1 — so the moment the
rotation decides someone needs healing, that heal is the shift. A cast
whose only purpose is changing form is mana for nothing.

The healing lists are already reachable from a DPS form: every one of
them is gated `!var.in_dps_form|!var.group_healthy`, so a hurt group
opens them while you are still in Cat.

History, so this does not come back: 2.5 gated the line on
!var.group_healthy, 3.0 loosened it to !var.can_catweave (always true out
of combat, so every shift cast a heal), 3.1 put it back and moved the
in-combat twin into main. 3.2 deletes both — the line never needed to
exist. Note the direction Fluid Form works: "Shred, Rake, and Skull Bash
can be used in any form and shift you INTO Cat Form". It covers entering,
not leaving; leaving is the base behaviour of casting a caster spell.
Pre-combat Lifebloom maintenance on tanks
```

---

## - call_action_list,name=abundance_maintenance,if=config.ooc_abundance

`FerrazRestoDruid.yaml` line 714

```
Abundance padding, now behind a toggle. This call had NO condition at
all: out of combat it re-cast Rejuvenation forever as the HoT expired,
which is the "burning mana for nothing while standing around" bug.
```

---

## - prowl,name="Auto Stealth",if=config.auto_prowl&!buff.prowl.up&!buff.travel_form.up&!buff.bear_form.up

`FerrazRestoDruid.yaml` line 718

```
Auto Stealth when all healing is done
```

---

## defensives:

`FerrazRestoDruid.yaml` line 721

```
Mitigations and Emergency Defensives: Ironbark on Tanks/Members -> Barkskin
-> Bear Form + Frenzied Regen.

Ironbark reads RAW health, not effective. Effective health adds the healing
already flying at the target, and Ironbark is damage REDUCTION — it does
not heal, so it has to land before those HoTs do, not after they have
already discounted the danger.
```

---

## racials:

`FerrazRestoDruid.yaml` line 735

```
Racial Abilities and Specific Mobility
```

---

## cooldowns:

`FerrazRestoDruid.yaml` line 744

```
Main Healing Cooldown Alignment: NS -> Trinkets/Potion -> Convoke -> NS Regrowth -> Tranquility -> Swiftmend
```

---

## - natures_swiftness,name="Nature Swiftness",off_gcd=true,ignore_queue=true,delay=150,range_check=none,if=group.count(cycle.health.pct<config.natures_swiftness_threshold)>=1

`FerrazRestoDruid.yaml` line 746

```
NO Mark of the Wild here. It used to be the first line of this list,
which runs in combat — so a missing buff outranked Nature's Swiftness,
Convoke, Tranquility and Swiftmend. It is allowed in combat, but it
belongs at the bottom: see the call in `main`, below active_healing.
NO Symbiotic Relationship line here. It used to sit in this list, which
runs IN COMBAT — and the spell can only be cast out of combat. The cast
failed, the bond buff never applied, the condition never cleared, and the
line took the GCD every single pass. That is the "casting it nonstop"
bug. It lives in `out_of_combat` only.
RAW health.pct here, NOT health.effective.pct. The docs define effective
as healthPct - healAbsorbPct + incomingHealsPct — it ADDS healing already
on the way. On a HoT healer that inflates everyone: a player at 55% real
health with Rejuvenation, Wild Growth and Lifebloom ticking reads 75-85%
effective. Gated on effective<60 this line needed someone at roughly
35-40% ACTUAL health, which is why it never fired.
Effective health is the right metric for "do they still need healing"
(it stops overheal). It is the wrong metric for "is this an emergency".
off_gcd=true is kept — Nature's Swiftness is off the global, so this is
free. Note it renders as a small overlaid icon during another spell's
GCD, not as the main suggestion.
```

---

## - regrowth,name="Nature Swift Regrowth",cycle=members,if=buff.natures_swiftness.up&cycle.health.pct<config.natures_swiftness_threshold

`FerrazRestoDruid.yaml` line 767

```
Overgrowth (new in 12.1) rides this line for free: with Nature's
Swiftness up, this Regrowth also applies Lifebloom, Rejuvenation and Wild
Growth to the same target. No extra line needed.
```

---

## - swiftmend.player,name="Self Swiftmend (Archdruid)",range_check=none,if=talent.power_of_the_archdruid&player.combat&cooldown.swiftmend.ready&(buff.rejuvenation.up|buff.regrowth.up|buff.wild_growth.up)

`FerrazRestoDruid.yaml` line 777

```
NEW in 5.0 — Power of the Archdruid: Swiftmend on cooldown spreads three
Rejuvenations, which is what gets Abundance to 5 stacks fast. Self-cast so
it never waits for someone to be hurt. Grove Guardians also makes every
Swiftmend summon a treant.
```

---

## - swiftmend,name="Swiftmend for SotF/Treants",cycle=members,if=cycle.health.effective.pct<config.swiftmend_threshold&(cycle.buff.rejuvenation.up|pred.cycle.buff.regrowth.up|pred.cycle.buff.wild_growth.up)

`FerrazRestoDruid.yaml` line 782

```
Swiftmend to obtain Soul of the Forest buff (requires active HoT on target)
```

---

## active_healing:

`FerrazRestoDruid.yaml` line 785

```
Sequential Active Healing: SotF consumption -> Lifebloom maintenance -> AoE and ST heals
```

---

## - regrowth,name="Clearcasting Regrowth",cycle=members,if=player.combat&buff.clearcasting.up&cycle.health.effective.pct<99

`FerrazRestoDruid.yaml` line 787

```
Treant usage and Clearcasting synergized with Wild Synthesis
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

## - regrowth,name="Regrowth Emergency",cycle=members,if=cycle.health.pct<config.regrowth_emergency_threshold

`FerrazRestoDruid.yaml` line 799

```
RAW health, like Nature's Swiftness: effective adds incomingHealsPct, so
with your HoTs rolling "50% effective" is roughly 30% real. An emergency
line has to read the health the player actually has.
```

---

## - rejuvenation,name="SotF Rejuvenation",cycle=members,if=var.has_soul&cycle.buff.rejuvenation.refreshable

`FerrazRestoDruid.yaml` line 804

```
Soul of the Forest is spent on REJUVENATION first. This is a priority
change in 5.0: the old order burned the proc on Regrowth. method.gg is
explicit that the proc belongs on Rejuvenation, and with Power of the
Archdruid in the build a SotF Rejuv is what feeds the Swiftmend spread.
Regrowth keeps the proc only as a fallback when nobody needs a HoT.
```

---

## - efflorescence,name="Efflorescence (no Lifetreading)",range_check=none,if=talent.efflorescence&!talent.lifetreading&!totem.efflorescence.up

`FerrazRestoDruid.yaml` line 813

```
Efflorescence is NOT CAST on this build. Lifetreading (1217941) carries
`replace="Efflorescence" (id=145205)` in its own spell data and reads
"Efflorescence healing increased by 25%, and it now automatically grows
beneath your Lifebloom target's feet." It REPLACES the button: with
Lifetreading talented there is nothing to cast, and the puddle follows
whoever holds your Lifebloom. The reference M+ log confirms it — 452
automatic placements of the Lifetreading version (1232285) and zero casts
of 145205 across 26 minutes.

The line is kept, gated on !talent.lifetreading, so a build that drops
Lifetreading still places the puddle by hand. On THIS build it is inert.

Consequence worth knowing: Lifetreading makes lifebloom_target decide
where your Efflorescence sits. That is why the default is the tank.
```

---

## - lifebloom.player,name="Self Lifebloom (Everbloom)",range_check=none,after=300,if=config.lifebloom_target=1&talent.everbloom&(buff.lifebloom.down|buff.lifebloom.remains<4.5)

`FerrazRestoDruid.yaml` line 829

```
NEW in 5.0 — Everbloom self loop. after=300 debounces Everbloom's own
restack tick; refreshing under 4.5s keeps the stacks it has built.
```

---

## - rejuvenation.player,name="Self Rejuvenation (Photosynthesis)",range_check=none,if=talent.photosynthesis&player.combat&buff.rejuvenation.down

`FerrazRestoDruid.yaml` line 834

```
NEW in 5.0 — Photosynthesis wants a Rejuvenation on yourself.
```

---

## - regrowth,name="Abundance Regrowth",cycle=members,if=buff.abundance.up&cycle.health.effective.pct<config.regrowth_threshold

`FerrazRestoDruid.yaml` line 838

```
Spend the Abundance window. Regrowth at -60% cost and +60% crit is the
entire payoff of keeping 5 Rejuvenations up; without this line the file
built the buff and never cashed it. FerrazRestoDruidRaid.yaml already
had this and the M+ file did not.
```

---

## - wild_growth,name="Wild Growth",range_check=none,if=group.count(cycle.health.effective.pct<config.wild_growth_threshold&!cycle.tank)>=config.wild_growth_members

`FerrazRestoDruid.yaml` line 844

```
Core periodic and direct healing logic
```

---

## utility:

`FerrazRestoDruid.yaml` line 851

```
Utilities, Mobility, and Mana Recovery
```

---

## - innervate.player,name="Innervate",off_gcd=true,ignore_queue=true,delay=150,range_check=none,if=talent.innervate&mana.pct<config.innervate_threshold&fight_remains>15

`FerrazRestoDruid.yaml` line 854

```
innervate.player, not bare innervate. Without an explicit cast target the
addon needs a target to fire it and simply does nothing when you have
none — which is most of the time between pulls, exactly when you want the
mana back. As a healer you innervate YOURSELF anyway (Season 2 made it a
flat 25% mana restore), so pinning the target loses nothing.
range_check=none for the same reason: it is a self-cast, so there is no
range to check.
talent.innervate added: the new build drops it, and the reference druid
never casts it in 26.9 minutes. Gated, not deleted.
```

---

## abundance_maintenance:

`FerrazRestoDruid.yaml` line 866

```
ABUNDANCE CHANGED IN 12.1 and this list was still written for the old one.
From the game's own spell data (207383 / 207640):
  "While you have at least 5 Rejuvenations active, Regrowth's cost is
   reduced by 60% and critical chance is increased by 60%."
  Buff 207640: Stacks: 1 maximum, duration 30s.
It no longer stacks per Rejuvenation — it is a binary threshold. The old
gate here read `buff.abundance.stack<5`, and since the buff caps at ONE
stack that comparison is true even while the buff is up. The filler could
never stop, in combat or out. It now gates on !buff.abundance.up, so it
pads until the threshold is met and then goes quiet.
```

---

## catweave_st:

`FerrazRestoDruid.yaml` line 880

```
Cat Form DPS Rotation (Single Target)
```

---

## catweave_aoe:

`FerrazRestoDruid.yaml` line 887

```
Cat Form DPS Rotation (AoE)
Until 5.1 this list was byte-identical to catweave_st — it filled with
Shred, a single-target builder, at every target count. Swipe IS talented on
this build and is the Cat AoE builder. Measured on sim/ab_test_resto_dps.py:
    3 targets   37994 -> 38501   +1.33%
    5 targets   44390 -> 51431  +15.86%
Numeric id 106785, not the name: "swipe" also matches the Bear version
(213764), the same reason FerrazFeral.yaml and FerrazGuardianElune.yaml use
ids for it. Shred stays underneath as the low-target fallback.
```

---

## - 106785,name="Swipe AoE",if=talent.swipe

`FerrazRestoDruid.yaml` line 901

```
talent.swipe: the reference build does not take it and never casts it
(0 Swipe casts in 26.9 min). Gated rather than deleted so the line
returns on its own if the build does. Shred below is the fallback.
```

---

## catweave:

`FerrazRestoDruid.yaml` line 907

```
Catweaving Transition and Entry (Physical DPS)
```

---

## - rake,name="Fluid Rake",if=!buff.cat_form.up

`FerrazRestoDruid.yaml` line 909

```
Fluid Form does the shifting, so the entry is a DAMAGE cast, not a form
cast. From the tooltip (449193), which SimC's Description field only
reproduces one line of:

  Shred, Rake, and Skull Bash ... shift you into Cat Form
  Mangle ... shifts you into Bear Form
  Wrath and Starfire shift you into Moonkin Form, if known.

So Rake both enters Cat AND applies the bleed in one global. The explicit
cat_form below is the fallback for a build without the talent — gated on
!talent.fluid_form so it never competes with the free shift.

The reference +15 log settles that this is how it plays: 53 Rake casts
against 3 Cat Form casts in 26.9 minutes. He essentially never shifts by
hand.
```

---

## - heart_of_the_wild,name="HotW Cat",if=config.use_heart_of_the_wild&talent.heart_of_the_wild&buff.cat_form.up

`FerrazRestoDruid.yaml` line 928

```
Heart of the Wild is cast BY NAME ONLY. Do not add morph ids to this
line — 2.6 and 2.7 both tried and both made it worse.

The talent (1261867) reads "Perform a powerful off-role ability depending
on your currently active shapeshift form". For a Restoration druid in Cat
Form the off-role ability is FERAL FRENZY, so the button showing Feral
Frenzy is the morph working correctly, not a misfire. Casting by name
follows that morph; casting by a hardcoded id fights it and surfaces the
wrong spell.

2.6 added 1261868 copied from FerrazGuardianElune.yaml — a Guardian file,
whose button is not this one. 2.7 added 1261867 on top. Both reverted.
If it misbehaves after a spec change, that is a Simia-side stale-button
problem and no id in this file will fix it.
```

---

## - convoke_the_spirits,global_delay=750,name="Convoke (Offensive)",if=buff.cat_form.up&cooldown.convoke_the_spirits.ready&target.time_to_die>10

`FerrazRestoDruid.yaml` line 943

```
global_delay, and NOT 500. This line had no delay at all while every other
Convoke line in both Resto files carried global_delay=500.

The guard `return,if=player.channeling` is the first line of main, so once
the channel is REGISTERED nothing below it runs. The gap is the window
between pressing Convoke and the client reporting the channel — a server
round trip plus the addon's polling interval. In that window the rotation
completes a full pass and suggests something else; during heavy healing
there is always a heal waiting, which is exactly when the clipping was
seen. global_delay is the documented tool for this: "blocks ALL spells for
N ms after pressing (useful for registering channels)".

Raised to 750 because 500 is marginal on a South American connection —
150-250ms of latency plus polling lands close to the old value. The cost
is 750ms of held suggestions after a Convoke press, which is free while
you are channelling for 4 seconds anyway.
```

---

## ranged_dps:

`FerrazRestoDruid.yaml` line 963

```
Caster-form damage. Rebuilt from a reference +15 log (Kireya, Murder Row,
26.9 min) after the build changed to that druid's exact string.

What he ACTUALLY casts, counted from the log — not what the talents allow:

  Sunfire   58 casts   29.3% of his total damage, the single biggest source
  Moonfire  22 casts    7.6%
  Starfire   0 casts   talented and never pressed
  Wrath      0 casts   the 49 Wrath hits in his damage come from Convoke
                       firing it, not from a manual cast

So this list is two DoTs and nothing else. No Starfire and no Wrath filler:
both are available on this build and he uses neither, and a filler here
would compete with the Cat weaving that produces the other 25%.

Sunfire first — it is four times Moonfire's damage share.

talent.sunfire gates it so the file still works if the build moves back:
Sunfire (93402) is "Talent Entry: Generic [tree=class, row=4, col=9]", a
class talent, not baseline for Restoration.
```

---

## bearweave:

`FerrazRestoDruid.yaml` line 987

```
Defensive rotation and debuffs in Bear Form (Bearweave)
!var.hotw_pending on both bear casts is what lets Heart of the Wild happen
at all. Read the flow: main calls bearweave, bearweave Thrashes (which
shifts you to BEAR via Fluid Form), then hands off to catweave, which casts
Rake to shift you to CAT. Next pass Thrash is up again and pulls you back
to Bear. HotW requires Cat Form at the instant it is evaluated, so in that
ping-pong it almost never gets a window — it only fired in testing when
Thrash and Mangle happened to both be on cooldown at once.
With this guard, a ready HotW makes bearweave step aside for one pass: you
go straight to Cat, cast it, and the bear bleeds resume afterwards.

No bear_form cast here either, for the same reason as catweave: Mangle is
in Fluid Form's list and shifts you into Bear by itself. Thrash is NOT in
that list, so out of Bear it is simply unusable and the pass falls through
to Mangle, which shifts you — after which Thrash works on the next pass.
```

---

## moving:

`FerrazRestoDruid.yaml` line 1007

```
Healing on the Move: Instant spells only (HoTs and Lifebloom)
```

---

## - call_action_list,name=abundance_maintenance,if=!var.can_catweave&(player.combat|config.ooc_abundance)

`FerrazRestoDruid.yaml` line 1012

```
Third caller, same rule: in combat always, out of combat only on request.
```

---

## avatar_sethraliss:

`FerrazRestoDruid.yaml` line 1015

```
Emergency Mouseover Healing on unit frames
Temple of Sethraliss, Avatar of Sethraliss. A Valithria-style fight: the
party heals the boss to 100% instead of killing it.

WHY MOUSEOVER AND NOT cycle=members. cycle=members walks the PARTY only —
the Avatar is never in it, so no amount of work inside the normal healing
lists could ever reach the boss.

WHY THIS DOES NOT REUSE mouseover_healing_emergency. That list is gated in
main on var.mo_friendly_valid, which requires mouseover.unitframe, and the
catalog is explicit: unitframe is "true if the mouseover came from a UI
unit frame (party/raid frame), FALSE IF FROM THE 3D WORLD". The Avatar is a
world unit, so that gate shuts before any line inside is read. Rollfacedk's
Battle Nurse Paladin solves it by dropping the unitframe check entirely,
which also heals every friendly NPC in the game; the npcid lock below gets
the same reach without that.

FAIL-SAFE DIRECTION. 1301199 (Defiling Taint) is a server-side dummy aura
and it is NOT confirmed which unit carries it — the Avatar or the Essence
Defiler channelling it. If it never resolves on the Avatar, `.down` reads
true forever and this degrades into "heal whenever you point at it", which
is exactly the behaviour that already works for Rollfacedk. The wrong guess
costs nothing; it never fails closed into a dead line.

Order is throughput: instant HoT, then Swiftmend eating it, then hardcast.
```

---

## engine:

`FerrazRestoDruid.yaml` line 1054

```
ENGINE. Queue flush plus the pre-rotation guards, in one list, called once
at the top of main.

This was two lists — spell_queue and sanity_checks — and this file was the
only one of the seven still shaped that way; the other six merged theirs
into `engine` long ago. Same actions in the same order, one caller instead
of two.

Nothing here is inherited. This file has always defined its own guards
rather than taking Simia's, which is why the shared auto_dispel /
auto_brez / auto_combat_potion chain never applied, and 5.2 inlined the
last two shared lists (auto_heal and auto_target_ranged) as well.
```

---

## - return,if=!state.rotation

`FerrazRestoDruid.yaml` line 1069

```
The five guards. `mounted` and `travel_form` were both missing from this
local copy; without them the rotation fires while mounted or flying.
```

---

## - natures_cure,delay=500,cycle=members,name="Nature's Cure",if=config.auto_dispel&cycle.dispelable.list

`FerrazRestoDruid.yaml` line 1081

```
Nature's Cure removes MAGIC, curse and poison — the healer dispel. It had
no toggle before; dispelling is your job, so it defaults ON.
```

---

## - natures_cure,delay=500,cycle=members,cycle_order=player_first,name="Devouring Rift (Affix)",if=config.affix_devour&cycle.debuff.440313.up.any

`FerrazRestoDruid.yaml` line 1084

```
Devouring Rift (Devour affix) bypasses dispel-type matching, so it needs
its own line keyed on the debuff id. player_first: clear yourself first.
```

---

## - healthstone,delay=250,if=healthstone.ready&health.pct<=config.healthstone_pct

`FerrazRestoDruid.yaml` line 1090

```
Inlined from _shared.yaml auto_heal. The shared list has no mana potion
line; a healer is the one spec that actually runs dry, so it is added.
```

---

## - target_enemy,delay=200,off_gcd=true,if=player.combat&config.auto_target.has(0)&!target.exists&enemies.combat.40y>=1

`FerrazRestoDruid.yaml` line 1096

```
Inlined from _shared.yaml auto_target_ranged (40y — you cast from range
even while weaving).
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

`FerrazRestoDruid.yaml` line 1116

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

## main:

`FerrazRestoDruid.yaml` line 1141

```
Main Rotation (main) with combat priorities
```

---

## - return,if=player.channeling|player.casting|var.protected_channel

`FerrazRestoDruid.yaml` line 1143

```
Aborts if channeling crucial abilities (Tranquility/Convoke)
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

## - call_action_list,name=avatar_sethraliss,if=mouseover.npcid=133392&mouseover.friendly&mouseover.debuff.1301199.down&mouseover.health.pct<100

`FerrazRestoDruid.yaml` line 1197

```
Temple of Sethraliss last boss.

No config toggle: mouseover.npcid=133392 already locks this to one NPC in
one dungeon, so a checkbox could only ever turn OFF something that never
fires anywhere else.

Deliberately NOT gated on !var.in_dps_form|!var.group_healthy either.
Healing the Avatar IS the objective of the fight, so it must not wait for
the party to be hurt first.
```

---

## - call_action_list,name=mouseover_healing_emergency,if=config.use_mouseover&var.mo_friendly_valid&mouseover.health.pct<config.mouseover_emergency_hp&(!var.in_dps_form|!var.group_healthy)

`FerrazRestoDruid.yaml` line 1207

```
Emergency Mouseover Healing on unit frames
```

---

## - call_action_list,name=active_healing,if=!var.in_dps_form|!var.group_healthy

`FerrazRestoDruid.yaml` line 1210

```
Sequential Active Healing: SotF consumption -> Lifebloom maintenance -> AoE and ST heals
```

---

## - call_action_list,name=abundance_maintenance,if=player.combat

`FerrazRestoDruid.yaml` line 1212

```
Pad Abundance IN COMBAT, always, regardless of the toggle. The toggle is
about downtime only.

This caller had to exist. The only in-combat caller was the downtime one
at the bottom of this list, and it carries
(!target.exists|target.friendly|target.range>40) — so it needed you to
have NO enemy target. It also sits below ranged_dps/bearweave, both of
which end in an unconditional filler (wrath, shred), so it was doubly
unreachable. Standing in combat on a live target with the group topped,
Abundance was never padded at all, even though the config text has always
claimed "in combat the padding runs regardless of this toggle".

Placed here on purpose: below every healing list, above the damage. That
is the real trade — a global spent padding is a global not spent on
damage. The list gates itself on !buff.abundance.up, so it stops as soon
as the 5 Rejuvenations are up and does not bleed DPS after that.
```

---

## - mark_of_the_wild,range_check=none,name="Mark of the Wild (low prio)",if=(buff.mark_of_the_wild.down.any|action.mark_of_the_wild.overlayed)&lastcast.mark_of_the_wild>=10

`FerrazRestoDruid.yaml` line 1230

```
Mark of the Wild, in combat, at the bottom of the priority. Everything
that heals outranks it; it outranks the DPS weaving. So a dropped buff is
reapplied on a global that would otherwise have been damage, never on one
that would have been a heal.
```

---

## - call_action_list,name=ranged_dps,if=config.ranged_dps&var.can_catweave&target.exists&target.alive&!target.friendly&!target.in_melee

`FerrazRestoDruid.yaml` line 1237

```
DPS weaving when the group is healthy
```


---

## Moved out of the YAML on 2026-08-28

The rotation files had grown back to roughly half comment while the root
cleanse and Incarnation work was going on. These blocks were trimmed to a
line or two each in the YAML; the full text is kept here.

---

### version: "5.7.0"

`FerrazRestoDruid.yaml` line 1

```
=============================================================================
Restoration Druid Ferraz M+ - spec 105 - patch 12.1.
=============================================================================

Lists (entry point: main):
  interrupts              out_of_combat           defensives              racials
  cooldowns               active_healing          utility                 abundance_maintenance
  catweave_st             catweave_aoe            catweave                ranged_dps
  bearweave               moving                  avatar_sethraliss       mouseover_healing_emergency
  auto_rez                engine                  main

WHY ANY OF IT IS THE WAY IT IS: .agents/rationale/RestoDruid.md
That file carries every measurement, every rejected alternative and every
bug this file has already been through. Read it before changing a line -
most of what looks improvable here was tried and reverted.
=============================================================================
```

---

### druid_shapeshift_root: player.debuff.root.up|player.debuff.snare.up

`FerrazRestoDruid.yaml` line 496

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
