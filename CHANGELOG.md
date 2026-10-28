# Changelog

Player-facing changes to the Ferraz rotations, newest first. Each entry names the rotation and the version that shipped it.

## 2026-10-28

### Balance · Mythic+ · v15.0.0
- Moonfire and Sunfire on your mouseover now work while moving and during the burst opener, not only while standing still in AoE. *Spread DoTs on Mouseover* behaves as described again.

### Balance · Raid · v12.0.0
- Moonfire and Sunfire on your mouseover now work while moving and during the burst opener, not only while standing still in AoE. *Spread DoTs on Mouseover* behaves as described again.

## 2026-10-27

### Restoration · Mythic+ · v37.0.0
- Soulcoiler Ritual Vessel is now used as the group defensive it is: its five barriers (-50% damage taken) go out about 3 seconds before an enemy AoE lands, or when the group is already taking heavy damage, instead of waiting for Convoke. Your other trinkets are unchanged.

### Restoration · Raid · v28.0.0
- Soulcoiler Ritual Vessel is now used as the group defensive it is: its five barriers (-50% damage taken) go out about 3 seconds before an enemy AoE lands, or when the group is already taking heavy damage, instead of waiting for Convoke. Your other trinkets are unchanged.

## 2026-10-25

### Guardian · Mythic+ · v5.1.0
- Heartstop Poison (Murder Row) is now dispelled from 2 stacks instead of 4, on you and on the party. Dispelling yourself with it is covered by its own line.

## 2026-10-24

### Restoration · Mythic+ · v36.0.0
- New recommended talents: the Mythic+ build of the world's top Restoration Druid, with Dream of Cenarius, Verdancy, Stonebark, Tranquil Mind and Astral Influence. Copy the new string from the rotation panel.
- Damage now works like his: Sunfire and Moonfire kept up, then Starfire on packs and Wrath on a single target, which heal through Dream of Cenarius. Starsurge only while moving. Heart of the Wild is off by default.
- Wild Growth goes out much more often: keeping Abundance up no longer comes before Wild Growth or the emergency Regrowth.
- Swiftmend prefers allies with Regrowth or Wild Growth, so it stops eating Rejuvenations.
- Convoke needs 2 injured allies instead of 3, and its default health line is 85% instead of 75%, so it comes back about once a minute.
- Barkskin goes out a little earlier by default (50%): Flower Walk heals the group around you while it is up.
- Ironbark defaults to *All Members* (a healing cooldown with Stonebark), and *Tanks Only* never lands on you.

### Restoration · Raid · v27.0.0
- Free globals now go to a Rejuvenation blanket on raid members who do not have one, before any damage spell. New sliders: *Rejuvenation Blanket - Max Active* (default 10) and *Min Mana %* (default 25). The old cap stopped spreading Rejuvenation after 5, a number made for a 5-player party.
- Swiftmend goes on yourself first. It eats the free Regrowth copy that Rampant Growth puts on your Lifebloom target, instead of eating an injured raider's Rejuvenation or Wild Growth. Soul of the Forest, Tree of Life stacks, Everbloom's bloom burst and Symbiotic Bloom still trigger.
- Wild Growth goes out much closer to its cooldown: it now comes before Lifebloom upkeep and Abundance Regrowth, and its default health line is 95%.
- Ironbark set to *Tanks Only* never lands on you.
- Convoke's default health line is 75%, so it no longer sits ready for half a minute.

### Balance · Mythic+ · v14.0.0
- Remove Corruption now follows Simia's standard dispel: it cleanses the poisons and curses on Simia's dispel list from anyone in the party, you included, with no setting to turn on.
- The "Remove Corruption - Self" and "Remove Corruption - Party" options were removed.

### Balance · Raid · v11.0.0
- New recommended talents: a build with Starweaver, Meteorites, Meteor Storm, Radiant Moonlight and Lunation (still Elune's Chosen). Copy the new string from the rotation panel.
- Starweaver is now used: a free Starfall is cast as soon as it procs, and so is a free Starsurge. Before, those free casts expired unused. Worth about +4.5% damage on a single target and +5.5% on 3 targets in SimulationCraft on the new build.
- Also works while moving and in the opener.
- Starsurge in Eclipse now goes out from 40 Astral Power instead of 50 (+0.4% on a single target).
- Measured against the previous build on the same SimulationCraft: the new build is about +16% with 2 targets and +12% with 3, and 2% behind on pure single target. The previous build's string is in the Balance Raid guide for single-target-only fights.

### Balance · Raid · v10.0.0
- Remove Corruption now follows Simia's standard dispel: it cleanses the poisons and curses on Simia's dispel list from anyone in the party, you included, with no setting to turn on.
- The "Remove Corruption - Self" and "Remove Corruption - Party" options were removed.

### Feral · Mythic+ · v10.0.0
- Remove Corruption now follows Simia's standard dispel: it cleanses the poisons and curses on Simia's dispel list from anyone in the party, you included, with no setting to turn on.
- The "Remove Corruption - Self" and "Remove Corruption - Party" options were removed.

### Feral · Raid · v7.0.0
- Remove Corruption now follows Simia's standard dispel: it cleanses the poisons and curses on Simia's dispel list from anyone in the party, you included, with no setting to turn on.
- The "Remove Corruption - Self" and "Remove Corruption - Party" options were removed.

### Guardian · Mythic+ · v5.0.0
- Remove Corruption now follows Simia's standard dispel: it cleanses the poisons and curses on Simia's dispel list from anyone in the party, you included, with no setting to turn on.
- The "Remove Corruption - Self" and "Remove Corruption - Party" options were removed.

## 2026-10-23

### Devourer · Mythic+ · v1.0.0
- New rotation: Devourer Demon Hunter for Mythic+, on the meta Annihilator build.
- Follows the current SimulationCraft priority: Void Metamorphosis as soon as it is ready, Collapsing Star and Void Ray inside it, Reap only on a full load of souls, Voidfall spent at 3 stacks.
- Never cuts the Void Ray channel or the Collapsing Star cast, and never starts either while moving.
- Predictive Blur, Darkness and Soul Immolation for defense; Disrupt on target, mouseover and focus; Consume Magic purge.

### Restoration · Mythic+ · v35.0.0
- Temple of Sethraliss, last boss: hover or target the Avatar of Sethraliss once and the rotation sets it as your focus. From then on every heal goes to the Avatar while it is friendly, with no need to keep the mouse on it.
- On the Avatar it uses Nature's Swiftness with an instant Regrowth, Wild Growth, Rejuvenation, Germination, Swiftmend and Regrowth.
- The party is not forgotten: if anyone drops below the new "Party Safety HP %" slider (default 50%), the rotation goes back to healing the party, cooldowns included, until they are safe.
- No heals are wasted while Defiling Taint blocks healing on the Avatar.

### Restoration · Mythic+ · v34.0.0
- The combat potion is pressed once, and nothing else is pressed for 0.4s after it, so it no longer lands on top of the Convoke channel.
- Healthstone and health potion are never used during Convoke or Tranquility. Barkskin is never used during Tranquility, whose channel breaks on any action; it still fires during Convoke.

### Restoration · Mythic+ · v33.0.0
- The combat potion now goes out before Convoke. Convoke waits for it while it is available.

### Restoration · Mythic+ · v32.0.0
- Convoke is only cast from caster form. Cat Form was missing from the check, so Convoke could go out with Feral spells.
- "Shift Out For Convoke" now also leaves Cat Form.
- A Convoke you queue by hand waits until you are out of Bear, Cat and Moonkin.

### Restoration · Mythic+ · v31.0.0
- Symbiotic Relationship is no longer cast twice on the tank.

### Restoration · Raid · v26.0.0
- The combat potion is pressed once, and nothing else is pressed for 0.4s after it, so it no longer lands on top of the Convoke channel.
- Healthstone and health potion are never used during Convoke or Tranquility. Barkskin is never used during Tranquility.

### Restoration · Raid · v25.0.0
- The combat potion now goes out before Convoke. Convoke waits for it while it is available.

### Restoration · Raid · v24.0.0
- Convoke is only cast from caster form, and "Shift Out For Convoke" leaves any animal form.
- A Convoke you queue by hand waits until you are out of Bear, Cat and Moonkin.

### Guardian · Mythic+ · v4.0.0
- Incarnation is no longer held back indefinitely while Heart of the Wild is ready. It waits through the HotW delay at the pull plus a few seconds (new "Max Wait" slider), then goes.
- Mark of the Wild is only cast out of combat.
- "Pull with Mouseover Moonfire" is now off by default.
- Ironfur is spent on Gory Fur procs, and Wild Guardian is not recast while its spirit is active.
- Mangle's rage threshold with Soul of the Forest is fixed.
- Settings panel reorganized into clear sections, with descriptions on every option.

### Balance · Mythic+ · v13.0.0
- Barkskin, Panic Bear, interrupts and dispels now work without a valid target, for example while a boss is untargetable.
- The emergency cast cut no longer loops: it only cuts a cast when Panic Bear is about to fire.
- Incarnation follows Fury of Elune even if you start moving, and is also used from the movement list.
- Touch the Cosmos procs go to Starsurge on single target instead of Starfall.
- The burst waits for Moonfire on the whole pack again (capped at 10 targets).
- Mark of the Wild only out of combat. Root breaking waits for your cast to finish.
- With Fluid Form, moving puts you back in Moonkin Form directly.
- Settings panel reorganized; the unused "Auto Combat" option was removed.

### Balance · Raid · v9.0.0
- Barkskin, Panic Bear, interrupts and dispels now work without a valid target.
- You no longer get stuck in Bear Form after a root break at low health.
- The emergency cast cut only fires when Panic Bear is about to follow. Frenzied Regeneration is not recast over itself.
- The opener now triggers on Incarnation charges, so the single-target priority runs between bursts.
- Touch the Cosmos procs and Astral Power go to Starsurge on single target, opener included.
- Starlord, Atmospheric Exposure and the Heart of the Wild bear morph are now detected reliably.
- Unused talent lines from the old Grove build removed. Settings panel reorganized.

### Feral · Mythic+ · v9.0.0
- Root breaking never cuts Convoke.
- Panic Bear no longer flips between Bear and Cat while your health is low.
- Predatory Swiftness, Apex Predator's Craving, Clearcasting and Sudden Ambush procs are detected reliably.
- Tiger's Fury no longer waits for a Berserk that is being held for Convoke.
- Mark of the Wild only out of combat. Predictive Barkskin accounts for your active defensives.
- Settings panel reorganized, with a Self Healing section for the Regrowth options.

### Feral · Raid · v6.0.0
- Root breaking never cuts Convoke.
- Predatory Swiftness, Apex Predator's Craving, Clearcasting and Sudden Ambush procs are detected reliably.
- Mark of the Wild only out of combat. Predictive Barkskin accounts for your active defensives.
- Settings panel reorganized, with a Self Healing section for the Regrowth options.

## 2026-10-22

### Restoration · Mythic+ · v30.1.0
- Settings panel reorganized into clear sections, with descriptions on every option. No change in behavior.

### Restoration · Mythic+ · v30.0.0
- Emergency cast cut never interrupts Tranquility or Convoke.
- Emergency defensives and the emergency Regrowth read your real health.
- Heals pick the lowest health percentage first.
- Rejuvenation spreading respects Abundance, and Swiftmend is used on cooldown.

### Restoration · Raid · v23.0.0
- Tree of Life from Reforestation is now detected: Wild Growth and instant Regrowth during it, and nothing shifts you out of it.
- New option: build 3 Reforestation stacks out of combat, so the first Swiftmend of a trash pull turns you into a tree.
- Cooldown order like Mythic+: Nature's Swiftness then an instant Regrowth, trinkets and potion with Convoke.
- Barkskin, healthstone and health potion also work outside of casts. New Regrowth Emergency slider.
- Convoke is no longer attempted while moving. Mark of the Wild is cast out of combat first.

Earlier history lives in the git log.
