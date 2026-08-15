"""Standalone lint/format checker for Simia rotation YAML.

Mirrors the rules the rotation-yaml-intellisense VS Code extension (v1.4.0)
applies, so a file that is clean here is clean in the editor too. Everything is
reimplemented from the extension's diagnosticProvider/formatProvider — there is
no dependency on VS Code being installed.

Not covered: spell-name validation. The extension checks spell names against a
database it downloads at runtime; without it, `buff.foo.up` cannot be told apart
from a typo.

Usage:
    python lint_rotations.py                  # lint every Ferraz*.yaml
    python lint_rotations.py FILE [FILE...]
    python lint_rotations.py --fix FILE       # apply formatting fixes only
"""

import os
import re
import sys

SHARED_DIR = 'simia_data_dump'

STEP_OPTIONS = {
    'after', 'call', 'cast_remains', 'casting_check', 'chain', 'channel_remains',
    'cycle', 'cycle_order', 'delay', 'empower_to', 'empowerto', 'for_next',
    'global_delay', 'hotkey', 'ignore_blocked', 'ignore_cds_toggle',
    'ignore_cooldown', 'ignore_movement', 'ignore_queue', 'ignore_usable',
    'interrupt', 'line_cd', 'modifier', 'name', 'override', 'range_check',
    'rangecheck', 'resource', 'target', 'use_off_gcd', 'use_while_casting',
}
# Documented on the Rotation Codex site but absent from the extension's
# STEP_OPTIONS table. Accepted here, reported only under --strict-options.
EXTRA_STEP_OPTIONS = {'off_gcd', 'snapshot', 'sec', 'op', 'value', 'if', 'ignore_range'}

SPECIAL_ACTIONS = {
    'trinket_1', 'trinket_2', 'weapon_onuse', 'wrist_onuse', 'helm_onuse',
    'cloak_onuse', 'belt_onuse', 'healthstone', 'health_potion', 'mana_potion',
    'combat_potion', 'augment_rune', 'target_enemy', 'target_mouseover',
    'target_focus', 'attack_target', 'petattack', 'interact_target',
    'interact_mouseover', 'loot_a_rang', 'variable', 'var', 'wait', 'return',
    'stop_casting', 'queue_spell', 'pool_resource', 'call_action_list',
    'run_action_list', 'focus_target', 'focus_mouseover', 'one_button_assist',
    'one_button_assist_lookup', 'use_item', 'use_items', 'call',
}
SPECIAL_ACTIONS |= {'focus_party%d' % n for n in range(1, 5)}
SPECIAL_ACTIONS |= {'focus_raid%d' % n for n in range(1, 41)}

TYPOS = [
    (re.compile(r'\bbuf\.'), 'W', 'Did you mean "buff."?', False),
    (re.compile(r'\bdebbuf\.'), 'W', 'Did you mean "debuff."?', False),
    (re.compile(r'\bcooldonw\.'), 'W', 'Did you mean "cooldown."?', False),
    (re.compile(r'\btalant\.'), 'W', 'Did you mean "talent."?', False),
    (re.compile(r'\bhealth_pct\b'), 'W', 'Did you mean "health.pct"?', False),
    (re.compile(r'\btarget_health\b'), 'W', 'Did you mean "target.health.pct"?', False),
    (re.compile(r'\bplayer_moving\b'), 'W', 'Did you mean "player.moving"?', False),
    (re.compile(r'\bactive_enemie\b'), 'W', 'Did you mean "active_enemies"?', False),
    (re.compile(r'\bremaning\b'), 'W', 'Did you mean "remains"?', False),
    (re.compile(r'[^.]\bstack\b\s*>'), 'I', 'Did you mean ".stack>"?', False),
    (re.compile(r'==+'), 'I', 'Use single = for equality', False),
    (re.compile(r'\band\b', re.I), 'W', 'Use & for AND operator', True),
    (re.compile(r'\bor\b', re.I), 'W', 'Use | for OR operator', True),
    (re.compile(r'\bnot\s+\w', re.I), 'W', 'Use ! for NOT operator', True),
    # Reversed expression order: the catalog defines these as player.X, never
    # X.player (found live in two Ferraz files as `auto_combat.player`).
    (re.compile(r'\bauto_combat\.player\b'), 'W', 'Did you mean "player.auto_combat"?', False),
    (re.compile(r'\b(combat|moving|casting|channeling|stunned|rooted|silenced|'
                r'feared|dead|alive|aggro|mounted|solo|group)\.player\b'),
     'W', 'Expression order looks reversed — did you mean "player.X"?', False),
]

# From expression-catalog.json's config_widgets block (SIMIA_DOCUMENTATION.md
# section 5). Includes documented aliases.
KNOWN_WIDGET_TYPES = {
    'slider', 'checkbox', 'dropdown', 'multi_select', 'unit_select', 'toggle',
    'number', 'number_input', 'copy_text', 'copy', 'copytext', 'copy-text',
    'link', 'url', 'note', 'info', 'text', 'divider', 'separator', 'button',
}


def strip_inline_comment(text):
    """Drop a YAML inline comment, preserving column positions."""
    in_single = in_double = False
    for i, c in enumerate(text):
        if c == "'" and not in_double:
            in_single = not in_single
        elif c == '"' and not in_single:
            in_double = not in_double
        elif c == '#' and not in_single and not in_double:
            if i == 0 or text[i - 1].isspace():
                return text[:i]
    return text


def quoted_ranges(text):
    ranges, i = [], 0
    while i < len(text):
        if text[i] in '"\'':
            quote, start = text[i], i + 1
            i += 1
            while i < len(text):
                if text[i] == '\\' and i + 1 < len(text):
                    i += 2
                    continue
                if text[i] == quote:
                    ranges.append((start, i))
                    i += 1
                    break
                i += 1
        else:
            i += 1
    return ranges


ALIAS_KEY = re.compile(
    r'^(\s*(?:buff|debuff|cooldown|cooldown_bypass|dot|totem|talent|hero_tree|drw|nameplates)'
    r'\.[\w.]+:)')


def collect_block_names(lines, root_re, entry_re):
    """Names defined directly under a root-level section."""
    names, inside = set(), False
    for text in lines:
        if root_re.match(text):
            inside = True
            continue
        if inside and re.match(r'^[a-z_]+:\s*$', text) and not text.startswith(' '):
            inside = False
            continue
        if inside:
            m = entry_re.match(text)
            if m:
                names.add(m.group(1))
    return names


def load_shared(root):
    """Config vars and list names published by the _shared.yaml the client loads."""
    cfg, lists = set(), set()
    path = os.path.join(root, SHARED_DIR, '_shared.yaml')
    if not os.path.isfile(path):
        return cfg, lists
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    cfg = collect_block_names(lines, re.compile(r'^config_shared:\s*$'),
                              re.compile(r'^\s{2}(\w+):\s*$'))
    lists = collect_block_names(lines, re.compile(r'^lists:\s*$'),
                                re.compile(r'^\s{2}(\w+):\s*$'))
    return cfg, lists


def lint(path, shared_cfg, shared_lists, strict_options=False):
    with open(path, encoding='utf-8') as fh:
        raw = fh.read()
    lines = raw.split('\n')
    out = []

    def add(n, sev, msg):
        out.append((n + 1, sev, msg))

    defined_lists = collect_block_names(lines, re.compile(r'^lists:\s*$'),
                                        re.compile(r'^\s{2}(\w+):\s*$')) | shared_lists
    defined_cfg = collect_block_names(lines, re.compile(r'^config:\s*$'),
                                      re.compile(r'^\s{2}(\w+):\s*$')) | shared_cfg
    # Line range covered by the top-level `config:` block, so `type:` checks
    # do not fire on unrelated uses of the word elsewhere in the file.
    config_start = None
    for i, text in enumerate(lines):
        if re.match(r'^config:\s*$', text):
            config_start = i
            break
    config_lines = set()
    if config_start is not None:
        for i in range(config_start + 1, len(lines)):
            if re.match(r'^[a-z_]+:\s*$', lines[i]):
                break
            config_lines.add(i)

    defined_vars = collect_block_names(lines, re.compile(r'^(?:variables|variable|var):\s*$'),
                                       re.compile(r'^\s{2}(\w+):'))
    for text in lines:
        m = re.match(r'^\s*-\s*(?:variable|var),name=(\w+)', text)
        if m:
            defined_vars.add(m.group(1))

    # Body lines of a YAML block scalar (`key: |`) are prose, not expressions.
    # Without this the word-operator checks fire on ordinary English: "Lunation
    # and Galactic Guardian" reads as a missing `&`. The extension has the same
    # false positive, so prose in a block scalar is best kept free of the words
    # "and", "or" and "not" anyway.
    prose = set()
    block_indent = None
    for n, text in enumerate(lines):
        if block_indent is not None:
            indent = len(text) - len(text.lstrip(' '))
            if text.strip() and indent <= block_indent:
                block_indent = None
            else:
                prose.add(n)
                continue
        m = re.match(r'^(\s*)[\w.]+:\s*[|>][-+]?\s*$', text)
        if m:
            block_indent = len(m.group(1))

    last_nonempty = -1
    for n, rawline in enumerate(lines):
        # --- formatting (applies to every line, comments included) ---
        if rawline != rawline.rstrip():
            add(n, 'F', 'Trailing whitespace')
        if rawline.startswith('\t') or '\t' in rawline:
            add(n, 'F', 'Tab character (indentation must be 2 spaces)')
        indent = len(rawline) - len(rawline.lstrip(' '))
        if rawline.strip() and indent % 2:
            add(n, 'F', 'Indent of %d is not a multiple of 2' % indent)
        if re.match(r'^[a-z_]+:\s*$', rawline) and last_nonempty >= 0:
            # A comment block directly above a root key documents that key, so the
            # blank line belongs above the comment, not between it and the key.
            # (The extension's formatter does not make this distinction and would
            # split the two apart.)
            anchor = n
            while anchor - 1 >= 0 and lines[anchor - 1].strip().startswith('#'):
                anchor -= 1
            prev = last_nonempty if anchor == n else anchor - 1
            while prev >= 0 and not lines[prev].strip():
                prev -= 1
            if prev >= 0:
                gap = anchor - prev
                if gap == 1:
                    add(n, 'F', 'Root section needs one blank line before it')
                elif gap > 2:
                    add(n, 'F', 'Root section has %d blank lines before it (want 1)' % (gap - 1))
        if rawline.strip():
            last_nonempty = n

        if not rawline.strip() or rawline.strip().startswith('#'):
            continue

        text = strip_inline_comment(rawline)
        skip_before = len(ALIAS_KEY.match(text).group(1)) if ALIAS_KEY.match(text) else 0

        # --- action-line rules ---
        m = re.match(r'^\s*-\s*(.+)$', text)
        if m:
            body = m.group(1)
            op, cl = body.count('('), body.count(')')
            if op != cl:
                add(n, 'E', 'Unbalanced parentheses: %d opening, %d closing' % (op, cl))
            if re.search(r',if=\s*(,|$)', body):
                add(n, 'E', 'Empty condition after if=')
            bad = re.search(r'[&|]{3,}', body)
            if bad:
                add(n, 'E', 'Invalid operator sequence "%s"' % bad.group(0))
            if re.search(r'[&|]\s*(,|$)', body):
                add(n, 'W', 'Condition ends with an operator')
            if re.search(r',if=[&|]', body):
                add(n, 'W', 'Condition starts with an operator (use ! for negation)')
            if re.search(r'\.up\s*=\s*true', body, re.I):
                add(n, 'I', '.up already returns boolean, drop the =true')
            if re.search(r'\.down\s*=\s*true', body, re.I):
                add(n, 'I', '.down already returns boolean, drop the =true')
            if re.match(r'^\s*-\s*,', text):
                add(n, 'E', 'Missing spell name before comma')
            if body.startswith(('call_action_list', 'run_action_list')) and 'name=' not in body:
                add(n, 'E', 'call_action_list/run_action_list requires name= parameter')
            call_alias = re.search(r'\bcall=(\w*)', body)
            if call_alias and not call_alias.group(1):
                add(n, 'E', 'call= requires a list name')
            ref = re.search(r'(?:call|run)_action_list.*name=(\w+)', body) or \
                (call_alias if call_alias and call_alias.group(1) else None)
            if ref:
                name = ref.group(1)
                if name not in defined_lists:
                    add(n, 'E', 'Action list "%s" is not defined' % name)
            if strict_options:
                for opt in re.findall(r',(\w+)=', body):
                    if opt not in STEP_OPTIONS and opt not in EXTRA_STEP_OPTIONS:
                        add(n, 'I', 'Step option "%s" is not in the extension table' % opt)

        # --- config widget type ---
        if n in config_lines:
            wm = re.match(r'^\s*type:\s*(\S+)\s*$', text)
            if wm and wm.group(1).strip('"\'') not in KNOWN_WIDGET_TYPES:
                add(n, 'W', 'Unknown config widget type "%s"' % wm.group(1))

        # --- reference rules (every line) ---
        for mm in re.finditer(r'\bconfig\.(\w+)', text):
            if mm.group(1) not in defined_cfg:
                add(n, 'W', 'Config variable "%s" is not defined' % mm.group(1))
        for mm in re.finditer(r'\b(?:var|variable)\.(\w+)', text):
            if mm.group(1) not in defined_vars:
                add(n, 'W', 'Variable "%s" is not defined' % mm.group(1))

        # --- typos ---
        if n in prose:
            continue
        ranges = quoted_ranges(text)
        for pattern, sev, msg, skip_strings in TYPOS:
            for mm in pattern.finditer(text):
                if mm.start() < skip_before:
                    continue
                if skip_strings and any(s <= mm.start() < e for s, e in ranges):
                    continue
                add(n, sev, '%s  (at "%s")' % (msg, mm.group(0).strip()))

    return sorted(out)


def fix_format(path):
    """Apply the formatter's rules: tabs -> 2 spaces, trim trailing whitespace,
    exactly one blank line before each root section."""
    with open(path, encoding='utf-8', newline='') as fh:
        raw = fh.read()
    eol = '\r\n' if raw.count('\r\n') > raw.count('\n') - raw.count('\r\n') else '\n'
    lines = raw.replace('\r\n', '\n').split('\n')
    lines = [re.sub(r'^\t+', lambda m: '  ' * len(m.group(0)), ln).rstrip() for ln in lines]
    out, seen_content = [], False
    for ln in lines:
        if re.match(r'^[a-z_]+:\s*$', ln) and seen_content:
            # Rewind past the comment block that documents this key, so the blank
            # line lands above the comments instead of splitting them off.
            insert_at = len(out)
            while insert_at - 1 >= 0 and out[insert_at - 1].strip().startswith('#'):
                insert_at -= 1
            while insert_at - 1 >= 0 and out[insert_at - 1] == '':
                out.pop(insert_at - 1)
                insert_at -= 1
            if insert_at > 0:
                out.insert(insert_at, '')
        out.append(ln)
        if ln.strip():
            seen_content = True
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(eol.join(out))


SEVERITY = {'E': 'error', 'W': 'warning', 'I': 'info', 'F': 'format'}


def main(argv):
    root = os.path.dirname(os.path.abspath(__file__))
    do_fix = '--fix' in argv
    strict = '--strict-options' in argv
    files = [a for a in argv if not a.startswith('-')]
    if not files:
        files = sorted(f for f in os.listdir(root)
                       if f.startswith('Ferraz') and f.endswith('.yaml'))
    shared_cfg, shared_lists = load_shared(root)

    total = 0
    for f in files:
        path = f if os.path.isabs(f) else os.path.join(root, f)
        if do_fix:
            fix_format(path)
        findings = lint(path, shared_cfg, shared_lists, strict)
        total += sum(1 for _, s, _ in findings if s in 'EW')
        if findings:
            print('\n%s' % os.path.basename(path))
            for line, sev, msg in findings:
                print('  %s:%d  %-7s %s' % (os.path.basename(path), line, SEVERITY[sev], msg))
        else:
            print('\n%s — clean' % os.path.basename(path))
    print('\n%d error/warning finding(s) across %d file(s).' % (total, len(files)))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
