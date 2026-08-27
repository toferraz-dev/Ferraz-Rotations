"""
Simia rotation interpreter and fault finder.

WHAT THIS IS. It parses a rotation YAML, evaluates its expressions against a
modelled game state, and steps `main` one tick at a time the way the addon
does: first matching line wins, `return` ends the pass, `call_action_list`
descends into another list.

WHAT IT IS FOR. Not throughput - SimulationCraft does that, and a hand-written
combat model would mostly measure its own assumptions. This looks for the
fault classes that actually recur in this repo:

  LOOP       the environment is frozen and the rotation still never settles.
             A sane priority converges on a filler; one that alternates
             shapeshifts forever is the Bear/Moonkin bug.
  STALL      in combat, alive, valid target, and nothing is ever suggested.
  DEAD LINE  a line that never fires in any scenario of the sweep.
  ALWAYS     a gate true in every scenario - "what makes this false?"

HOW UNKNOWNS ARE HANDLED. Simia has ~634 expressions; this models the ones
these files use. Anything else - cycle.*, group.count(...), mouseover.*,
interrupt.*.check, trinket_1.ready - evaluates to UNKNOWN, and UNKNOWN is
treated as false, so those lines do not fire. That is a real limit, not a
hidden one: --unknowns prints every expression that went unresolved.

So a clean report means "no fault found in what is modelled". It never means
the rotation is correct.
"""
import argparse
import random
import re
import sys
import traceback
from collections import defaultdict

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")

UNKNOWN = object()


# ---------------------------------------------------------------- expressions

TOKEN = re.compile(r"""
    \s*(?:
      (?P<num>\d+(?:\.\d+)?)
    | (?P<name>[A-Za-z_][A-Za-z_0-9.]*)
    | (?P<op><=|>=|!=|>\?|<\?|=|<|>|&|\||!|\(|\)|,|\+|-|\*|/|%)
    )""", re.X)


def tokenize(s):
    out, i = [], 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        m = TOKEN.match(s, i)
        if not m:
            raise ValueError("bad token at %d in %r" % (i, s))
        i = m.end()
        if m.group('num'):
            out.append(('num', float(m.group('num'))))
        elif m.group('name'):
            out.append(('name', m.group('name')))
        else:
            out.append(('op', m.group('op')))
    return out


class Parser:
    """`|` lowest, then `&`, then comparison, then unary `!`, then atom."""

    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, val=None):
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        if val and tok[1] != val:
            raise ValueError("expected %r got %r" % (val, tok[1]))
        self.i += 1
        return tok

    def parse(self):
        n = self.or_()
        if self.peek():
            raise ValueError("trailing tokens: %r" % (self.t[self.i:],))
        return n

    def or_(self):
        n = self.and_()
        while self.peek() == ('op', '|'):
            self.eat()
            n = ('or', n, self.and_())
        return n

    def and_(self):
        n = self.cmp_()
        while self.peek() == ('op', '&'):
            self.eat()
            n = ('and', n, self.cmp_())
        return n

    def cmp_(self):
        n = self.add_()
        tok = self.peek()
        if tok and tok[0] == 'op' and tok[1] in ('<', '>', '<=', '>=', '=', '!='):
            op = self.eat()[1]
            return ('cmp', op, n, self.add_())
        return n

    def add_(self):
        n = self.mul_()
        while self.peek() and self.peek()[0] == 'op' and self.peek()[1] in ('+', '-', '>?', '<?'):
            op = self.eat()[1]
            n = ('arith', op, n, self.mul_())
        return n

    def mul_(self):
        n = self.unary()
        while self.peek() and self.peek()[0] == 'op' and self.peek()[1] in ('*', '/', '%'):
            op = self.eat()[1]
            n = ('arith', op, n, self.unary())
        return n

    def unary(self):
        if self.peek() == ('op', '-'):
            self.eat()
            return ('arith', '-', ('num', 0.0), self.unary())
        if self.peek() == ('op', '!'):
            self.eat()
            return ('not', self.unary())
        return self.atom()

    def atom(self):
        tok = self.peek()
        if tok == ('op', '('):
            self.eat()
            n = self.or_()
            self.eat(')')
            return n
        tok = self.eat()
        if tok[0] == 'num':
            return ('num', tok[1])
        name = tok[1]
        if self.peek() == ('op', '('):           # .has(2), group.count(...)
            self.eat()
            depth, start = 1, self.i
            while depth:
                t = self.eat()
                if t == ('op', '('):
                    depth += 1
                elif t == ('op', ')'):
                    depth -= 1
            return ('call', name, self.t[start:self.i - 1])
        return ('ref', name)


_CACHE = {}


def parse_expr(s):
    if s not in _CACHE:
        _CACHE[s] = Parser(tokenize(s)).parse()
    return _CACHE[s]


# --------------------------------------------------------------------- state

FORM_BUFF = {'bear_form': 'bear', 'cat_form': 'cat',
             'moonkin_form': 'moonkin', 'travel_form': 'travel'}


class State:
    """Only what the rotation can read or change is modelled."""

    def __init__(self, config, talents):
        self.config = dict(config)
        self.talents = set(talents)
        self.health = 100.0
        self.health_effective = None       # None -> mirrors health
        self.form = 'moonkin'              # moonkin|bear|cat|travel|caster
        self.buffs = set()
        self.cds = {}                      # name -> seconds remaining
        self.charges = defaultdict(lambda: 1)
        self.casting = False
        self.channeling = False
        self.combat = True
        self.moving = False
        self.standing_time = 99.0
        self.enemies40 = 3
        self.enemies8 = 3
        self.astral_power = 50.0
        self.dead = False
        self.mounted = False
        self.pins = {}                     # expression -> value

    def eff(self):
        return self.health if self.health_effective is None else self.health_effective

    def key(self):
        return (round(self.health, 2), self.form, tuple(sorted(self.buffs)),
                self.casting, self.channeling, round(self.astral_power, 1),
                tuple(sorted((k, round(v, 1)) for k, v in self.cds.items())))

    def clone(self):
        s = State(self.config, self.talents)
        s.health = self.health
        s.health_effective = self.health_effective
        s.form = self.form
        s.buffs = set(self.buffs)
        s.cds = dict(self.cds)
        s.charges = defaultdict(lambda: 1, self.charges)
        s.casting = self.casting
        s.channeling = self.channeling
        s.combat = self.combat
        s.moving = self.moving
        s.standing_time = self.standing_time
        s.enemies40 = self.enemies40
        s.enemies8 = self.enemies8
        s.astral_power = self.astral_power
        s.dead = self.dead
        s.mounted = self.mounted
        s.pins = dict(self.pins)
        return s


def truthy(v):
    if v is UNKNOWN:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    return bool(v)


def numeric(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return 0.0


class Evaluator:
    def __init__(self, state, variables, unknown_sink):
        self.s = state
        self.vars = variables
        self.unknown = unknown_sink
        self._stack = set()

    def _buff(self, name):
        if name in FORM_BUFF:
            return self.s.form == FORM_BUFF[name]
        return name in self.s.buffs

    def ev(self, n):
        t = n[0]
        if t == 'num':
            return n[1]
        if t == 'not':
            v = self.ev(n[1])
            return UNKNOWN if v is UNKNOWN else (not truthy(v))
        if t == 'and':
            a = self.ev(n[1])
            if a is not UNKNOWN and not truthy(a):
                return False
            b = self.ev(n[2])
            if b is not UNKNOWN and not truthy(b):
                return False
            return UNKNOWN if (a is UNKNOWN or b is UNKNOWN) else True
        if t == 'or':
            a = self.ev(n[1])
            if a is not UNKNOWN and truthy(a):
                return True
            b = self.ev(n[2])
            if b is not UNKNOWN and truthy(b):
                return True
            return UNKNOWN if (a is UNKNOWN or b is UNKNOWN) else False
        if t == 'cmp':
            _, op, l, r = n
            a, b = self.ev(l), self.ev(r)
            if a is UNKNOWN or b is UNKNOWN:
                return UNKNOWN
            a, b = numeric(a), numeric(b)
            return {'<': a < b, '>': a > b, '<=': a <= b, '>=': a >= b,
                    '=': a == b, '!=': a != b}[op]
        if t == 'arith':
            _, op, l, r = n
            a, b = self.ev(l), self.ev(r)
            if a is UNKNOWN or b is UNKNOWN:
                return UNKNOWN
            a, b = numeric(a), numeric(b)
            if op == '/' and b == 0:
                return UNKNOWN
            return {'+': a + b, '-': a - b, '*': a * b,
                    '>?': max(a, b), '<?': min(a, b),
                    '/': a / b if b else 0.0, '%': a % b if b else 0.0}[op]
        if t == 'call':
            return self.call(n[1], n[2])
        return self.ref(n[1])

    def call(self, name, args):
        if name.endswith('.has') and name.startswith('config.'):
            val = self.s.config.get(name[7:-4])
            if isinstance(val, list) and args:
                return args[0][1] in val
        self.unknown.add(name + '(...)')
        return UNKNOWN

    def ref(self, name):
        s = self.s
        if name in s.pins:
            return s.pins[name]

        if name.startswith('config.'):
            v = s.config.get(name[7:])
            if v is None:
                self.unknown.add(name)
                return UNKNOWN
            return v

        if name.startswith('var.') or name.startswith('variable.'):
            key = name.split('.', 1)[1]
            if key in self._stack:
                return UNKNOWN
            expr = self.vars.get(key)
            if expr is None:
                self.unknown.add(name)
                return UNKNOWN
            self._stack.add(key)
            try:
                return self.ev(parse_expr(str(expr)))
            except ValueError as e:
                self.unknown.add('%s [unparsed: %s]' % (name, e))
                return UNKNOWN
            finally:
                self._stack.discard(key)

        if name.startswith('talent.'):
            return name[7:] in s.talents

        if name.startswith('buff.'):
            p = name.split('.')
            b = p[1]
            prop = p[2] if len(p) > 2 else 'up'
            if prop == 'up' or prop == 'react':
                return self._buff(b)
            if prop == 'down':
                return not self._buff(b)
            if prop == 'stack':
                return 1.0 if self._buff(b) else 0.0
            if prop == 'remains':
                return 10.0 if self._buff(b) else 0.0

        if name.startswith('cooldown.'):
            p = name.split('.')
            c = p[1]
            prop = p[2] if len(p) > 2 else 'ready'
            rem = s.cds.get(c, 0.0)
            if prop == 'ready':
                return rem <= 0
            if prop == 'remains':
                return rem
            if prop in ('charges', 'charges_fractional'):
                return float(s.charges[c]) if rem <= 0 else 0.0

        simple = {
            'health.pct': s.health,
            'health.effective.pct': s.eff(),
            'player.combat': s.combat,
            'player.casting': s.casting,
            'player.channeling': s.channeling,
            'player.moving': s.moving,
            'player.dead': s.dead,
            'player.standing.time': s.standing_time,
            'mounted': s.mounted,
            'astral_power': s.astral_power,
            'astral_power.deficit': 100.0 - s.astral_power,
            'enemies.combat.40y': float(s.enemies40),
            'enemies.combat.8y': float(s.enemies8),
        }
        if name in simple:
            return simple[name]

        self.unknown.add(name)
        return UNKNOWN


# -------------------------------------------------------------------- effects

# Spells that leave you in caster form when cast from a shapeshift. Fluid Form
# turns some of these into a shift instead - handled in apply().
DOTS = {'moonfire', 'sunfire', 'rake', 'rip', 'thrash', 'immolate',
        'stellar_flare', 'lifebloom', 'rejuvenation', 'regrowth'}

CASTER_SPELLS = {
    'starfall', 'starsurge', 'moonfire', 'sunfire', 'lunar_eclipse',
    'solar_eclipse', 'fury_of_elune', 'incarnation_chosen_of_elune',
    'celestial_alignment', 'stellar_flare', 'rejuvenation', 'regrowth',
    'wild_growth', 'swiftmend', 'lifebloom', 'efflorescence', 'tranquility',
    'nourish', 'mark_of_the_wild', 'solar_beam', 'remove_corruption',
    'soothe', 'thorn_bloom', 'rebirth', 'revive',
}
# Fluid Form: Wrath and Starfire shift you into Moonkin instead of caster.
FLUID_TO_MOONKIN = {'wrath', 'starfire'}

# Form-cancelling is per FORM, not per spell.
#
# Moonfire carries SPELL_ATTR0_NOT_SHAPESHIFTED (16) exactly like Starfall and
# Solar Beam, so reading the attribute made it look form-cancelling everywhere
# and the fuzzer reported a Bear/Moonfire loop in FerrazGuardianElune.yaml that
# cannot happen. Per the author:
#
#   Bear    (Guardian)  Moonfire does NOT cancel
#   Moonkin (Balance)   Moonfire does NOT cancel
#   Cat     (Feral)     probably DOES - author unsure, and Lunar Inspiration
#                       is the talent that makes it castable in Cat, so that
#                       is what the exception keys on
#
# Moonkin needs no entry: nothing in this model cancels it, because the
# cancel rule only ever fires from bear, cat or travel.
#
# Second time trusting SimC spell data over the game produced a wrong answer
# here - see the Fluid Form note in .agents/SIMIA_EXPERT_PROMPT.md. Attributes
# describe what the base spell requires, not what the class ends up able to do.
SAFE_FROM_FORM = {
    'moonfire': {'bear'},
}
# (spell, form) -> talents that make it safe there.
SAFE_WITH_TALENT = {
    ('moonfire', 'cat'): ('lunar_inspiration',),
}
# Off-GCD / item lines that change nothing this model tracks.
NEUTRAL = {
    'barkskin', 'healthstone', 'health_potion', 'combat_potion', 'trinket_1',
    'trinket_2', 'queue_spell', 'interact_target', 'interact_mouseover',
    'pool_resource', 'target_enemy', 'ironbark', 'innervate', 'natures_swiftness',
    'frenzied_regeneration', 'heart_of_the_wild', 'incapacitating_roar',
    'attack_target', 'stampeding_roar',
}


def land_dot(state, base):
    """A DoT the rotation just cast is now on the target.

    Without this the gate that let the line fire - dot.X.refreshable,
    mouseover.debuff.X.down - stays pinned true forever, and the line refires
    every tick. That is not a rotation loop, it is the environment being
    frozen against the rotation's own action.
    """
    for k in list(state.pins):
        if ('debuff.%s.' % base) in k or ('dot.%s.' % base) in k:
            if k.endswith(('.down', '.refreshable')):
                state.pins[k] = False
            elif k.endswith('.up'):
                state.pins[k] = True


def apply_effect(state, spell):
    """Mutate state the way the game would. Returns a short description."""
    s = state
    base = spell.split('.')[0]
    if base in DOTS:
        land_dot(s, base)

    if base == 'stop_casting':
        s.casting = False
        s.channeling = False
        return 'cast ended'
    if base in FORM_BUFF:
        if s.form == FORM_BUFF[base]:
            return 'no-op (already in form)'
        s.form = FORM_BUFF[base]
        return 'form -> ' + s.form
    if base in NEUTRAL:
        return ''
    if base in FLUID_TO_MOONKIN:
        if 'fluid_form' in s.talents:
            if s.form != 'moonkin':
                s.form = 'moonkin'
                return 'form -> moonkin (Fluid Form)'
            return ''
        if s.form != 'caster':
            s.form = 'caster'
            return 'form -> caster'
        return ''
    if s.form in SAFE_FROM_FORM.get(base, ()):
        return ''
    if any(t in s.talents for t in SAFE_WITH_TALENT.get((base, s.form), ())):
        return ''
    if base in CASTER_SPELLS or base.isdigit():
        if s.form in ('bear', 'cat', 'travel'):
            s.form = 'caster'
            return 'form -> caster (cast cancelled the form)'
        return ''
    return ''


# --------------------------------------------------------------------- engine

class Rotation:
    def __init__(self, path):
        with open(path, encoding='utf-8') as fh:
            self.doc = yaml.safe_load(fh)
        self.path = path
        self.lists = self.doc.get('lists') or {}
        self.vars = self.doc.get('variables') or {}
        self.entry = self.doc.get('entry', 'main')
        self.config_defaults = {}
        for k, v in (self.doc.get('config') or {}).items():
            if isinstance(v, dict) and 'default' in v:
                self.config_defaults[k] = v['default']
        self.actions = {}
        for name, lines in self.lists.items():
            self.actions[name] = [parse_action(name, i, l)
                                  for i, l in enumerate(lines or [])
                                  if isinstance(l, str)]

    def all_actions(self):
        for lst in self.actions.values():
            for a in lst:
                yield a


class Action:
    __slots__ = ('list', 'index', 'spell', 'mods', 'cond', 'raw', 'name')

    def __init__(self, lst, index, spell, mods, cond, raw, name):
        self.list, self.index, self.spell = lst, index, spell
        self.mods, self.cond, self.raw, self.name = mods, cond, raw, name

    def label(self):
        return '%s[%d] %s' % (self.list, self.index, self.name or self.spell)


def split_top(s, sep=','):
    out, depth, cur = [], 0, ''
    quoted = False
    for ch in s:
        if ch == '"':
            quoted = not quoted
        if not quoted:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif ch == sep and depth == 0:
                out.append(cur)
                cur = ''
                continue
        cur += ch
    out.append(cur)
    return out


def parse_action(lst, index, line):
    parts = split_top(line)
    spell = parts[0].strip()
    mods, cond, name = {}, None, None
    for p in parts[1:]:
        p = p.strip()
        if p.startswith('if='):
            cond = p[3:]
        elif p.startswith('name='):
            name = p[5:].strip('"')
        elif '=' in p:
            k, v = p.split('=', 1)
            mods[k.strip()] = v.strip()
        else:
            mods[p] = 'true'
    return Action(lst, index, spell, mods, cond, line, name)


class Engine:
    def __init__(self, rot, state):
        self.rot = rot
        self.state = state
        self.unknown = set()
        self.errors = []

    def cond_true(self, action):
        if action.cond is None:
            return True
        try:
            node = parse_expr(action.cond)
        except ValueError as e:
            self.errors.append('%s: %s' % (action.label(), e))
            return False
        ev = Evaluator(self.state, self.rot.vars, self.unknown)
        return truthy(ev.ev(node))

    def step(self, list_name=None, depth=0, fired=None):
        """One rotation pass.

        Returns (Action|None, effect, off_gcd_list). Lines carrying
        off_gcd=true do NOT end the pass in the addon - they fire alongside
        the global. Treating them as terminal made queue_spell swallow every
        tick and left the rest of the file unexplored.
        """
        if fired is None:
            fired = []
        if depth > 12:
            return None, 'recursion guard', fired
        name = list_name or self.rot.entry
        for a in self.rot.actions.get(name, []):
            if not self.cond_true(a):
                continue
            base = a.spell.split('.')[0]
            if base == 'return':
                return None, 'return @ ' + a.label(), fired
            if base == 'call_action_list':
                # The target list is written `name=aoe`, which parse_action
                # puts in .name, NOT in .mods. Reading mods here returned
                # None, and step(None) restarts `main` - a re-entry that blows
                # up exponentially instead of erroring.
                target = a.mods.get('list') or a.name
                if target not in self.rot.actions:
                    self.errors.append('%s: no such list %r'
                                       % (a.label(), target))
                    continue
                act, eff, fired = self.step(target, depth + 1, fired)
                if act is not None or eff.startswith('return'):
                    return act, eff, fired
                continue
            if base == 'variable':
                continue
            if a.mods.get('off_gcd') == 'true' or base in OFF_GCD_ALWAYS:
                fired.append((a, apply_effect(self.state, a.spell)))
                continue
            return a, apply_effect(self.state, a.spell), fired
        return None, 'no action', fired


OFF_GCD_ALWAYS = {'queue_spell', 'pool_resource'}


# ------------------------------------------------------------------ scenarios

def build_scenarios(rot, extra_talents):
    """Frozen environments.

    Health is the axis most faults live on, so it is sampled densely around
    the defensive thresholds (30 and 35 in the Balance files). The rest exist
    so CD- and resource-gated lines get a chance to fire; without them almost
    every line reads as dead.
    """
    grid = []
    for health in (100, 60, 40, 36, 34, 32, 30, 28, 20, 10):
        for enemies in (1, 3):
            for casting in (False, True):
                for hotw in (False, True):
                    for ap in (0.0, 55.0, 95.0):
                        for cds_up in (True, False):
                            grid.append((health, enemies, casting, hotw, ap,
                                         cds_up))
    out = []
    for health, enemies, casting, hotw, ap, cds_up in grid:
        st = State(rot.config_defaults, extra_talents)
        st.health = float(health)
        st.enemies40 = st.enemies8 = enemies
        st.casting = casting
        st.astral_power = ap
        st.config['hotw_bear_defensive'] = hotw
        if not cds_up:
            for cd in ('frenzied_regeneration', 'heart_of_the_wild', 'barkskin',
                       'incarnation_chosen_of_elune', 'fury_of_elune',
                       'lunar_eclipse', 'swiftmend', 'rebirth'):
                st.cds[cd] = 30.0
        out.append(('hp=%-3d n=%d cast=%-5s hotw=%-5s ap=%-4.0f cds=%s'
                    % (health, enemies, casting, hotw, ap,
                       'up' if cds_up else 'down'), st))
    return out


def run_scenario(rot, state, ticks):
    """Step with the environment frozen.

    Cycle detection keys on what the ROTATION itself mutates - form, buffs,
    casting - not on the environment, which never moves here. A cycle is only
    reported as a LOOP when it contains a form change: converging on a filler
    is correct, ping-ponging between shapeshifts is the bug this exists to
    find.
    """
    eng = Engine(rot, state)
    trace, seen = [], {}
    for t in range(ticks):
        k = (state.form, tuple(sorted(state.buffs)), state.casting,
             state.channeling)
        if k in seen:
            cycle = trace[seen[k]:]
            shifts = [e for _, e, _ in cycle if 'form ->' in e]
            if shifts:
                return trace, ('LOOP', cycle)
            return trace, ('SETTLED', cycle)
        seen[k] = t
        action, effect, off = eng.step()
        trace.append((action, effect, off))
    acted = [a for a, _, off in trace if a is not None or off]
    if not acted and state.combat and not state.casting:
        return trace, ('STALL', trace)
    return trace, ('OPEN', [])



# ----------------------------------------------------------------- fuzzing

def walk(node, out):
    if not isinstance(node, tuple):
        return
    if node[0] == 'ref':
        out.add(node[1])
    elif node[0] == 'call':
        out.add(node[1] + '(...)')
    for x in node[1:]:
        walk(x, out)


def collect_names(rot):
    """Every identifier the file actually reads, so the fuzzer randomises the
    things this rotation cares about instead of a generic guess."""
    refs = set()
    for a in rot.all_actions():
        if a.cond:
            try:
                walk(parse_expr(a.cond), refs)
            except ValueError:
                pass
    for v in rot.vars.values():
        try:
            walk(parse_expr(str(v)), refs)
        except ValueError:
            pass
    buffs, cds, talents, opaque = set(), set(), set(), set()
    for r in refs:
        if r.startswith('buff.'):
            buffs.add(r.split('.')[1])
        elif r.startswith('cooldown.'):
            cds.add(r.split('.')[1])
        elif r.startswith('talent.'):
            talents.add(r[7:])
        elif not r.startswith(('config.', 'var.', 'variable.')):
            if r not in KNOWN_SIMPLE:
                opaque.add(r)
    return dict(buffs=sorted(buffs), cds=sorted(cds),
                talents=sorted(talents), opaque=sorted(opaque))


KNOWN_SIMPLE = {
    'health.pct', 'health.effective.pct', 'player.combat', 'player.casting',
    'player.channeling', 'player.moving', 'player.dead', 'player.standing.time',
    'mounted', 'astral_power', 'astral_power.deficit',
    'enemies.combat.40y', 'enemies.combat.8y',
}


def random_state(rot, rng, names):
    """A random but internally consistent game state.

    Opaque expressions - the ones this model cannot evaluate - are PINNED
    randomly instead of being forced false. That is the whole point of the
    fuzzer: the grid sweep only ever explored the false branch of every
    cycle.*, mouseover.* and interrupt.* gate in the file.
    """
    st = State(rot.config_defaults, [])
    st.health = round(rng.uniform(1, 100), 1)
    st.health_effective = round(
        min(100.0, max(0.0, st.health + rng.uniform(-15, 15))), 1)
    st.form = rng.choice(['moonkin', 'bear', 'cat', 'caster', 'travel'])
    st.buffs = {b for b in names['buffs']
                if b not in FORM_BUFF and rng.random() < 0.35}
    st.cds = {c: (0.0 if rng.random() < 0.5 else round(rng.uniform(1, 120), 1))
              for c in names['cds']}
    for c in names['cds']:
        st.charges[c] = rng.choice([0, 1, 1, 2])
    st.casting = rng.random() < 0.35
    st.channeling = rng.random() < 0.15
    st.combat = rng.random() < 0.85
    st.moving = rng.random() < 0.3
    st.standing_time = rng.choice([0.0, 0.5, 1.0, 3.0, 30.0])
    st.enemies40 = rng.choice([0, 1, 2, 3, 5, 8])
    st.enemies8 = min(st.enemies40, rng.choice([0, 1, 2, 3, 5]))
    st.astral_power = round(rng.uniform(0, 100), 1)
    st.dead = False
    st.mounted = False
    st.talents = {t for t in names['talents'] if rng.random() < 0.5}

    for k, v in (rot.doc.get('config') or {}).items():
        if not isinstance(v, dict):
            continue
        t = v.get('type')
        if t == 'checkbox':
            st.config[k] = rng.random() < 0.5
        elif t == 'slider':
            lo, hi = v.get('min', 0), v.get('max', 100)
            st.config[k] = rng.randint(int(lo), int(hi))
        elif t == 'multi_select':
            vals = [o['value'] for o in v.get('options', [])
                    if isinstance(o, dict) and 'value' in o]
            st.config[k] = [x for x in vals if rng.random() < 0.5]
        elif t == 'toggle':
            st.config[k] = rng.random() < 0.5

    # Biased, not uniform. Pinning target.valid / target.attackable false at
    # the same rate as everything else killed ~92% of cases at the target
    # guards in `main`, so the fuzzer tested almost nothing and reported a
    # clean 100% SETTLED on a file with a known loop in it. These describe
    # "you have a live enemy targeted", which is the normal case.
    st.pins = {}
    for o in names['opaque']:
        st.pins[o] = rng.random() < PIN_BIAS.get(o, 0.35)
    return st


# Loops that only exist because the environment is frozen.
#
# Root Cleanse (Balance/Feral) and Shapeshift Clear (Restoration) both shift
# out of a root. Their gate - debuff_list.freedom / player.rooted - is Simia's
# own list of what a shift actually removes, so in game the first shift clears
# it and the condition falls away on its own. This model holds every pinned
# expression still for the whole run, so the root never goes and the shift
# keeps re-arming. Confirmed with the author as a modelling artifact, not a
# rotation fault.
#
# The suppression is by line NAME, so it only silences these specific lines.
# A new shapeshift loop somewhere else still reports.
BENIGN_MARKERS = ('Root Cleanse', 'Shapeshift Clear')


# Probability that an unmodelled expression is pinned true.
PIN_BIAS = {
    'target.valid': 0.9, 'target.attackable': 0.95, 'target.dead': 0.03,
    'target.exists': 0.95, 'target.enemy': 0.95, 'target.combat': 0.85,
    'state.rotation': 0.98, 'state.blocked_inputs': 0.02,
    'target.boss': 0.25, 'target.time_to_die': 0.5,
    'mouseover.exists': 0.3, 'mouseover.dead': 0.05,
}


def fuzz(rot, count, seed, ticks, verbose=False):
    """Random states, one run each. Reports anything that is not a clean
    settle, deduped, each with the seed that reproduces it."""
    names = collect_names(rot)
    findings = {}
    stats = defaultdict(int)
    reached = set()
    for i in range(count):
        case_seed = seed + i
        rng = random.Random(case_seed)
        st = random_state(rot, rng, names)
        try:
            state = st.clone()
            trace, verdict = run_scenario(rot, state, ticks)
        except RecursionError:
            stats['CRASH'] += 1
            findings.setdefault(('CRASH', 'recursion'), []).append(case_seed)
            continue
        except Exception as exc:
            stats['CRASH'] += 1
            key = ('CRASH', '%s: %s' % (type(exc).__name__, exc))
            findings.setdefault(key, []).append(case_seed)
            if verbose:
                traceback.print_exc()
            continue

        for a, _, off in trace:
            if a is not None:
                reached.add(a.label())
            for oa, _ in off:
                reached.add(oa.label())
        kind = verdict[0]
        stats[kind] += 1
        if kind == 'LOOP':
            sig = tuple(sorted({a.label() for a, e, _ in verdict[1]
                                if a is not None and 'form ->' in e}))
            if any(any(m in lbl for m in BENIGN_MARKERS) for lbl in sig):
                stats['LOOP(benign)'] += 1
                stats['LOOP'] -= 1
            else:
                findings.setdefault(('LOOP', sig), []).append(case_seed)
        elif kind == 'STALL':
            findings.setdefault(('STALL', ''), []).append(case_seed)

        eng = Engine(rot, st.clone())
        for a in rot.all_actions():
            if a.cond is not None:
                try:
                    eng.cond_true(a)
                except Exception as exc:
                    findings.setdefault(
                        ('COND', '%s -> %s' % (a.label(), exc)),
                        []).append(case_seed)
        for e in eng.errors:
            findings.setdefault(('PARSE', e), []).append(case_seed)
    return findings, stats, names, reached


def describe_case(rot, seed, names):
    """Rebuild a fuzz case from its seed, so a finding can be reproduced."""
    rng = random.Random(seed)
    st = random_state(rot, rng, names)
    on = [k for k, v in st.pins.items() if v]
    parts = [
        'hp=%.1f eff=%.1f form=%s cast=%s chan=%s combat=%s moving=%s '
        'enemies=%d ap=%.0f' % (st.health, st.eff(), st.form, st.casting,
                                st.channeling, st.combat, st.moving,
                                st.enemies40, st.astral_power),
        '      talents: ' + (', '.join(sorted(st.talents)) or '(none)'),
        '      buffs:   ' + (', '.join(sorted(st.buffs)) or '(none)'),
        '      pinned:  ' + (', '.join(sorted(on)[:8]) or '(none)'),
    ]
    return ('\n').join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--talents', default='',
                    help='comma-separated talents to treat as taken')
    ap.add_argument('--ticks', type=int, default=40)
    ap.add_argument('--unknowns', action='store_true',
                    help='list every expression this model could not resolve')
    ap.add_argument('--fuzz', type=int, default=0, metavar='N',
                    help='run N random states per file instead of the fixed '
                         'grid, pinning unmodelled expressions randomly')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--replay', type=int, default=None, metavar='SEED',
                    help='print the full trace of one fuzz case by its seed')
    ap.add_argument('--trace', default=None,
                    help='print the full trace for scenarios matching this text')
    args = ap.parse_args()

    talents = [t.strip() for t in args.talents.split(',') if t.strip()]
    bad = 0

    if args.fuzz or args.replay is not None:
        for path in args.files:
            rot = Rotation(path)
            names = collect_names(rot)
            if args.replay is not None:
                print('=' * 78)
                print('%s  replay seed %d' % (path, args.replay))
                print('=' * 78)
                print(describe_case(rot, args.replay, names))
                rng = random.Random(args.replay)
                st = random_state(rot, rng, names)
                state = st.clone()
                trace, verdict = run_scenario(rot, state, args.ticks)
                print('')
                for k, (a, e, off) in enumerate(trace):
                    extra = ''.join(' +' + o.label() for o, _ in off)
                    print('  %2d  %-48s %s%s'
                          % (k, a.label() if a else '(nothing)', e, extra))
                print('')
                print('  verdict: %s' % verdict[0])
                continue

            print('=' * 78)
            print('%s  fuzz: %d random states, seeds %d..%d'
                  % (path, args.fuzz, args.seed, args.seed + args.fuzz - 1))
            print('=' * 78)
            findings, stats, names, reached = fuzz(rot, args.fuzz, args.seed,
                                                   args.ticks)
            print('  randomised: %d buffs, %d cooldowns, %d talents, '
                  '%d unmodelled expressions'
                  % (len(names['buffs']), len(names['cds']),
                     len(names['talents']), len(names['opaque'])))
            nlines = sum(len(v) for v in rot.actions.values())
            print('  coverage:   %d of %d lines reached (%.0f%%)'
                  % (len(reached), nlines, 100.0 * len(reached) / (nlines or 1)))
            total = sum(stats.values()) or 1
            print('  outcomes:   ' + '  '.join(
                '%s %d (%.0f%%)' % (k, v, 100.0 * v / total)
                for k, v in sorted(stats.items())))
            if not findings:
                print('')
                print('  NOTHING FOUND. No crash, no loop, no stall.')
                continue
            bad = 1
            order = {'CRASH': 0, 'PARSE': 1, 'COND': 2, 'LOOP': 3, 'STALL': 4}
            for (kind, detail), seeds in sorted(
                    findings.items(), key=lambda kv: (order.get(kv[0][0], 9),
                                                      -len(kv[1]))):
                print('')
                print('  %s  x%d   (first seed %d)'
                      % (kind, len(seeds), seeds[0]))
                if detail:
                    if isinstance(detail, tuple):
                        for d in detail:
                            print('      ' + str(d))
                    else:
                        print('      ' + str(detail))
                print(describe_case(rot, seeds[0], names))
                print('      reproduce: python sim/rotation_sim.py %s '
                      '--replay %d' % (path, seeds[0]))
        return bad

    for path in args.files:
        rot = Rotation(path)
        print('=' * 78)
        print('%s  (entry: %s, %d lists, %d lines)'
              % (path, rot.entry, len(rot.actions),
                 sum(len(v) for v in rot.actions.values())))
        print('=' * 78)

        fired = defaultdict(int)
        cond_true = defaultdict(int)
        cond_seen = defaultdict(int)
        unknown_all, errors_all = set(), []
        loops, stalls = [], []

        for label, st in build_scenarios(rot, talents):
            eng = Engine(rot, st.clone())
            for a in rot.all_actions():
                if a.cond is not None:
                    cond_seen[a.label()] += 1
                    if eng.cond_true(a):
                        cond_true[a.label()] += 1
                else:
                    cond_seen[a.label()] += 1
                    cond_true[a.label()] += 1
            unknown_all |= eng.unknown
            errors_all += eng.errors

            state = st.clone()
            trace, verdict = run_scenario(rot, state, args.ticks)
            for a, _, off in trace:
                if a is not None:
                    fired[a.label()] += 1
                for oa, _ in off:
                    fired[oa.label()] += 1
            kind = verdict[0]
            if kind == 'LOOP':
                loops.append((label, verdict[1]))
            elif kind == 'STALL':
                stalls.append(label)
            if args.trace and args.trace in label:
                print('\n--- trace: %s' % label)
                for i, (a, e, off) in enumerate(trace):
                    extra = ''.join(' +%s' % o.label() for o, _ in off)
                    print('  %2d  %-50s %s%s'
                          % (i, a.label() if a else '(nothing)', e, extra))
                print('  verdict: %s' % kind)

        if errors_all:
            bad = 1
            print('\nEXPRESSIONS THAT DID NOT PARSE (%d)' % len(errors_all))
            for e in sorted(set(errors_all)):
                print('  ! ' + e)

        if loops:
            bad = 1
            print('\nLOOP - environment frozen, rotation never settles (%d scenarios)'
                  % len(loops))
            for label, cycle in loops[:6]:
                print('  %s' % label)
                for a, e, _ in cycle[:8]:
                    print('      %-52s %s' % (a.label() if a else '(nothing)', e))
        else:
            print('\nLOOP: none. Every scenario settled or stayed open.')

        if stalls:
            print('\nSTALL - in combat and nothing suggested (%d scenarios)'
                  % len(stalls))
            for s in stalls[:8]:
                print('  %s' % s)

        dead = [a.label() for a in rot.all_actions() if fired[a.label()] == 0]
        if dead:
            print('\nNEVER FIRED in any scenario (%d) - dead, or gated on '
                  'something this model does not evaluate' % len(dead))
            for d in dead[:20]:
                print('  . ' + d)
            if len(dead) > 20:
                print('  ... and %d more' % (len(dead) - 20))

        always = [k for k, v in cond_true.items()
                  if cond_seen[k] and v == cond_seen[k]]
        if always:
            print('\nALWAYS TRUE in every scenario (%d) - ask what makes it false'
                  % len(always))
            for a in always[:15]:
                print('  ~ ' + a)

        if args.unknowns:
            print('\nUNRESOLVED EXPRESSIONS (%d) - treated as false'
                  % len(unknown_all))
            for u in sorted(unknown_all):
                print('  ? ' + u)
        else:
            print('\n%d expressions unresolved (treated as false). --unknowns to list.'
                  % len(unknown_all))

    return bad


if __name__ == '__main__':
    sys.exit(main())
