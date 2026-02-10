# 🐻 Ferraz Druid Rotations 🌿

> Custom rotation profiles for World of Warcraft Druids, optimized for **Mythic+** content.

---

## 🛡️ Guardian Druid — Elune's Chosen

| | |
|---|---|
| **File** | `FerrazGuardian.yaml` |
| **Version** | 3.6 |
| **Spec** | 104 |
| **Build** | Elune's Chosen |

### ✨ Features

| Feature | Description |
|---------|-------------|
| ⚔️ **Dual Rotation Styles** | Wowhead (Aggressive DPS) or Alternative (Balanced) |
| 🛡️ **Smart Defensives** | Tiered usage: Emergency → Dangerous → Heavy Damage |
| 💢 **Rage Management** | Auto Ironfur stacking + Raze/Maul dumps |
| 🔇 **Interrupt System** | Skull Bash + Incapacitating Roar + Soothe |
| 🌍 **Full Racial Support** | Defensive, offensive, CC, and utility for all races |
| 🌙 **Moonfire Spreading** | Galactic Guardian procs + Lunar Beam synergy |
| 🐻 **Elune's Synergy** | Lunar Beam + Rage of the Sleeper integration |

### ⚙️ Configuration

| Setting | Default | Description |
|---------|:-------:|-------------|
| 💔 Survival Instincts | 50% | Emergency defensive |
| 💚 Frenzied Regeneration | 65% | Self-heal threshold |
| 🔰 Ironfur Stacks | 3-5 | Min/max maintenance |
| 🐻 Incarnation | 3+ enemies | Major cooldown |
| 🔇 Auto Interrupt | ✅ On | 250ms delay |
| 🌙 Rage of the Sleeper | 70% | Defensive cooldown |

---

## 🛡️ Guardian Druid — Druid of the Claw

| | |
|---|---|
| **File** | `FerrazGuardianClaw.yaml` |
| **Version** | 1.0 |
| **Spec** | 104 |
| **Build** | Druid of the Claw |

### ✨ Features

| Feature | Description |
|---------|-------------|
| ⚔️ **Dual Rotation Styles** | Wowhead (Aggressive DPS) or Method.gg (Balanced) |
| �️ **Smart Defensives** | Tiered: Emergency → Dangerous → Threshold → Maintenance |
| 💢 **Rage Management** | Ironfur stacking + Ravage procs + Maul dumps |
| 🔇 **Interrupt System** | Skull Bash + Incapacitating Roar + Soothe |
| 🌙 **Moonfire Spreading** | Galactic Guardian procs + pull with Moonfire |
| 🐾 **Ravage & Berserk** | Ravage proc priority + Berserk Ravage support |

### ⚙️ Configuration

| Setting | Default | Description |
|---------|:-------:|-------------|
| 💔 Survival Instincts | 50% | Emergency defensive |
| �💚 Frenzied Regeneration | 65% | Self-heal threshold |
| 🔰 Ironfur Stacks | 3-5 | Min/max maintenance |
| 🐻 Incarnation | 3+ enemies | Major cooldown |
| 🔇 Auto Interrupt | ✅ On | 250ms delay |
| 🌀 Thrash Stacks | 3 | Maintain on target |

---

## 🌙 Balance Druid — Elune's Chosen

| | |
|---|---|
| **File** | `FerrazBalance.yaml` |
| **Version** | 1.0 |
| **Spec** | 102 |
| **Build** | Elune's Chosen |

### ✨ Features

| Feature | Description |
|---------|-------------|
| ⚔️ **Dual Rotation Styles** | Wowhead (Aggressive DPS) or Method.gg (Balanced) |
| 🌟 **Astral Power Management** | Starsurge dumps, Star-Lord maintenance, overcap prevention |
| ☀️ **Eclipse System** | Lunar Eclipse activation + Incarnation burst windows |
| 🌠 **AoE with Starfall** | Configurable enemy threshold for Starfall usage |
| 🔇 **Interrupt System** | Solar Beam + Typhoon + Incapacitating Roar |
| 🛡️ **Defensives** | Barkskin + Shadowmeld for threat drops |
| 💚 **Heal Support** | Heart of the Wild for emergency party healing |
| 🏃 **Movement** | Stampeding Roar with in/out of combat modes |

### ⚙️ Configuration

| Setting | Default | Description |
|---------|:-------:|-------------|
| 🌟 Starfall Threshold | 2+ enemies | Min enemies for Starfall |
| ⚡ AP Dump | 80 | Astral Power overcap threshold |
| 🐻 Incarnation | 3+ enemies | Major cooldown |
| 🔇 Solar Beam | ✅ On | 250ms delay |
| 🌿 Barkskin | 50% | Defensive threshold |
| 💚 Heart of the Wild | ✅ On | Party heal at 80% HP |
| 🌑 Shadowmeld | ✅ On | Threat level 3 |

### 🌙 Rotation Priority

**Single Target:**
> ☀️ Fury of Elune → 🌑 Lunar Eclipse → 🔥 Sunfire/Moonfire → ⭐ Starsurge → ✨ Starfire → 💫 Wrath

**AoE (2+ targets):**
> ☀️ Fury of Elune → 🌑 Lunar Eclipse → 🌠 Starfall → 🔥 Sunfire/Moonfire → ✨ Starfire → 💫 Wrath

---

## 💚 Restoration Druid — Wildstalker

| | |
|---|---|
| **File** | `FerrazRestoDruid.yaml` |
| **Version** | 2.5 |
| **Spec** | 105 |
| **Build** | Wildstalker |

### ✨ Features

| Feature | Description |
|---------|-------------|
| 💚 **Proactive Healing** | Lifebloom on tanks, HoT maintenance, Efflorescence |
| ⏰ **Smart Cooldowns** | Convoke (caster only), Tranquility, Nature's Swiftness |
| 🐱 **Catweaving** | Auto Cat Form when group is healthy |
| 🛡️ **Externals** | Ironbark & Barkskin with thresholds |
| 💧 **Utility** | Innervate + Nature's Cure dispels |
| 🔇 **Interrupt** | Incapacitating Roar + Soothe |
| 🤝 **Symbiotic** | Symbiotic Relationship on tanks |

### ⚙️ Configuration

| Setting | Default | Description |
|---------|:-------:|-------------|
| 🌳 Ironbark | 60% | External on party |
| 🌀 Convoke | 75% / 3 | Caster form healing CD |
| 🌿 Wild Growth | 80% / 3 | AoE heal trigger |
| ⚡ Swiftmend | 65% | Emergency heal |
| 🐱 Catweave | 60% group | DPS when healthy |
| 💧 Innervate | 60% mana | Mana management |

### 🐱 Catweaving Rotation

**Single Target:**
> 🌙 Moonfire → 🩸 Rip → 🦷 Ferocious Bite → 🐾 Rake → ⚔️ Shred

**AoE (3+ targets):**
> 🌙 Moonfire → 🌀 Thrash → 🐾 Swipe → 🐾 Rake → ⚔️ Shred

---

*Made with 💜 by Ferraz*
