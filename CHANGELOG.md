# Changelog

Player-facing changes to the Ferraz rotations, newest first. Each entry names the rotation and the version that shipped it.

## 2026-10-23

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
