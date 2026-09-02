# Measuring a Simia rotation with SimulationCraft

How this repo uses SimC to decide whether a change to a rotation YAML is worth
keeping. Written to be handed to another agent working on the same files.

Everything here was established by running it, not by reading about it. Where a
claim has a known limit, the limit is stated.

---

## 1. What SimC can and cannot answer

SimC simulates **damage**. That is the whole of what it decides here.

| Spec | Half that is measurable | Half that is not |
|---|---|---|
| Balance | all of it | — |
| Feral | all of it | — |
| Guardian | damage | survival, threat, cooldown timing vs boss damage |
| Restoration | Cat/Bear weaving damage | every healing decision |

**The healing model.** As of nightly `a9a6985` (2026-08-23) SimC does spawn
healing targets and does report HPS with a real error bar — but only if you
pass `healing=N` explicitly. `role=heal` alone spawns nothing and everything
reads 0.

Even then it answers less than it looks. The healing target is
`health=0|20000000`: a bottomless bucket that starts empty and never fills.
Measured consequence — `actual_amount == total_amount`, overheal `0.00%`, and
there is no overheal field in the JSON at all. So:

- **measurable**: raw HPS of a cast sequence, mana efficiency, talent/gear impact
- **not measurable**: overheal, triage, cooldown timing, any HP threshold

Every healing threshold in a rotation is therefore unmeasurable — all targets
sit at 0% forever, so `cycle.health.pct<X` has nothing to decide. A throughput
sim always favours spamming the highest-HPS spell, which is exactly what
overheals in a real key. Treat healing numbers as biased, and say so whenever
you quote one.

---

## 2. M+ versus raid

The difference is the fight style and the target count, and it matters more
than people expect — a change can win at one and lose at the other.

**Check the fight style is supported before believing any number.** SimC knows
which styles each spec module was validated against, and says so:

    Severe: Player 'Tassiana' does not support fight style DungeonSlice,
    results are inaccurate and should not be used.

Balance Druid prints that for `DungeonSlice`, `HeavyMovement`,
`CastingPatchwerk` and `HecticAddCleave`. It prints it with SimC's own stock
APL, and on older binaries too — so it is the spec module talking, not the
custom APL, and it was **not** a new check. Every DungeonSlice number this repo
produced before 2026-08-27 carried that warning unnoticed, because nothing
grepped for it. Always grep:

```bash
simc ... 2>&1 | grep -iE "does not support fight style|^Error|Severe"
```

| | M+ | Raid |
|---|---|---|
| `fight_style` | `DungeonRoute` + a route file | omit (SimC default = Patchwerk) |
| targets | set by the pull events | 1 for ST, 6–8 for cleave |
| `target_error` | `0.15` | `0.15` |
| what it models | pull after pull, travel time, bosses | one target, full duration, no downtime |

`DungeonRoute` is supported and is the better proxy anyway: it is an actual
sequence of pulls with travel delays between them, so cooldown drift and
downtime are modelled rather than assumed away. It requires pull events —
without them it refuses to start:

    Error: Initialization error: DungeonRoute fight style requires at least
    one pull event with pull=1.

The route lives in `sim/dungeon_route.simc`. Syntax:

```
raid_events+=/pull,pull=01,bloodlust=0,delay=010,enemies="a1":1200000|"a2":1200000
```

`enemies` is `|`-delimited `"name":health[:CreatureType]`; prefix a name with
`BOSS_` to spawn it as a boss actor. **Health pools must be calibrated to the
character's actual throughput.** The first route written here used pools ~10x
too large and produced a 4850-second fight; the numbers in that file are sized
for ~144k Patchwerk single-target and need re-scaling after a big gear change.

DungeonRoute DPS is route-wide and includes the travel delays, so it reads far
below Patchwerk (100.6k vs 144.1k on the same gear). Only deltas between
profilesets mean anything — never compare a route number to a Patchwerk one.

**A second trap:** the harnesses only pass `fight_style` when you give
`--style`. Without it you are running Patchwerk, whatever you meant. Label
results with the style you actually ran.

---

## 3. The A/B harness

Each spec has one: `sim/ab_test_<spec>.py`, plus a `.simc` profile per spec in
`sim/`. The design is the same in all of them.

The harness **generates a SimC APL from Python**, one function that takes a
variant dict and emits action lines. Variants differ from the baseline by
**exactly one thing**. That is the whole discipline: a variant that changes two
things measures neither.

```python
VARIANTS = {
    'ferraz':       ({}, 'the current rotation'),
    'swipe_aoe':    (dict(swipe_aoe=True), 'Swipe instead of Shred as AoE filler'),
    'no_bearweave': (dict(bearweave=False), 'straight into Cat, no Bear opener'),
}
```

Run it:

```bash
python sim/ab_test_resto_dps.py --targets 3
```

```bash
python sim/ab_test_balance.py ferraz no_wrath --targets 5 --style DungeonSlice
```

### Significance

A result is real only if the gap clears the combined error bar:

```
comb = 2 * sqrt(e1² + e2²)        # e = dps['mean_std_dev'] from the JSON
real = abs(delta) > comb
```

Anything inside that is printed as `~` and must be reported as noise, never as
a small win. **Use `mean_std_dev`, not `stddev`** — the second is per-iteration
spread and is far larger, so it hides real differences.

### Comparing runs

Never compare a number from one run against a number written down earlier
unless the profile, gear, target count, fight style and binary are all
identical. Re-run the baseline in the same batch. Two profile snapshots
compared across a gear change produced a "this is noise" verdict here that was
wrong; the gain was real.

---

## 4. Translating Simia YAML into a SimC APL

The harness is only as good as this translation, and this is where the errors
happen. Mirror the YAML **line for line**. Do not invent lines to "make it
work" — a missing shapeshift or an ungated filler can produce a fake +244%,
which measured nothing but the harness's own invention.

Expressions that exist in Simia and have **no SimC equivalent**:

| Simia | why it fails | what to do |
|---|---|---|
| `target.in_melee` | Simia-only; SimC errors out | SimC parks the target in melee — drop the branch |
| `enemies.combat.8y` | no combat-aware count | `spell_targets` |
| `cycle.*`, `group.count(...)` | no party model | no equivalent; the line cannot be measured |
| `player.combat` | sim is always in combat | drop |
| `var.can_catweave` | depends on group health | permanently true in sim — state this as a divergence |

Spell-name traps found the hard way:

- `thrash_bear` is invalid for Restoration. SimC registers the generic `thrash`
  and resolves it by form.
- `swipe` matches the Bear version. Use the numeric id (`106785` for Cat).
- Fluid Form auto-shifts on Thrash/Mangle/Rake/Shred. Do **not** add explicit
  `bear_form` / `cat_form` lines the YAML does not have.

Write the divergences into the harness docstring. A harness whose limits are
undocumented will be trusted past them.

---

## 5. Reading a talent string

SimC decodes them. Put `talents=<string>` in a profile, run it, and read the
talent table out of the HTML report. This is how a build gets verified before
any rotation change is justified by it.

The same binary answers "can this spec even cast X":

```bash
./sim/tools/simc-*/simc.exe "spell_query=spell.name=starsurge"
```

Read the `Talent Entry` line. `free=(Balance)` means free **for Balance only** —
another spec needs to spend a point. That check caught three lines in the
Restoration ranged list that had been inert for weeks, and it contradicted a
comment that claimed the opposite "verified against the game's spell data".

`spell_query` only carries player spell data. NPC and encounter auras are not in
it — for those, Wowhead, and then a Simia snapshot to confirm which unit
actually carries the aura.

---

## 6. Update the binary before you trust it

Standing rule in this repo. The bundled WoW data goes stale within days, and
every gear and talent measurement depends on it matching the live client.

```bash
./sim/tools/simc-*/simc.exe 2>&1 | head -1
```

```bash
curl -s -k -L "http://downloads.simulationcraft.org/nightly/" | grep -oE 'simc-[0-9.]+[a-f0-9]+-win64\.7z'
```

Plain `http` — the `https` on that host serves a certificate for
`*.your-server.de` and fails validation.

SimulationCraft publishes **no GitHub releases**; the releases API returns `[]`.
Use the compare API instead and report `ahead_by` plus whether any commit
touches the class being measured:

```bash
curl -s "https://api.github.com/repos/simulationcraft/simc/compare/<local-sha>...<remote-sha>"
```

The active branch is `midnight`, not `master`. Extraction needs the `py7zr` pip
package; there is no 7-Zip on this machine. After updating, repoint every
harness path and **re-verify the most important recent finding on the new
binary** before trusting it.

### `py`, not `python`, for the extraction

Two Pythons are installed and they resolve differently from this shell. `py7zr`
lives only in the one the `py` launcher finds:

```
python -> ModuleNotFoundError: No module named 'py7zr'
py     -> Python314\python.exe, py7zr 1.1.3
```

`python` is fine for everything else in this repo; the extraction step is the
one that needs `py`.

### Strip the GUI after extracting

The nightly ships the Qt desktop app alongside the CLI. `simc.exe` is
statically linked and needs none of it — verified by running a full Patchwerk
sim after deleting the lot. Extracting leaves a 539 MB folder; stripped it is
118 MB, and the CLI is 115 MB of that.

Safe to delete from the extracted folder:

```
SimulationCraft.exe  QtWebEngineProcess.exe  Qt6*.dll
dxcompiler.dll  dxil.dll  d3dcompiler_47.dll  opengl32sw.dll
Welcome.png  Error.html
resources/  qml/  qmltooling/  platforms/  imageformats/  styles/
translations/  locale/  iconengines/  networkinformation/  position/
tls/  generic/
```

Keep `simc.exe`, `profiles/` and the license files. `tls/` is a Qt network
plugin, not the CLI's TLS — armory imports still work without it.

---

## 6b. Check fight-style support WITH the route attached

Balance supports DungeonRoute but not DungeonSlice. **Elemental Shaman supports
neither.** Guardian supports Patchwerk, DungeonSlice and DungeonRoute. Assume
nothing per spec; probe it.

The probe itself has a trap. Passing `fight_style=DungeonRoute` with **no route
file** prints no warning at all — the validation only runs once `raid_events`
pull entries exist, so a bare style check returns a false pass. Probe with the
route attached:

```bash
./sim/tools/simc-*/simc.exe PROFILE.simc sim/dungeon_route.simc fight_style=DungeonRoute iterations=20 threads=8 2>&1 | grep -c "does not support"
```

0 means supported. Argument order does not matter; putting `fight_style=` first
gives the same answer. Run it against a profile known to pass (a druid one) as a
control before believing a failure.

When a spec has no dungeon style, M+ numbers come from multi-target Patchwerk
(`desired_targets=N`). That models a static pull of N mobs and nothing else — no
pull cadence, no cooldown budgeting across a route, no travel. Say so in the
writeup instead of letting the number imply a route.

---

## 7. What a result is allowed to claim

Absolute DPS is meaningless here. The Restoration harness runs on SimC's MID1
**Balance** preset because no Restoration one exists, so only deltas between
variants mean anything. Say that whenever you quote a number.

A finished measurement reports: the variant, the delta, the error bar, the
target count, the fight style, and the binary. Drop any of those and the number
cannot be checked later — and in this repo, numbers do get checked later.
