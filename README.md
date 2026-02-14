# Munkey Rotations
[![Discipline Priest](/Priest/Discipline/banner.jpeg)](/Priest/Discipline)
Real-life optimized rotations for World of Warcraft that go beyond simple priority lists. Our rotations are designed with extensive customization options and intelligent decision-making to adapt to actual gameplay scenarios.

*** PLEASE NOTE THAT SOME FEATURES / ROTATIONS MAY REQUIRE THE MUNKEY ROTATIONS ADDON INSIDE THE ADDON FOLDER ***
*** IF YOU EXPERIENCE ANY ISSUES PLEASE DOWNLOAD THE ADDON AND TRY AGAIN BEFORE REPORTING THEM ***

## Feature Requests and bugs
Submit bug reports, requests for new toggles / features or supported class here:
**https://munkey.fdback.io/**

## Quick Links
- 🚀 [Getting Started](#getting-started)
- 🐛 [Bug Report Template](BUG_REPORT_EXAMPLE.md)
- 💡 [Feature Request Template](FEATURE_REQUEST_TEMPLATE.md)

## Philosophy
Traditional rotations often rely on static priority lists that don't account for the dynamic nature of real encounters. Our rotations feature:
- **Context-Aware Decision Making**: Rotations that adapt based on fight conditions, movement, and group needs
- **Extensive Customization**: Granular configuration options to match your playstyle and content type
- **Real-World Optimization**: Tested in actual gameplay scenarios, not just simulation environments
- **Intelligent Cooldown Management**: Smart usage of defensive and offensive cooldowns based on fight dynamics
- **Mouseover Integration**: Full mouseover support for enhanced control and responsiveness

## Supported Specializations
### ✅ Fully Supported
| Class | Specialization | Features |
|-------|---------------|----------|
| Priest | Discipline | Complete healing rotation with Atonement management, smart cooldowns, mouseover support |
| Paladin | Holy | Complete healing rotation with smart cooldowns and mouseover support |
| Paladin | Protection | Complete tank rotation with smart cooldowns and mouseover support |

### 🧪 Testers Needed
| Class | Specialization | Status | ETA |
|-------|---------------|--------|-----|
| Paladin | Retribution | Alpha | 2026-01-30 |

### 🚧 In Development
| Class | Specialization | Status | ETA |
|-------|---------------|--------|-----|
| Druid | Feral | Alpha | 2026-01-30 |
| Rogue | Outlaw | Alpha | 2026-01-30 |

### 📋 Planned
| Class | Specialization | Priority |
|-------|---------------|----------|
| Priest | Shadow | MEDIUM |

### ❌ Not Planned
- PvP-specific rotations
- Leveling rotations

## Key Features
### Smart Rotation Logic
- **Conditional Execution**: Actions based on fight state, health levels, and buff/debuff status
- **Movement Optimization**: Special handling for casting while moving
- **Resource Management**: Intelligent use of class resources (Holy Power, Mana, etc.)
- **Proc Utilization**: Automatic detection and usage of beneficial procs

### Extensive Configuration
- **Threshold Customization**: Adjustable health percentages for all abilities
- **Targeting Options**: Flexible targeting with mouseover support
- **Cooldown Management**: Configurable usage of major and minor cooldowns
- **Content Adaptation**: Settings for different content types (raids, dungeons, solo)

### Quality of Life
- **Auto-targeting**: Intelligent enemy selection when none exists
- **Interrupt Management**: Smart interrupt timing with priority systems
- **Emergency Actions**: Automatic life-saving abilities with safety checks
- **Utility Integration**: Seamless use of class utility spells

## Getting Started
1. **Choose your specialization** from the supported list above
2. **Navigate to the class folder** (e.g., `Priest/Discipline/`)
3. **Read the README.md** for detailed configuration options
4. **Import the rotation file** into your rotation addon
5. **Customize settings** based on your needs and content type

## File Structure
```
├── Class/
│   ├── Specialization/
│   │   ├── README.md          # Detailed documentation
│   │   └── rotation_XXX.yaml  # Rotation file
│   └── ...
├── reference_guide.yaml       # Technical reference
└── README.md                  # This file
```

## Contributing
We welcome contributions from the community! Whether it's:
- **Bug reports** for existing rotations
- **Feature requests** for new functionality
- **Documentation improvements**

Please ensure any contributions maintain our philosophy of real-world optimization and extensive customization.

## Requirements
- Compatible rotation addon/framework that supports YAML rotations
- World of Warcraft retail version
- Proper keybinds for all abilities used in rotations
- Mouseover macros recommended for optimal functionality

## Support
For questions, bug reports, or feature requests, please check the individual specialization README files first, as they contain detailed troubleshooting information and known issues. Preferably reports are done on the github repository to make tracking easier and also public visibility of progress.

---

*Rotations are continuously updated based on game changes, community feedback, and real-world testing.*
