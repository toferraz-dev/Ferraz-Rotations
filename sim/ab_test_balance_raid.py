"""A/B harness for the RAID Balance rotation (FerrazBalanceRaid.yaml).

Same idea as sim/ab_test_balance.py, different rotation and different fight
style: raid means Patchwerk, not DungeonSlice.

The big fact this harness exists to measure: the file is written for Keeper of
the Grove (Force of Nature, Wild Mushroom, the three Moons, Solar Eclipse
first, Wrath as filler) but the talent string it now carries is ELUNE'S CHOSEN
with Lunar Calling. Every Grove line is dead on that build, and the fillers are
the wrong way round.

Dropped on purpose, as in the M+ harness: defensives, interrupts, mouseover
casts, Mark of the Wild, Thorn Bloom, and the two `moving_*` lists.

Run:
    python sim/ab_test_balance_raid.py                 # every variant, 1 target
    python sim/ab_test_balance_raid.py --targets 3
    python sim/ab_test_balance_raid.py raid_ferraz raid_v2
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.62ca36f-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Ferraz_balance_raid.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl_balance_raid')
OUT_DIR = os.path.join(ROOT, 'sim', 'out_balance_raid')

CD_ACTIVE = 'buff.ca_inc.up'
ECLIPSE_DOWN = 'buff.eclipse.down'
# `var.opener` — true whenever CA/Inc is off cooldown and not already running,
# so the YAML re-enters its "opener" ramp before every burst, not just on pull.
OPENER = 'cooldown.ca_inc.up&!' + CD_ACTIVE
# The YAML's Sundered Firmament gate on Fury of Elune.
FOE_GATE = ('!talent.sundered_firmament|(debuff.atmospheric_exposure.remains<2'
            '&buff.eclipse_lunar.remains>5)|fight_remains<20')
FOE_GATE_AOE = '!talent.sundered_firmament|debuff.atmospheric_exposure.remains<2'


def a(action, *conds):
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    L = []
    add = L.append

    add('actions.precombat=snapshot_stats')
    add('actions.precombat+=/moonkin_form')
    add('actions.precombat+=/wrath')

    add('actions=call_action_list,name=trinkets')
    if v['opener']:
        add('actions+=/run_action_list,name=opener_aoe,if=(%s)&spell_targets>1' % OPENER)
        add('actions+=/run_action_list,name=opener_st,if=(%s)&spell_targets=1' % OPENER)
    add('actions+=/run_action_list,name=aoe,if=spell_targets>1')
    add('actions+=/run_action_list,name=st')

    # The YAML fires trinkets in the burst window or when the burst is far away.
    add('actions.trinkets=' + a('use_items', CD_ACTIVE + '|cooldown.ca_inc.remains>40'))
    # NOTE: the YAML has no potion line at all. `potion='off'` is the faithful
    # translation; the others price what adding one would be worth.
    if v['potion'] == 'burst':
        add('actions.trinkets+=/' + a('potion', CD_ACTIVE))
    elif v['potion'] == 'burst_end':
        add('actions.trinkets+=/' + a('potion', CD_ACTIVE + '|fight_remains<=30'))

    def emit(name, lines):
        lines = [x for x in lines if x]
        for i, ln in enumerate(lines):
            add('actions.%s%s%s' % (name, '=' if i == 0 else '+=/', ln))

    # --- the two knobs the mismatch is about --------------------------------
    # Filler. The YAML ends both damage lists on Wrath, which is a Keeper of the
    # Grove habit; Lunar Calling wants Starfire.
    if v['filler'] == 'wrath':
        st_filler = [a('starfire', 'buff.eclipse_lunar.up&!' + CD_ACTIVE), 'wrath']
        aoe_filler = [a('starfire', 'spell_targets>=3'), 'wrath']
    elif v['filler'] == 'starfire_only':
        st_filler = ['starfire']
        aoe_filler = ['starfire']
    else:
        st_filler = [a('wrath', ECLIPSE_DOWN), 'starfire']
        aoe_filler = ['starfire']

    # Dead Grove lines: Force of Nature, Wild Mushroom, the three Moons. SimC
    # drops them for lack of the talent; `off` removes them from the file too.
    grove = v['grove_lines']
    fon = a('force_of_nature', CD_ACTIVE + '|cooldown.ca_inc.remains>30') if grove else ''
    mush_st = a('wild_mushroom', 'buff.eclipse_lunar.up|cooldown.wild_mushroom.full_recharge_time<cooldown.ca_inc.remains') if grove else ''
    mush_aoe = a('wild_mushroom', 'buff.eclipse.up|cooldown.wild_mushroom.full_recharge_time<cooldown.ca_inc.remains') if grove else ''
    moons = [
        a('full_moon', 'astral_power.deficit>40&debuff.atmospheric_exposure.remains<action.full_moon.execute_time+0.5'),
        a('half_moon', 'astral_power.deficit>20&debuff.atmospheric_exposure.remains<action.half_moon.execute_time+0.5'),
        a('new_moon', 'astral_power.deficit>10&debuff.atmospheric_exposure.remains<action.new_moon.execute_time+0.5'),
    ] if grove else []

    # Spender. `floor` is the YAML's flat astral_power>60; `approx` is the
    # Eclipse-aware floor that won 0.79% in the M+ file.
    ss_main = (a('starsurge', 'buff.eclipse.up&astral_power>=50|' + ECLIPSE_DOWN + '&astral_power.deficit<20')
               if v['spender'] == 'approx'
               else a('starsurge', 'astral_power>60&spell_targets=1'))

    # DoT maintenance. The YAML only allows the pandemic refresh while no
    # Eclipse is up (`refreshable&var.eclipse_down`); `always` drops that.
    if v['dot_gate']:
        mf = a('moonfire', 'dot.moonfire.remains<2|dot.moonfire.refreshable&' + ECLIPSE_DOWN)
        sf = a('sunfire', 'dot.sunfire.remains<2|dot.sunfire.refreshable&' + ECLIPSE_DOWN)
    else:
        mf = a('moonfire', 'dot.moonfire.remains<2|dot.moonfire.refreshable')
        sf = a('sunfire', 'dot.sunfire.remains<2|dot.sunfire.refreshable')

    # Incarnation. The YAML waits for Ascendant Stars to fade; `foe` adds the
    # Fury of Elune alignment the M+ file uses.
    inc_conds = ['!' + CD_ACTIVE]
    if not v['inc_no_ascendant']:
        inc_conds.append('buff.ascendant_stars.down')
    if v['inc_foe_align']:
        inc_conds.append('(cooldown.fury_of_elune.remains<2|buff.fury_of_elune.up)')
    inc = a('celestial_alignment', *inc_conds)

    # --- st -------------------------------------------------------------------
    emit('st', [
        mf, sf,
        a('eclipse', ECLIPSE_DOWN),
        a('fury_of_elune', FOE_GATE),
        fon,
        a('starfall', 'spell_targets>=2&buff.touch_the_cosmos.react'),
        a('starsurge', 'buff.touch_the_cosmos.react'),
        ss_main,
        inc,
    ] + moons + [mush_st] + st_filler)

    # --- aoe ------------------------------------------------------------------
    emit('aoe', [
        a('sunfire', 'dot.sunfire.remains<2|dot.sunfire.refreshable&' + ECLIPSE_DOWN)
        if v['dot_gate'] else a('sunfire', 'dot.sunfire.remains<2|dot.sunfire.refreshable'),
        a('moonfire', 'spell_targets<6', 'dot.moonfire.remains<2|dot.moonfire.refreshable&' + ECLIPSE_DOWN)
        if v['dot_gate'] else a('moonfire', 'spell_targets<6', 'dot.moonfire.remains<2|dot.moonfire.refreshable'),
        a('eclipse', ECLIPSE_DOWN),
        a('fury_of_elune', FOE_GATE_AOE),
        fon,
        a('celestial_alignment', '!' + CD_ACTIVE, ECLIPSE_DOWN + '|fight_remains<20'),
        a('starfall', 'buff.touch_the_cosmos.react'),
        a('starfall', 'astral_power>50&target.time_to_die>5'),
        a('starsurge', 'buff.starfall.up&buff.touch_the_cosmos.react'),
        a('starsurge', 'buff.starfall.up&astral_power>80&buff.starlord.stack<3'),
        mush_aoe,
    ] + aoe_filler)

    # --- opener_st / opener_aoe ----------------------------------------------
    emit('opener_st', [
        mf, sf,
        a('eclipse', ECLIPSE_DOWN),
        a('starsurge', 'buff.ascendant_stars.up|buff.touch_the_cosmos.react'),
        'fury_of_elune',
        fon,
        a('celestial_alignment', '!' + CD_ACTIVE),
        a('starfall', 'spell_targets>1&(buff.touch_the_cosmos.react|astral_power>80)'),
        a('starsurge', 'buff.touch_the_cosmos.react|astral_power>80'),
    ] + (['wrath'] if v['filler'] == 'wrath' else ['starfire']))

    emit('opener_aoe', [
        a('sunfire', 'dot.sunfire.refreshable'),
        a('moonfire', 'spell_targets<6&dot.moonfire.refreshable'),
        'fury_of_elune',
        fon,
        a('celestial_alignment', '!' + CD_ACTIVE),
        a('eclipse', ECLIPSE_DOWN),
        a('starfall', 'astral_power>50|buff.ascendant_stars.up'),
        a('starsurge', 'buff.starfall.up&buff.ascendant_stars.up'),
    ] + ([a('wrath', 'buff.ascendant_stars.up')] if v['filler'] == 'wrath'
         else [a('starfire', 'buff.ascendant_stars.up')]))

    return '\n'.join(L) + '\n'


DEFAULTS = dict(filler='wrath', grove_lines=True, spender='floor', dot_gate=True,
                inc_foe_align=False, inc_no_ascendant=False, opener=True,
                potion='off')

VARIANTS = {
    'raid_ferraz':   ({}, 'Estado ANTIGO do arquivo (Wrath filler, Grove lines, piso fixo)'),
    'filler_ec':     (dict(filler='ec'), 'Starfire de filler, Wrath so fora de Eclipse'),
    'no_grove':      (dict(grove_lines=False), 'Remove as linhas mortas de Grove (FoN/Mushroom/Moons)'),
    'spender_approx': (dict(spender='approx'), 'Piso de AP amarrado ao Eclipse (Rattle the Stars)'),
    'dots_always':   (dict(dot_gate=False), 'Refresca DoT no pandemic mesmo dentro do Eclipse'),
    'inc_foe':       (dict(inc_foe_align=True), 'Incarnation alinhado com Fury of Elune'),
    'raid_v2':       (dict(filler='ec', grove_lines=False, spender='approx'),
                      'Todas as mudancas que ganharam, juntas'),
    'v2_inc_foe':    (dict(filler='ec', grove_lines=False, spender='approx', inc_foe_align=True),
                      'raid_v2 + Incarnation alinhado com Fury of Elune'),
    'v2_no_stars':   (dict(filler='ec', grove_lines=False, spender='approx',
                           inc_no_ascendant=True),
                      'raid_v2 sem esperar Ascendant Stars cair para o Incarnation'),
    'v2_no_opener':  (dict(filler='ec', grove_lines=False, spender='approx', opener=False),
                      'raid_v2 sem as listas de opener'),
    'v2_no_wrath':   (dict(filler='starfire_only', grove_lines=False, spender='approx'),
                      'raid_v2 sem Wrath nenhum, so Starfire'),
    # --- pocao ---------------------------------------------------------------
    # NOTE: the YAML now carries the potion line WITH the fight_remains<=30
    # clause, so `v3_potion_end` — not `v3` — is what the file actually does.
    # `v3` is kept as the no-potion control.
    'v3':            (dict(filler='starfire_only', grove_lines=False, spender='approx'),
                      'Controle: mesma rotacao SEM pocao'),
    'v3_potion':     (dict(filler='starfire_only', grove_lines=False, spender='approx',
                           potion='burst'), 'v3 + pocao dentro do burst'),
    'v3_potion_end': (dict(filler='starfire_only', grove_lines=False, spender='approx',
                           potion='burst_end'), 'v3 + pocao no burst ou no fim da luta'),
}


def run(name, error, enemies, style):
    os.makedirs(APL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    apl = os.path.join(APL_DIR, '%s.simc' % name)
    js = os.path.join(OUT_DIR, '%s_%dt_%s.json' % (name, enemies, style or 'patchwerk'))
    if name != 'simc_default':
        v = dict(DEFAULTS)
        v.update(VARIANTS[name][0])
        with open(apl, 'w', encoding='utf-8') as fh:
            fh.write(build(v))
    cmd = [SIMC, PROFILE]
    if name != 'simc_default':
        cmd.append(apl)
    cmd += ['target_error=%s' % error, 'threads=8', 'json2=' + js,
            'output=' + os.path.join(OUT_DIR, 'nul.txt')]
    if enemies > 1:
        cmd += ['desired_targets=%d' % enemies]
    if style:
        cmd += ['fight_style=' + style]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.isfile(js):
        print('FAILED %s\n%s' % (name, (r.stdout or '')[-1500:]))
        return None
    d = json.load(open(js, encoding='utf-8'))
    dps = d['sim']['players'][0]['collected_data']['dps']
    return dps['mean'], dps['mean_std_dev'], dps['count']


def main(argv):
    error = '0.15'
    enemies = 1
    style = ''
    names = []
    i = 0
    while i < len(argv):
        if argv[i] == '--error':
            error = argv[i + 1]; i += 2; continue
        if argv[i] == '--style':
            style = argv[i + 1]; i += 2; continue
        if argv[i] == '--targets':
            enemies = int(argv[i + 1]); i += 2; continue
        names.append(argv[i]); i += 1
    if not names:
        names = ['simc_default'] + list(VARIANTS)

    results = {}
    for n in names:
        sys.stdout.write('running %-16s ... ' % n)
        sys.stdout.flush()
        r = run(n, error, enemies, style)
        results[n] = r
        print('%.0f DPS' % r[0] if r else 'failed')

    ref = results.get('raid_ferraz')
    print('\n%-16s %10s %8s %10s  %s' % ('variant', 'DPS', '+/-', 'vs atual', 'what'))
    print('-' * 78)
    for n in names:
        r = results[n]
        if not r:
            continue
        mean, err, _ = r
        delta = ''
        if ref and n != 'raid_ferraz':
            d = mean - ref[0]
            comb = 2 * (err ** 2 + ref[1] ** 2) ** 0.5
            delta = '%+.2f%%%s' % (100 * d / ref[0], '' if abs(d) > comb else ' ~')
        what = 'APL padrao do SimC' if n == 'simc_default' else VARIANTS[n][1]
        print('%-16s %10.0f %8.0f %10s  %s' % (n, mean, err, delta, what))
    print('\n"~" = dentro da margem de erro, nao e diferenca real.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
