# Simia Pro YAML Rotations Rule

Whenever you are tasked with creating, reviewing, or modifying a YAML rotation file in this workspace, you MUST adhere to the following workflow BEFORE taking any action:

1. **Review Official Documentation:** Read `c:\Games\Python\Rotations\SIMIA_DOCUMENTATION.md` to refresh your understanding of the structural requirements, config widgets, modifiers, and syntax of Simia Pro rotations.
2. **Consult Shared Data (`simia_data_dump/`):** Simia Pro heavily relies on centralized shared databases. Consult the files in `c:\Games\Python\Rotations\simia_data_dump\` (specifically files like `_spells.yaml`, `_defensives.yaml`, `_npcdata.yaml`, etc.) to understand existing pandemic thresholds (which enable `.refreshable`), predictive capabilities (`pred.cycle`), and burst variables.
3. **Apply Advanced Mechanics:** Ensure you are utilizing advanced capabilities such as `off_gcd=true`, `ignore_queue=true`, and predictive targets (`pred.cycle.health.pct`, `incoming.pct`) instead of relying on basic/archaic logic that blocks the spell queue. 
4. **Match the House Format:** Follow `.agents/SIMIA_YAML_STANDARD.md` — the formatting and
   validation rules extracted from the `rotation-yaml-intellisense` VS Code extension. Before
   finishing any edit to a rotation file, run `python lint_rotations.py` and leave it clean.
5. **Avoid Spell Queue Blocking:** Do NOT block the rotation's `main` list with generic `player.casting` or `player.channeling` checks unless it is strictly necessary to protect specific channeled abilities (like Tranquility or Convoke). Generic blocking breaks the WoW spell queue mechanism.
