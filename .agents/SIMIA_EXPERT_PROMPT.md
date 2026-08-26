# Briefing: working on Simia rotation YAMLs

Paste this to an agent that will edit rotations in this repo. It is written as
instructions to that agent.

Everything below was learned by getting it wrong first. The wrong turns are
included on purpose — they are the parts that repeat.

---

## The one habit that matters most

**When a rotation misbehaves in game, ask which `name="..."` line the execution
log showed. Do not reason about conditions from the YAML first.**

A single "it keeps casting Rejuvenation out of combat" report took five
attempts here. Four diagnoses were wrong — each found a real bug, none found
*that* bug. The answer arrived in seconds once the list was named: the list had
**three callers and only one was gated**.

Reading the file cannot find this class of fault, because the fault is usually
a second caller, a config wired in only one place, or an expression that
silently never resolves. So:

- Ask for the line name. Every line in these rotations carries `name=` for this.
- Then `grep -n "call_action_list,name=<list>"` for **every** caller, not the
  obvious one.
- State a diagnosis as a candidate, not as the cause, until the line is known.

---

## Snapshots are the ground truth

`/simia snapshot` writes a log with `=== PLAYER ===`, `=== TARGET ===`,
`=== PARTY[n] ===`, `=== SPELLS ===`, `=== QUEUE ===`, `=== MORPHS ===`,
`=== BINDINGS ===` and a full `=== ROTATION TRACE ===` with per-step
`SANITY` / `CONDITION` breakdowns showing each sub-expression and PASS/FAIL.

**Always grep a snapshot with its section header attached:**

```bash
awk '/^=== /{sec=$0} /PATTERN/{print NR": ["sec"] "$0}' snapshot.log
```

A bare grep hides which unit an aura is on. That cost four wrong fixes to one
line here: Symbiotic Relationship has **two auras**, `474754` on the healer
(`mine=no`) and `474750` on the tank (`mine=yes`), and a headerless grep made
them look like one id sitting on the player.

---

## Bug class #1: conditions that can never turn false

This is the dominant failure mode. A line looks gated, is not, and fires every
pass. Real examples from this repo:

| Condition | Why it never went false |
|---|---|
| `auto_combat.player` | expression does not exist — reversed name, never fired |
| `buff.abundance.stack<5` | the buff caps at **1** stack; true even while up |
| `buff.symbiotic_relationship.down` | the NAME does not resolve to the aura |
| `buff.474760.down` | that id is the bond **heal**, never an aura |
| `buff.474750.down` on a `cycle=tanks` line | bare `buff.` reads the **player** |
| `!player.casting\|!player.channeling` | `\|` where `&` was meant — almost always true |

**Before shipping any gate, ask: what makes this false?** If you cannot name
the state, the line is not gated.

Verify a buff id against a snapshot, never against a guess. And note that a
**cast id and its aura id are different spells** — Storm Blessed is cast as
`1310311` and applies aura `1289229`; gating on the cast id would be true for
2.5 seconds a minute.

---

## Bug class #2: `|` with an ungated branch

In `A|B`, each branch must stand alone. If one has no gate, the condition has
no gate.

```yaml
# WRONG — the left branch has no health check, so a full-health target passes
if=buff.clearcasting.up&(pred.cycle.buff.regrowth.down|cycle.health.effective.pct<99)
```

Three separate bugs here had this shape. Audit for it:

```bash
# split each if= on top-level | and flag branches that mention no health
```

---

## Bug class #3: `cycle.` prefix missing

On a line with `cycle=members` / `cycle=tanks`, a property must name the cycled
unit: `cycle.buff.X`, `cycle.health.pct`. **Bare `buff.X` reads the player.**

The fastest check is a diff against its neighbours — in a file where twenty
`cycle=` lines use the prefix, the one that does not is the bug.

Exceptions are real: `buff.clearcasting.up`, `buff.abundance.up`,
`buff.natures_swiftness.up`, `buff.cat_form.up` are genuinely player auras and
correctly bare. Unit-qualified forms like `tank1.buff.X` are fine too.

---

## Expressions that do not mean what they look like

| Expression | Reality |
|---|---|
| `active_enemies` | **nameplate** count — includes a training dummy nearby and packs nobody pulled. Use `enemies.combat.40y` / `enemies.combat.8y`. |
| `player.auto_combat` | a **config** check, not combat state. Combat state is `player.combat`. |
| `health.effective.pct` | `healthPct - healAbsorbPct + incomingHealsPct`. Correct for "does this still need healing"; **wrong for emergencies** — with HoTs rolling, 30% real reads ~50% effective. |
| `target.valid` | documented as including "in combat (PvE)"; in practice it does **not** hold unpulled mobs back. |
| `mouseover.unitframe` | true only from a **UI party/raid frame**, false from the 3D world. Gating healing on it makes world NPCs unhealable. |
| `group.count(EXPR)` | iterates **allies**. There is no enemy equivalent, and no `.any(EXPR)` predicate for enemies. |
| `target_enemy` | "nearest enemy", **no filter** — but it cycles on repeated presses, like Tab. |

There is **no melee-aware enemy count**. `target.in_melee` and
`target.melee_gap` are per-unit tests. Use `enemies.combat.8y`.

---

## The spell queue

Three different things share the name.

**`queue_spell` has two opposite forms.** Bare, it flushes what the *player*
queued. With `spell=X` it makes the *rotation* queue X — for an off-GCD the
addon cannot press during a hardcast. Mistaking one for the other adds
automatic casts nobody asked for.

**The queue is NOT filtered by cooldown on entry.** The `_shared.yaml` comment
promises "usable (valid, off CD, has charges)"; the off-CD half holds only at
flush. The addon uses `IsUsableSpell()`, which checks resources and state and
**ignores cooldown** — that is `GetSpellCooldown`, a separate call. A snapshot
showed `QUEUE (1)` holding a spell reading `usable=YES cd=26.8/120.0`.

**This is not fixable in YAML.** The queue is populated by Lua at keypress; no
rotation expression is evaluated then. `queue_logic:` gates the **cast**, not
the entry. Do not go looking for an entry expression — there is none.

---

## Modifiers worth knowing

| Modifier | What it does |
|---|---|
| `ignore_queue=true` | skips only the `isCurrentSpell` guard. Does **not** bypass CD, cost or range. Pairs with `off_gcd=true` on reactive defensives and kicks. |
| `ignore_usable` | skips CD **and** resources |
| `ignore_cooldown` | CD only; resources still required |
| `range_check=` | `none` \| `mob` \| `mouseover` \| `focus` \| `target` |
| `casting_check=any` | run the step only while casting/channelling |
| `delay=`, `global_delay=`, `line_cd=`, `after=` | throttles; `global_delay` blocks *everything* for N ms |

Cast-target suffixes: `.player`, `.focus`, `.mouseover`, and **`.focus_mouseover`**
— that last one is used by five community rotations and one official one, but
the docs list `focus_mouseover` only as a standalone action. It is a valid
suffix.

There is **no cancel-form action**. Only `stop_casting`. Casting any healing
spell drops you out of Cat/Bear on its own, so a spell whose only purpose is
leaving a form is wasted mana — that mistake was made and reverted four times.

`spell_overrides:` is a top-level block that AND-s a condition onto every cast
of a spell. It is invisible in the priority list, so when debugging a spell,
check whether an override is gating it.

---

## SimC spell data: trust the fields, not the prose

`spell_query` is the right tool for "can this spec cast X" and "is this
channelled" — the `Attributes` and `Talent Entry` fields have held up every
time. The `Description` field has not.

Worked example. Fluid Form (449193) reads, in SimC:

    Description : Shred, Rake, and Skull Bash can be used in any form and
                  shift you into Cat Form, if necessary.

The in-game tooltip for the same id carries three lines, not one:

    Shred, Rake, and Skull Bash ... shift you into Cat Form
    Mangle ... shifts you into Bear Form
    Wrath and Starfire shift you into Moonkin Form, if known.

Reading only SimC's copy produced a confident, twice-repeated, wrong claim
that Starfire does not return a Balance druid to Moonkin. It does, and that
turns a form shift from a spent global into a free one.

So: quote `Attributes` and `Talent Entry` as evidence. For what a spell
actually DOES, ask for the tooltip.

## Documentation gaps to expect

`expression-catalog.json` and `SIMIA_DOCUMENTATION.md` are incomplete, and the
site's copy is byte-identical to the local one — updating will not help.
Missing entirely: **`hero_tree.*`** (26 hero trees, used by 27+ official
rotations), `queue_logic`, and any description of `queue_spell`.

So: an expression absent from the catalog is **not proof it is invalid**. Check
`simia_data_dump/rotation_*.yaml` — those are the official rotations, and they
are the real specification.

---

## House rules for this repo

**M+ and raid must differ only in the damage lists.** Defensives, dispels,
interrupts and the opening checks are identical between the two files of a
spec. If you fix one, fix its twin.

**Versioning is semver, bumped on every commit**, alongside the `Last update`
stamp in the `about` config block — both must agree:

- bug fix `+0.0.1` · improvement `+0.1.0` · large change `+1.0.0`
- keep the quotes: `version: "3.8.1"`

**Every spell line gets `name=`.** Non-negotiable when the same spell appears
twice in one list — the log cannot tell you which fired, and that blindness is
what costs the five-attempt debugging sessions.

**Do not open websites with browser/MCP tools** — it crashes the IDE. `WebFetch`
and `WebSearch` are fine. `auth.simia.pro` returns 403 to WebFetch; fetch it
with `curl -A "Mozilla/5.0"`.

Run `python lint_rotations.py Ferraz*.yaml` after every edit.

---

## How to close a bug report

1. Get the line name from the log, or a snapshot taken **while it is happening**.
2. Find every caller of the list involved.
3. Name the state that makes the condition false. If you cannot, that is the bug.
4. Confirm ids against the snapshot — cast id vs aura id, and which unit carries it.
5. Write the *why* into the file as a comment, including what was tried and
   failed. These bugs come back otherwise; several here were fixed two, three,
   four times.
