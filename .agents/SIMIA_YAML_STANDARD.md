# Simia Rotation YAML — Formatting & Validation Standard

Extracted from `rotation-yaml-intellisense` v1.4.0 (the VS Code extension) so the rules
are usable without the editor. Sources inside the `.vsix`:
`out/providers/formatProvider.js` and `out/diagnosticProvider.js`.

`lint_rotations.py` in the repo root implements everything below.

```bash
python lint_rotations.py
```

```bash
python lint_rotations.py --fix
```

`--fix` only applies the formatting rules (section 1). Diagnostics are reported, never
auto-rewritten. `--strict-options` additionally flags step options absent from the
extension's table.

---

## 1. Formatting

| Rule | Detail |
| --- | --- |
| Indentation | 2 spaces per level. Tabs are invalid; one tab is rewritten as 2 spaces. |
| Trailing whitespace | Stripped from every line. |
| Root sections | Exactly one blank line before each root key (`config:`, `variables:`, `lists:`, …). |
| List sorting | Alphabetical sorting of blocks under `lists:` exists but is **off by default** (`rotationYaml.format.sortLists`). Do not sort — priority lists read better grouped by role. |

> [!NOTE]
> The extension's formatter counts the comment above a root key as ordinary content and
> will insert the blank line *between* the comment and the key, splitting a header from
> the block it documents. `lint_rotations.py` deliberately deviates: it rewinds past a
> contiguous comment block so the blank line lands above the comments.

## 2. Diagnostics — Errors

| Check | Trigger |
| --- | --- |
| Unbalanced parentheses | `(` count ≠ `)` count on an action line |
| Empty condition | `,if=` with nothing after it |
| Invalid operator sequence | 3+ consecutive `&` or `\|` |
| Missing spell name | Action line starting with `- ,` |
| Missing list name | `call_action_list` / `run_action_list` without `name=` |
| Empty `call=` | `call=` with no list name |
| Undefined list | `name=X` referencing a list not defined locally nor in `_shared.yaml` |

## 3. Diagnostics — Warnings

| Check | Trigger |
| --- | --- |
| Trailing operator | Condition ends in `&` or `\|` |
| Leading operator | `,if=&` or `,if=\|` — use `!` for negation |
| Undefined config | `config.X` where `X` is in neither the file's `config:` nor `_shared.yaml`'s `config_shared:` |
| Undefined variable | `var.X` / `variable.X` not defined in `variables:` nor by a `variable,name=X` action |
| Word operators | `and` → `&`, `or` → `\|`, `not X` → `!X` (skipped inside quoted strings) |
| Typos | `buf.` `debbuf.` `cooldonw.` `talant.` `health_pct` `target_health` `player_moving` `active_enemie` `remaning` |

## 4. Diagnostics — Info

- `.up=true` / `.down=true` — both already return boolean, drop the `=true`.
- `==` — the DSL uses a single `=` for equality.
- ` stack>` without a leading dot — probably meant `.stack>`.

## 5. Step options recognised by the extension

```
after  call  cast_remains  casting_check  chain  channel_remains  cycle  cycle_order
delay  empower_to  empowerto  for_next  global_delay  hotkey  ignore_blocked
ignore_cds_toggle  ignore_cooldown  ignore_movement  ignore_queue  ignore_usable
interrupt  line_cd  modifier  name  override  range_check  rangecheck  resource
target  use_off_gcd  use_while_casting
```

> [!WARNING]
> The Rotation Codex site documents `off_gcd=` and `snapshot=`, which are **not** in this
> table; the extension carries `use_off_gcd` and `use_while_casting`, which are not on the
> site. Both spellings appear in shipped community rotations. `lint_rotations.py` accepts
> both and only reports the mismatch under `--strict-options`.

## 6. Special actions (valid as an action name, not a spell)

```
trinket_1  trinket_2  weapon_onuse  wrist_onuse  helm_onuse  cloak_onuse  belt_onuse
healthstone  health_potion  mana_potion  combat_potion  augment_rune
target_enemy  target_mouseover  target_focus  attack_target  petattack
interact_target  interact_mouseover  loot_a_rang
variable  var  wait  return  stop_casting  queue_spell  pool_resource
call_action_list  run_action_list  call
focus_target  focus_mouseover  focus_party1-4  focus_raid1-40
one_button_assist  one_button_assist_lookup  use_item  use_items
```

## 7. Not covered by `lint_rotations.py`

- **Spell-name validation.** The extension checks every `buff.X` / `cooldown.X` / action
  name against a spell database it downloads at runtime. Without that database a typo is
  indistinguishable from a valid spell, so the check is omitted rather than guessed at.
- **`cfg.X` references.** The extension only validates the `config.X` spelling; `cfg.X`
  (used in `FerrazBalanceRaid.yaml`) passes unchecked in both.
- Alias-definition keys (`buff.foo.stack: …`) are skipped by the spell validators on the
  left-hand side of the colon, matching the extension.
