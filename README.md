# Ferraz Druid Rotations

Custom rotation profiles for World of Warcraft Druids, optimized for **Mythic+** content.

---

## Guardian Druid
**Version:** 3.5 | **Spec:** 104 | **Build:** Elune's Chosen

### Features
- **Dual Rotation Styles:** Choose between Wowhead (Aggressive DPS) or Alternative (Balanced)
- **Smart Defensive Logic:** Tiered defensive usage based on emergency, dangerous, and heavy damage situations
- **Rage Management:** Automatic Ironfur stacking with configurable thresholds
- **Interrupt System:** Auto-interrupt with configurable delay + Incapacitating Roar for AoE
- **Full Racial Support:** Defensive, offensive, CC, and utility racials for all races
- **Moonfire Spreading:** Galactic Guardian proc management and Lunar Beam synergy

### Configuration Highlights
| Setting | Default | Description |
|---------|---------|-------------|
| Survival Instincts | 50% HP | Emergency defensive threshold |
| Frenzied Regeneration | 65% HP | Self-heal activation |
| Ironfur Stacks | 3-5 | Minimum/maximum stack maintenance |
| Incarnation | 3+ enemies | Major cooldown usage |
| Auto Interrupt | On | With 250ms delay |

---

## Restoration Druid
**Version:** 2 | **Spec:** 105 | **Build:** Wildstalker

### Features
- **Proactive Healing:** Lifebloom on tanks, Rejuvenation/Regrowth maintenance
- **Smart Cooldown Usage:** Convoke (caster form only), Tranquility, Nature's Swiftness
- **Catweaving Support:** Automatic Cat Form shifting for DPS when group is healthy
- **Defensive Externals:** Ironbark and Barkskin with configurable thresholds
- **Utility:** Innervate for mana management, Nature's Cure for dispels
- **Interrupt:** Incapacitating Roar (AoE) + Soothe for enrage removal

### Configuration Highlights
| Setting | Default | Description |
|---------|---------|-------------|
| Ironbark | 60% HP | External defensive on party members |
| Convoke | 70% HP / 3 members | Major healing cooldown |
| Wild Growth | 80% HP / 3 members | AoE heal activation |
| Swiftmend | 60% HP | Emergency single-target heal |
| Catweave | 60% group HP | DPS when group is healthy |

### Catweaving Rotation
- **Single Target:** Moonfire → Rip → Ferocious Bite → Rake → Shred
- **AoE (3+ targets):** Moonfire → Thrash → Swipe → Rake → Shred

---

## Files
- [`FerrazGuardian.yaml`] - Guardian Druid rotation
- [`FerrazRestoDruid.yaml`] - Restoration Druid rotation

---

*Author: Ferraz*
