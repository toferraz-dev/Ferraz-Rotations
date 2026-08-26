"""A/B harness: measure the DAMAGE half of FerrazRestoDruid.yaml.

SimulationCraft has no usable healing model, so nothing about the healing
priority can be validated. What CAN be measured is the Cat/Bear weaving that
runs while the group is topped — the catweave_st, catweave_aoe, bearweave and
ranged_dps lists — and that is what this harness prices.

Read the numbers as "which weaving shape does more damage", never as "this
rotation heals better". A variant that wins here can still be wrong in a key
if it keeps you in Cat Form when someone needs a global.

Gear is SimC's own MID1 Balance preset (there is no MID1 Restoration one), so
absolute DPS is meaningless; only the deltas between variants matter.

Run:
    python sim/ab_test_resto_dps.py
    python sim/ab_test_resto_dps.py ferraz cat_only
    python sim/ab_test_resto_dps.py --targets 4 --style DungeonSlice
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.02b39ce-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Ferraz_resto_mplus.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl_resto_dps')
OUT_DIR = os.path.join(ROOT, 'sim', 'out_resto_dps')

AOE = 3          # config.aoe_threshold


def a(action, *conds):
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    L = []
    add = L.append
    add('actions.precombat=snapshot_stats')

    # The YAML only weaves while the group is healthy. SimC has no group to be
    # hurt, so var.can_catweave is permanently true here — the weaving lists run
    # unopposed. That is the harness's biggest divergence from the game and the
    # reason a "cat forever" variant looks better here than it plays.
    add('actions=variable,name=weave,value=1')

    # The YAML splits ranged_dps vs the melee lists on `target.in_melee`. That
    # is a SIMIA expression; SimC has no equivalent and errors on it. SimC also
    # parks the target in melee for the whole fight, so the split has nothing to
    # decide — the melee branch would always win. Translated as: forms variants
    # go straight to melee, caster_only forces the ranged list.
    if v['forms']:
        if v['bearweave']:
            add('actions+=/call_action_list,name=bearweave')
        add('actions+=/call_action_list,name=catweave')
    else:
        add('actions+=/call_action_list,name=ranged')

    # --- ranged_dps ---
    add('actions.ranged=sunfire,if=dot.sunfire.refreshable')
    add('actions.ranged+=/moonfire,if=dot.moonfire.refreshable')
    add('actions.ranged+=/wrath')

    # --- bearweave, byte-for-byte from the YAML ---
    # NOTE: there is deliberately NO bear_form line and Mangle is NOT
    # unconditional. The YAML leans on Fluid Form to auto-shift when Thrash or
    # Mangle is cast, and gates Mangle on !buff.bear_form.up so it only ever
    # acts as the entry cast. An earlier version of this harness added a
    # bear_form line and an unconditional Mangle; that parked the rotation in
    # Bear Form spamming Mangle forever and made `no_bearweave` look like
    # +244%, which was measuring "the cat rotation works" and nothing else.
    # `thrash`, not `thrash_bear`: for Restoration SimC only registers the
    # generic action and resolves it by form.
    add('actions.bearweave=thrash,if=dot.thrash.stack<3|dot.thrash.remains<=8')
    add('actions.bearweave+=/mangle,if=!buff.bear_form.up&(dot.thrash.remains<=8|dot.thrash.stack<3)')

    # --- catweave entry + cooldowns ---
    add('actions.catweave=cat_form,if=!buff.cat_form.up')
    if v['hotw']:
        add('actions.catweave+=/heart_of_the_wild,if=!buff.heart_of_the_wild.up')
    if v['convoke']:
        add('actions.catweave+=/' + a('convoke_the_spirits', 'buff.cat_form.up'))
    add('actions.catweave+=/call_action_list,name=cat_aoe,if=spell_targets>=%d' % v['aoe_at'])
    add('actions.catweave+=/call_action_list,name=cat_st,if=spell_targets<%d' % v['aoe_at'])

    # --- catweave_st / catweave_aoe, as the YAML writes them ---
    # NOTE: the YAML's AoE list is byte-identical to its ST list — both filler
    # on Shred. Swipe (213764) IS talented on this build and is the Cat AoE
    # builder; `swipe_aoe` prices adding it.
    for name in ('cat_st', 'cat_aoe'):
        eq = 'actions.%s=' % name
        add(eq + a('rip', 'combo_points>=5&dot.rip.refreshable'))
        add('actions.%s+=/' % name + a('ferocious_bite', 'combo_points>=5'))
        add('actions.%s+=/' % name + a('rake', 'dot.rake.refreshable'))
        if name == 'cat_aoe' and v['swipe_aoe']:
            add('actions.cat_aoe+=/swipe_cat')
        add('actions.%s+=/shred' % name)

    return '\n'.join(L) + '\n'


DEFAULTS = dict(forms=True, bearweave=True, hotw=True, convoke=True, aoe_at=AOE,
                swipe_aoe=False)

VARIANTS = {
    'ferraz':       ({}, 'A rotacao atual: bearweave -> catweave, HotW e Convoke'),
    'swipe_aoe':    (dict(swipe_aoe=True), 'Swipe no lugar do Shred como filler de AoE'),
    'no_bearweave': (dict(bearweave=False), 'Sem Bear: entra direto em Cat'),
    'no_hotw':      (dict(hotw=False), 'Sem Heart of the Wild'),
    'no_convoke':   (dict(convoke=False), 'Sem Convoke ofensivo'),
    'caster_only':  (dict(forms=False), 'So caster: Sunfire/Moonfire/Wrath, nunca troca de forma'),
    'aoe_at_2':     (dict(aoe_at=2), 'Entra na lista AoE com 2 alvos em vez de 3'),
    'aoe_at_4':     (dict(aoe_at=4), 'Entra na lista AoE so com 4 alvos'),
}


def run(name, error, enemies, style):
    os.makedirs(APL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    apl = os.path.join(APL_DIR, '%s.simc' % name)
    js = os.path.join(OUT_DIR, '%s_%dt_%s.json' % (name, enemies, style or 'patchwerk'))
    v = dict(DEFAULTS)
    v.update(VARIANTS[name][0])
    with open(apl, 'w', encoding='utf-8') as fh:
        fh.write(build(v))
    cmd = [SIMC, PROFILE, apl, 'target_error=%s' % error, 'threads=8',
           'json2=' + js, 'output=' + os.path.join(OUT_DIR, 'nul.txt')]
    if enemies > 1:
        cmd += ['desired_targets=%d' % enemies]
    if style:
        cmd += ['fight_style=' + style]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.isfile(js):
        print('FAILED %s\n%s' % (name, (r.stdout or '')[-1200:]))
        return None
    d = json.load(open(js, encoding='utf-8'))
    dps = d['sim']['players'][0]['collected_data']['dps']
    return dps['mean'], dps['mean_std_dev']


def main(argv):
    error, enemies, style, names = '0.2', 1, '', []
    i = 0
    while i < len(argv):
        if argv[i] == '--error':
            error = argv[i + 1]; i += 2; continue
        if argv[i] == '--targets':
            enemies = int(argv[i + 1]); i += 2; continue
        if argv[i] == '--style':
            style = argv[i + 1]; i += 2; continue
        names.append(argv[i]); i += 1
    if not names:
        names = list(VARIANTS)
    res = {}
    for n in names:
        out = run(n, error, enemies, style)
        if out:
            res[n] = out
            print('running %-14s ... %.0f DPS' % (n, out[0]))
    if 'ferraz' not in res:
        return
    base, base_e = res['ferraz']
    print('\n%-14s %9s %6s %10s  %s' % ('variant', 'DPS', '+/-', 'vs ferraz', 'what'))
    print('-' * 92)
    for n in names:
        if n not in res:
            continue
        m, e = res[n]
        if n == 'ferraz':
            print('%-14s %9.0f %6.0f %10s  %s' % (n, m, e, '', VARIANTS[n][1]))
            continue
        d = m - base
        comb = 2 * ((e ** 2 + base_e ** 2) ** 0.5)
        tag = '%+.2f%%' % (100 * d / base) if abs(d) > comb else '~'
        print('%-14s %9.0f %6.0f %10s  %s' % (n, m, e, tag, VARIANTS[n][1]))
    print('\n"~" = dentro da margem de erro, nao e diferenca real.')
    print('LEMBRE: isto mede so o dano. O SimC nao modela healing nem o grupo '
          'levando dano,\nentao "ficar em Cat para sempre" sempre parece bom aqui '
          'e nao e.')


if __name__ == '__main__':
    main(sys.argv[1:])
