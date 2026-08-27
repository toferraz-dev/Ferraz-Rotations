# Destruction — rationale
Every technical comment that used to live in `FerrazDestruction.yaml`, moved out so the
rotation file can stay readable. Nothing here was rewritten: the text is
verbatim, in file order. The YAML keeps a short comment at each of these
points.

Read this before changing the matching line — most of it records something
that was already tried and failed.

---

## version: "1.0.0"

`FerrazDestruction.yaml` line 1

```
=============================================================================
Destruction Warlock — spec 267 — patch 12.1 (Midnight) — Diabolist, M+.
=============================================================================

Built on the architecture of FerrazBalance.yaml: the plumbing, the combat
wall, the TTD gating and the engine list are the same shape. Only the damage
priority is Warlock.

── WHY DIABOLIST ────────────────────────────────────────────────────────────
Measured on this machine, SimC 1210-01 nightly 2165324, against SimC's own
MID2 Warlock profiles so every spec runs the same gear:

                           DungeonSlice   1 target   5 targets
  Destruction Diabolist        225783      217623      465068
  Demonology                   206622      206167      422138
  Destruction (Hellcaller)     201216      225286      397809
  Affliction                   194216      207494      439239
  Affliction Hellcaller        182600      200422      414794

+9.3% over the next spec on the M+ proxy, and it leads at 5 targets too.
Destruction with the other hero tree wins single target (225286) — that is
the one count where Diabolist is behind, which is why this file is M+ and
not raid.

── WHERE THE PRIORITY COMES FROM ────────────────────────────────────────────
SimC's own Destruction APL, read out of the MID2 Diabolist profile, then
translated to Simia using simia_data_dump/rotation_267.yaml — the OFFICIAL
Simia Destruction rotation — for the addon-side spellings. Nothing here is
invented: every expression appears in one of those two sources.

── THE TALENT STRING, VERIFIED BY WHAT ACTUALLY CAST ─────────────────────────
Reading the talent tree out of the HTML report is not reliable: it lists the
whole tree, selected or not, so it reported both Wither and Immolate, and
both hero trees. What settles it is the Actions table — the spells the sim
really pressed:

  CAST      chaos_bolt, conflagrate, immolate, incinerate, infernal_bolt,
            rain_of_fire, ruination, shadowburn, soul_fire, summon_infernal
            + the Diabolist manifestations (diabolic_gaze, diabolic_imp,
              echo_of_sargeras, eye_explosion)
  NOT CAST  wither, havoc, cataclysm, malevolence

So: Immolate, not Wither — this is Diabolist, not Hellcaller. Every branch
in SimC's list that keys off wither / havoc / cataclysm / malevolence /
internal_combustion / fire_and_brimstone is DEAD on this build and was
dropped rather than carried as noise. Put them back only with the string.

── COUNTING ENEMIES ─────────────────────────────────────────────────────────
enemies.around_target, not active_enemies and not enemies.combat.40y.
active_enemies is a NAMEPLATE count (see SIMIA_DOCUMENTATION pitfall #8) and
would fire AoE next to a training dummy. around_target counts enemies near
the TARGET, which is where Rain of Fire physically lands — for a
ground-targeted spender that is the question worth asking, and it is what
Simia's own rotation_267 uses.

── WHAT IS NOT MEASURED ─────────────────────────────────────────────────────
Everything below is judgement, and each carries the same warning at its own
config entry:
  defensives, both HP sliders     SimC has no M+ damage-intake model
  the dispel and interrupt lists  no dispel model, no cast-bar model
  both moving_* lists             SimC never moves
  every ttd_* slider              sim dummies live the whole fight
  the pet choice                  SimC never needs a kick
=============================================================================
```

---

## about:

`FerrazDestruction.yaml` line 76

```
==========================================================================
BUILD STAMP — display only. Keep in sync with version:/patch: above.
==========================================================================
```

---

## recommended_talents:

`FerrazDestruction.yaml` line 85

```
==========================================================================
RECOMMENDED BUILD — the string this priority assumes.
==========================================================================
```

---

## pet_choice:

`FerrazDestruction.yaml` line 94

```
==========================================================================
PET — the single biggest utility decision this spec makes.
==========================================================================
Destruction has NO interrupt of its own. Spell Lock belongs to the
Felhunter and Axe Toss to the Felguard (Demonology only), so the pet you
carry decides whether you can kick at all. Shadowfury is a stun, not a
kick: it works on trash and does nothing to a boss.

Imp brings Singe Magic instead — the only Magic dispel a Warlock has, per
simia_data_dump/_dispeldata.yaml.

In a key the kick is almost always worth more than the dispel. Default is
Felhunter for that reason, and the dispel list simply goes quiet.

UNMEASURABLE: SimC never needs a kick and never takes a dispellable
debuff, so this is judgement, not a number.
```

---

## auto_burst:

`FerrazDestruction.yaml` line 128

```
==========================================================================
COOLDOWNS — Summon Infernal is the burst window everything else rides.
==========================================================================
Diabolist keys off Diabolic Ritual stacking into Demonic Art, and the
Infernal is what the trinkets and potion align to. var.infernal_active is
taken verbatim from Simia's rotation_267: it counts the 20 seconds AFTER
the summon as well, because the Infernal keeps hitting after the button.
```

---

## infernal_min_standing_time:

`FerrazDestruction.yaml` line 149

```
Same reasoning as inc_min_standing_time in FerrazBalance.yaml: while you
are still repositioning behind the tank the pull is not parked, and an
Infernal dropped on a pack nobody has gathered is the cooldown wasted.
Destruction has an extra reason — it is a hardcast spec, so if you are
moving you are not spending the window anyway.

UNMEASURABLE: SimC never moves, so player.standing.time is effectively
infinite there and this gate is always open.
```

---

## use_trinket_1:

`FerrazDestruction.yaml` line 166

```
==========================================================================
TRINKETS & CONSUMABLES — all three ride the Infernal window.
==========================================================================
```

---

## ttd_infernal:

`FerrazDestruction.yaml` line 187

```
==========================================================================
TIME TO DIE — stop a long cooldown being spent on trash that is about to
  die. target.boss short-circuits every one of them.
  UNVALIDATED: SimC dummies live the whole fight.
==========================================================================
```

---

## ttd_immolate:

`FerrazDestruction.yaml` line 216

```
Immolate is a DoT with a ramp. Refreshing it on a mob that dies first is
a wasted global AND a wasted shard trickle.
```

---

## aoe_threshold:

`FerrazDestruction.yaml` line 227

```
==========================================================================
AOE — where the AoE list opens and when Rain of Fire is worth a shard.
==========================================================================
SimC opens the Diabolist AoE list at 2. Not re-measured here against your
own gear — this is SimC's threshold, carried over.
```

---

## rof_min_enemies:

`FerrazDestruction.yaml` line 241

```
Rain of Fire is a shard spender and a channel. SimC gates it at 3 enemies
and scales the shard floor by how many Immolates are already out.
```

---

## unending_resolve_dmg_pct:

`FerrazDestruction.yaml` line 251

```
==========================================================================
DEFENSIVES — UNVALIDATED: SimC has no M+ damage-intake model.
  Two different scales: incoming.mitigated.pct is post-defensives, so 40
  on a Dmg% slider is NOT 40 on an HP% slider.
==========================================================================
Both lines and both scales are lifted from Simia's own rotation_267
defensives list, which is the only part of that file this rotation copies
wholesale.
```

---

## dark_pact_dmg_pct:

`FerrazDestruction.yaml` line 275

```
Dark Pact eats your own health for a shield, so it wants to fire while you
still HAVE health to spend. Deliberately a higher HP floor than Unending
Resolve, not a lower one.
```

---

## auto_dispel_self:

`FerrazDestruction.yaml` line 294

```
==========================================================================
DISPELS — Singe Magic only, and only with an Imp out.
==========================================================================
From simia_data_dump/_dispeldata.yaml the Warlock's only entry is
singe_magic — the Imp's Magic dispel. It is a PET ability, so with the
default Felhunter this whole section is inert and the toggle does nothing.
UNVALIDATED: SimC has no dispel model.
```

---

## engine_loot_nearby:

`FerrazDestruction.yaml` line 315

```
==========================================================================
ENGINE — the plumbing FerrazBalance.yaml inlines instead of inheriting.
  Simia's shared `sanity_checks` is NOT just guards: it also calls
  auto_dispel, affix, auto_purge_enrage, auto_brez, auto_rez and
  auto_combat_potion. Inheriting it means none of that can be switched
  off, and the shared potion call fights this file's own potion line.
  The five return guards are copied verbatim — do not drop any of them.
==========================================================================
```

---

## engine_auto_combat:

`FerrazDestruction.yaml` line 329

```
Defined locally rather than inherited, for the same reason as in
FerrazBalance.yaml: this file claims to own its plumbing, and an inherited
default can move without any commit here. Same options, same default.
Note "Off" is option 0 and is NOT selected by default, so the has(0) guard
below is inert until you tick it yourself.
```

---

## discord_button:

`FerrazDestruction.yaml` line 379

```
==========================================================================
HELP
==========================================================================
```

---

## infernal_active: pet.infernal.active|(cooldown.summon_infernal.duration-cooldown.summon_infernal.remains)<20

`FerrazDestruction.yaml` line 390

```
Verbatim from Simia's rotation_267. The second clause is the important
half: the Infernal keeps hitting for 20s after the button, so the burst
window is not "the cast", it is the cast plus that tail.
```

---

## ritual_length: buff.diabolic_ritual_mother_of_chaos.remains+buff.diabolic_ritual_overlord.remains+buff.diabolic_ritual_pit_lord.remains

`FerrazDestruction.yaml` line 395

```
Diabolic Ritual builds toward Demonic Art. Only one of the three is ever
up, so summing the three remains values reads as "time left on the ritual"
— which is what every Chaos Bolt decision below keys off.
```

---

## burst_ok: config.auto_burst|config.burst_toggle

`FerrazDestruction.yaml` line 400

```
Burst allowed: auto or manual toggle.
```

---

## pull_engaged: player.combat&player.standing.time>=config.infernal_min_standing_time&debuff.immolate.up

`FerrazDestruction.yaml` line 403

```
The pull is actually parked. Same shape as FerrazBalance's pull_engaged:
combat, standing still for N seconds, and something has been hit. Immolate
on the target is the "something has been hit" proof.
```

---

## infernal_ttd_ok: (target.boss|target.time_to_die>=config.ttd_infernal|fight_remains>=config.ttd_infernal)

`FerrazDestruction.yaml` line 408

```
=== TIME TO DIE === (target.boss always ignores TTD)
```

---

## engine:

`FerrazDestruction.yaml` line 415

```
Everything spell_queue / sanity_checks / auto_target_ranged used to do,
inlined so every piece has a toggle.
```

---

## - queue_spell,if=!player.casting&!player.channeling

`FerrazDestruction.yaml` line 418

```
`&`, not `|`. With `|` the condition is true whenever you are not doing
at least ONE of the two, and you are almost never casting AND
channelling at once — so it reads true on every pass and guards nothing.
```

---

## - return,if=!state.rotation

`FerrazDestruction.yaml` line 423

```
--- The five guards, verbatim. Dropping any lets the rotation fire while
dead or mounted.
```

---

## - target_enemy,name="Swap Off Storm Blessed",delay=500,off_gcd=true,if=target.buff.1289229.up&enemies.combat.40y>=2

`FerrazDestruction.yaml` line 442

```
--- Temple of Sethraliss, Adderis and Aspix ---------------------------
Storm Blessed alternates between the two bosses and gives its holder
"Immunity - Damage Only" on every school — a hard immunity, not a
reduction, so damage into it is thrown away.

1289229 is the AURA. 1310311 is the 2.5s cast that applies it; gating on
the cast id would only be true for those 2.5 seconds.

target_enemy takes no filter — it is "target nearest enemy" and cycles
on repeated presses, like Tab. So describe why the CURRENT target is
wrong and let the next pass re-evaluate; delay=500 stops it spinning.
enemies.combat.40y>=2 stops it hunting once one boss is dead.
```

---

## pet_support:

`FerrazDestruction.yaml` line 456

```
Out of combat only. A summon in combat costs you the pull, and the
rotation's combat wall keeps this list on the idle side of the line.
```

---

## interrupts:

`FerrazDestruction.yaml` line 462

```
Destruction has NO interrupt of its own — Spell Lock is the Felhunter's.
With an Imp out the first three lines are inert and Shadowfury is all you
have, which stuns trash and does nothing to a boss. See the pet_choice
config for why the default is the Felhunter.
UNVALIDATED: SimC has no cast-bar model.
```

---

## dispels:

`FerrazDestruction.yaml` line 473

```
Singe Magic is a PET ability and belongs to the Imp. With the default
Felhunter this list is inert. UNVALIDATED: no dispel model in SimC.
```

---

## defensives:

`FerrazDestruction.yaml` line 479

```
Ahead of interrupts, so survival outranks utility. Copied from Simia's own
rotation_267 and given per-line configs. UNVALIDATED by simulation.

Predicted damage first, reactive HP second — incoming.mitigated.pct is
post-defensives, so it already discounts anything already running.
```

---

## - dark_pact,name="Dark Pact (HP)",range_check=none,if=health.effective.pct<=config.dark_pact_hp_pct

`FerrazDestruction.yaml` line 487

```
Dark Pact spends your health for a shield, so its HP floor is HIGHER
than Unending Resolve's on purpose — at 20% there is nothing left to
spend and the shield is small.
```

---

## trinkets:

`FerrazDestruction.yaml` line 493

```
Ride the Infernal window. Same shape as FerrazBalance's trinkets list.
```

---

## - combat_potion,delay=150,name="Combat Potion",if=var.burst_ok&config.use_potion&combat_potion.ready&player.combat&(var.potion_ttd_ok&var.infernal_active|fight_remains<=30)

`FerrazDestruction.yaml` line 497

```
fight_remains<=30 lets a potion that would otherwise be wasted at the
end of a fight go out anyway — the same clause that measured +0.61% in
FerrazBalance.yaml. Not re-measured here.
```

---

## racials:

`FerrazDestruction.yaml` line 502

```
Racials ride the same window, exactly as SimC's ogcd list does.
```

---

## st:

`FerrazDestruction.yaml` line 509

```
===========================================================================
SINGLE TARGET — SimC's actions.default, with the dead branches removed.

The shape to understand before editing: Diabolic Ritual charges up and
turns into Demonic Art, and a Chaos Bolt fired while Demonic Art is up is
what consumes it. So Chaos Bolt has TWO entries at different priorities —
one high, to spend the Art, and one low, as an ordinary shard dump.
var.ritual_length is how much ritual time is left.
===========================================================================
```

---

## - soul_fire,name="Soul Fire",if=soul_shard<=4

`FerrazDestruction.yaml` line 519

```
Soul Fire on cooldown while it will not overcap. It is a shard generator
with a cast time, so it goes before the shard spenders.
```

---

## - conflagrate,name="Conflagrate (2 charges)",if=cooldown.conflagrate.charges>=2

`FerrazDestruction.yaml` line 523

```
Do not sit on two Conflagrate charges — the second is pure waste.
```

---

## - chaos_bolt,name="Chaos Bolt (Demonic Art)",if=talent.diabolic_ritual&(demonic_art|var.ritual_length<action.chaos_bolt.execute_time)&target.health.pct>20

`FerrazDestruction.yaml` line 526

```
SPEND DEMONIC ART. The health.pct>20 clause hands the execute window to
Shadowburn instead, which is what the line below it is for.
```

---

## - summon_infernal,name="Summon Infernal",if=var.burst_ok&var.infernal_ttd_ok&var.pull_engaged

`FerrazDestruction.yaml` line 532

```
The burst window. var.pull_engaged is the M+ half SimC cannot model —
see the config note: an Infernal dropped while the tank is still
gathering is the cooldown thrown away.
```

---

## - shadowburn,name="Shadowburn",if=((!demonic_art&var.ritual_length>2)|target.health.pct<=20)&(buff.fiendish_cruelty.up|talent.conflagration_of_chaos)

`FerrazDestruction.yaml` line 537

```
Execute, or a filler when the ritual has time left and no Art to spend.
```

---

## - immolate,name="Immolate",if=(debuff.immolate.remains<debuff.immolate.duration*0.3|debuff.immolate.refreshable)&(!talent.soul_fire|cooldown.soul_fire.remains+action.soul_fire.cast_time>debuff.immolate.remains)&var.immolate_ttd_ok

`FerrazDestruction.yaml` line 540

```
DoT. Pandemic-aware, and TTD-gated so it is not applied to something
about to die. SimC's version also carries an internal_combustion clause;
that talent is not on this build, so it is gone.
```

---

## - chaos_bolt,name="Chaos Bolt (Shard Dump)",if=talent.diabolic_ritual&var.ritual_length>4

`FerrazDestruction.yaml` line 548

```
Ordinary shard dump, well below the Demonic Art one.
```

---

## - infernal_bolt,name="Infernal Bolt",if=soul_shard<=3

`FerrazDestruction.yaml` line 551

```
Infernal Bolt replaces Incinerate while the ritual is running and gives
a bigger shard chunk, so it goes first.
```

---

## aoe:

`FerrazDestruction.yaml` line 556

```
===========================================================================
AOE — SimC's actions.aoe_dia. Havoc and Cataclysm lines removed: neither
is on this build, verified by what the sim actually cast.

SimC uses target_if on several of these to pick the best mob. Simia has no
target_if — the only targeting action is target_enemy, "nearest enemy",
with no filter. So those lines act on the current target instead, which is
the honest translation rather than a fake one.
===========================================================================
```

---

## - chaos_bolt,name="Chaos Bolt (Demonic Art)",if=talent.diabolic_ritual&(demonic_art|var.ritual_length<action.chaos_bolt.execute_time)&enemies.around_target<=(10-2*talent.destructive_rapidity)

`FerrazDestruction.yaml` line 568

```
Spend Demonic Art. The upper bound scales with Destructive Rapidity
exactly as SimC writes it.
```

---

## - rain_of_fire,name="Rain of Fire",if=(soul_shard>=(3.5-0.1*active_dot.immolate)|buff.alythesss_ire.up)&enemies.around_target>=config.rof_min_enemies

`FerrazDestruction.yaml` line 572

```
The shard floor drops as more Immolates tick, because each one feeds
shards back. 3.5 minus 0.1 per active Immolate, straight from SimC.
```

---

## - shadowburn,name="Shadowburn (AoE)",if=enemies.around_target<=(4-talent.destructive_rapidity+2*buff.fiendish_cruelty.up)|(talent.conflagration_of_chaos&enemies.around_target<=(6+2*buff.fiendish_cruelty.up))

`FerrazDestruction.yaml` line 578

```
Target-count cap widens with Fiendish Cruelty up, as SimC has it.
```

---

## - soul_fire,name="Soul Fire (AoE)",if=soul_shard<4&(talent.avatar_of_destruction&enemies.around_target<=10|enemies.around_target<=5)

`FerrazDestruction.yaml` line 585

```
Avatar of Destruction widens the Soul Fire cap from 5 to 10.
```

---

## - immolate,name="Immolate (Spread)",if=debuff.immolate.refreshable&active_dot.immolate<=5&(target.boss|target.time_to_die>18|fight_remains>18)

`FerrazDestruction.yaml` line 588

```
active_dot.immolate<=5 is SimC's cap on how wide it is worth spreading.
TTD is 18 here, not 8 — a spread Immolate needs longer to pay back than
the one on your primary target.
```

---

## moving_st:

`FerrazDestruction.yaml` line 596

```
===========================================================================
MOVING — instant casts only.

This matters far more for Destruction than it did for Balance. Chaos Bolt,
Incinerate, Soul Fire, Immolate and Infernal Bolt are ALL hardcasts, and
Rain of Fire is a channel — so while you move, almost the entire priority
is unavailable. What is left is Conflagrate, Shadowburn and Ruination.

UNMEASURABLE: SimC never moves.
===========================================================================
```

---

## main:

`FerrazDestruction.yaml` line 616

```
Entry point: first matching line wins the GCD, everything above the damage
lists outranks damage.
```

---

## - call_action_list,name=engine

`FerrazDestruction.yaml` line 621

```
--- Engine plumbing. Must stay at the top. ---
```

---

## - call_action_list,name=pet_support,if=!player.combat

`FerrazDestruction.yaml` line 624

```
--- COMBAT WALL. Nothing below this line runs out of combat. ---
Above it: the engine (loot, auto-target, consumables) and the pet
summon. Below: damage, defensives, interrupts and cooldowns.

player.combat, NOT player.auto_combat. The catalog defines the second as
a "Config-based auto-combat check", not combat state — using it here is
the bug that silently disabled four rotations in this repo.
```

---

## - return,if=!target.valid&!((config.engine_auto_combat.has(1)&target.quest_mob&target.enemy&!target.dead)|(config.engine_auto_combat.has(2)&target.combat&target.enemy&!target.dead)|(config.engine_auto_combat.has(3)&target.targeting_party&target.enemy&!target.dead))

`FerrazDestruction.yaml` line 634

```
--- Target guards ---
```

---

## - call_action_list,name=defensives

`FerrazDestruction.yaml` line 639

```
--- Survival, then utility, then the burst window ---
```

---

## - call_action_list,name=moving_aoe,if=player.moving&enemies.around_target>=config.aoe_threshold

`FerrazDestruction.yaml` line 646

```
--- Damage priority: moving first (instant-only), then stationary. ---
```
