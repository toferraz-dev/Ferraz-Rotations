"""A/B harness: measure the Ferraz Balance rotation against the SimC default,
and isolate one change per variant.

The Simia YAML cannot be fed to SimulationCraft, so the damage half of
FerrazBalance.yaml is translated here into a SimC action list. Everything the
sim does not model is dropped on purpose: defensives, interrupts, mouseover
casts, Heart of the Wild party healing, Mark of the Wild, and the two `moving_*`
lists (SimC never moves).

Talent notes for the string this profile carries (Elune's Chosen):
  * Starweaver is NOT talented, so `buff.starweavers_weft/warp` never proc.
    Those YAML lines are translated anyway so the baseline matches the rotation
    byte for byte; the `no_starweaver` variant deletes them to price them.
  * Incarnation: Chosen of Elune is talented, so SimC redirects
    `celestial_alignment` to it at parse time and exposes both through the
    `ca_inc` cooldown/buff alias. There is no separate `incarnation_*` action.
  * Lunar Calling + Lunation are in, which is why Fury of Elune is on cooldown
    without a CA-alignment gate.

Each variant differs from `ferraz` by exactly one edit, so the delta is
attributable. Run:

    python sim/ab_test_balance.py                    # every variant
    python sim/ab_test_balance.py ferraz inc_asap    # just these
    python sim/ab_test_balance.py --error 0.1        # tighter (slower)
    python sim/ab_test_balance.py --targets 5        # AoE
    python sim/ab_test_balance.py --style DungeonSlice
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.a9a6985-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Ferraz_balance.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl_balance')
OUT_DIR = os.path.join(ROOT, 'sim', 'out_balance')

# --- config values, mirrored from the YAML defaults --------------------------
# The TTD sliders (ttd_incarnation, ttd_fury_of_elune, ttd_starfall, ...) all
# short-circuit on `target.boss`, which is true for every SimC dummy, so they
# are constant-true here and are not emitted.
SS_AP = 60          # ec_st: starsurge,if=astral_power>60
SF_AP = 50          # aoe:   starfall,if=astral_power>50
SF_PANIC = 80       # aoe:   starfall,if=astral_power>=80 (anti-cap dump)
MOONFIRE_CAP = 99   # aoe: no target cap on Moonfire as of YAML 2.6 —
                    # the old 6 measured -8% to -10.65% at 6/8/10 targets

# `var.eclipse_down` = buff.eclipse_solar.down & buff.eclipse_lunar.down
ECLIPSE_DOWN = 'buff.eclipse.down'
# `var.cd_active` = buff.celestial_alignment.up | buff.incarnation_*.up
CD_ACTIVE = 'buff.ca_inc.up'


def a(action, *conds):
    """Join an action with its conditions, dropping empties."""
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    """Emit the action lists for one variant. `v` holds the toggles."""
    L = []
    add = L.append

    # --- precombat ------------------------------------------------------------
    # The YAML has a single `wrath,if=!player.combat&!player.moving&target.distance<=40`.
    # SimC drains the whole precombat list, so one Wrath is the faithful count;
    # `opener_simc` restores the three the default APL casts.
    add('actions.precombat=snapshot_stats')
    add('actions.precombat+=/moonkin_form')
    for _ in range(3 if v['opener_simc'] else 1):
        add('actions.precombat+=/wrath')
    if v['prepot']:
        # The YAML gates the potion behind burst_toggle & cd_active, so it never
        # pre-pots; the SimC default does.
        add('actions.precombat+=/potion')

    add('actions=variable,name=inc_ready,value=' + inc_ready(v))
    if v['eclipse_timings']:
        # Straight from the SimC default APL: hold Eclipse so the refresh does not
        # land on top of Fury of Elune or CA/Inc.
        add('actions+=/variable,name=eclipse_timings,value='
            '(cooldown.eclipse.full_recharge_time<((cooldown.fury_of_elune.remains*'
            '!talent.lunation)<?(buff.eclipse.duration+2))|cooldown.ca_inc.remains<'
            '((cooldown.fury_of_elune.remains*!talent.lunation)<?(buff.eclipse.duration+2)))'
            '|fight_remains<buff.eclipse.duration')
    add('actions+=/call_action_list,name=trinkets')
    thr = v['aoe_threshold']
    add('actions+=/run_action_list,name=aoe,if=spell_targets>=%d' % thr)
    add('actions+=/run_action_list,name=ec_st')

    # --- trinkets / potion ----------------------------------------------------
    # The YAML defaults use_trinket_1/2 and use_potion to false, but an unused
    # on-use trinket makes the profile incomparable to the SimC default run, so
    # the harness enables them with the YAML's own gate:
    #   burst_toggle & ready & cd_active & cooldown.fury_of_elune.remains>0
    if v['trinkets'] == 'ferraz':
        gate = CD_ACTIVE + '&cooldown.fury_of_elune.remains>0'
        add('actions.trinkets=' + a('use_items', gate))
        add('actions.trinkets+=/' + a('potion', gate))
    elif v['trinkets'] == 'simc':
        add('actions.trinkets=' + a('use_items', CD_ACTIVE))
        add('actions.trinkets+=/' + a('potion', CD_ACTIVE))
    elif v['trinkets'] == 'free':
        # Trinkets whenever ready, ignoring the burst window entirely: a 2min
        # trinket held for a 3min Incarnation loses a use per fight.
        add('actions.trinkets=use_items')
        add('actions.trinkets+=/' + a('potion', CD_ACTIVE))
    elif v['trinkets'] == 'twopot':
        # Pre-pot plus a second potion at the end, which is how the SimC default
        # squeezes ~1.5 potions into a 300s fight.
        gate = CD_ACTIVE + '&cooldown.fury_of_elune.remains>0'
        add('actions.trinkets=' + a('use_items', gate))
        add('actions.trinkets+=/' + a('potion', CD_ACTIVE + '|fight_remains<=30'))
    else:  # 'off' -- the literal YAML default
        add('actions.trinkets=' + a('berserking', CD_ACTIVE))

    # Heart of the Wild: for Balance it is +30% damage to every Balance spell
    # for 45s on a 5min cooldown, plus instant Starsurge. The YAML only ever
    # casts it as a party heal, so `off` is the current behaviour.
    hotw = {
        'off': '',
        'cd': 'heart_of_the_wild',
        'burst': a('heart_of_the_wild', CD_ACTIVE),
        'pre_burst': a('heart_of_the_wild', 'variable.inc_ready|' + CD_ACTIVE),
    }[v['hotw']]
    if hotw:
        add('actions.trinkets+=/' + hotw)

    # Thorn Bloom, the Harronir racial: 3min CD, 0.5s GCD, 10y puddle at the
    # target area, up to 8 enemies. Only reachable with `--race harronir`.
    thorn = {
        'off': '',
        'cd': 'thorn_bloom',
        'burst': a('thorn_bloom', CD_ACTIVE),
        'aoe': a('thorn_bloom', 'spell_targets>=2'),
        'burst_or_aoe': a('thorn_bloom', CD_ACTIVE + '|spell_targets>=3'),
    }[v['thorn']]
    if thorn:
        add('actions.trinkets+=/' + thorn)

    def emit(name, lines):
        """Write one action list, fixing up the '=' vs '+=/' on the first entry."""
        lines = [x for x in lines if x]
        for i, ln in enumerate(lines):
            add('actions.%s%s%s' % (name, '=' if i == 0 else '+=/', ln))

    # --- shared pieces --------------------------------------------------------
    mf = a('moonfire', 'dot.moonfire.remains<2|dot.moonfire.refreshable')
    sf = a('sunfire', 'dot.sunfire.remains<2|dot.sunfire.refreshable')
    # `lunar_eclipse` in the YAML is the Eclipse cast; with Lunar Calling there
    # is only one Eclipse spell in SimC.
    ecl_gate = ECLIPSE_DOWN + '&cooldown.eclipse.up'
    if not v['eclipse_yields_to_inc']:
        eclipse = a('eclipse', ecl_gate)
    else:
        eclipse = a('eclipse', ecl_gate, '!variable.inc_ready')
    # Second Eclipse line, the SimC way: refresh early when the timing variable
    # says the window would otherwise clash with a cooldown.
    eclipse2 = 'eclipse,if=variable.eclipse_timings' if v['eclipse_timings'] else ''
    inc = a('celestial_alignment', 'variable.inc_ready')
    foe = a('fury_of_elune', v['foe_gate'])
    # The YAML only casts the free Starfire inside the two `moving_*` lists, so
    # the stationary rotation never spends an Ascendant Fires proc on purpose.
    asc = a('starfire', 'buff.ascendant_fires.up') if v['ascendant_fires'] else ''

    # --- ec_st ----------------------------------------------------------------
    dots = [mf, sf]
    # Rattle the Stars discounts the spender while Eclipse is up; the SimC APL
    # spends off `action.starsurge.cost>1` instead of a flat AP floor.
    # `cost_approx` is the same idea written with expressions Simia actually has:
    # Rattle the Stars only discounts the spender while an Eclipse is up, so the
    # AP floor moves with the Eclipse instead of reading the live cost.
    ss_main = {
        'floor': a('starsurge', 'astral_power>%d' % v['ss_ap']),
        'cost': a('starsurge', 'buff.eclipse.down&astral_power.deficit<20'
                  '|buff.eclipse.up&action.starsurge.cost>1'),
        'approx': a('starsurge', 'buff.eclipse.up&astral_power>=50'
                    '|buff.eclipse.down&astral_power.deficit<20'),
    }[v['spender']]
    spend_st = [
        # Touch the Cosmos makes the next spender free; at one target the YAML
        # always burns it on Starsurge. `cosmos` is the SimC gate: with
        # Meteorites + Aetherial Kindling + Stellar Amplification and no Power of
        # Goldrinn, the free cast is worth more as Starfall while CA/Inc is down.
        {'off': '',
         'always': a('starfall', 'buff.touch_the_cosmos.react'),
         'cosmos': a('starfall', 'buff.touch_the_cosmos.react&!' + CD_ACTIVE),
         }[v['st_starfall']],
        a('starfall', 'buff.starweavers_weft.react') if v['starweaver_lines'] else '',
        a('starsurge', 'buff.starweavers_warp.react|buff.touch_the_cosmos.react')
        if v['starweaver_lines'] else a('starsurge', 'buff.touch_the_cosmos.react'),
        ss_main,
    ]
    fillers_st = [
        a('wrath', ECLIPSE_DOWN + '&spell_targets<=1') if v['wrath_filler'] else '',
        'starfire',
    ]
    core_st = [eclipse, inc, foe, eclipse2]
    emit('ec_st', (core_st + dots if v['cds_first'] else dots + core_st)
         + [asc] + spend_st + fillers_st)

    # --- aoe ------------------------------------------------------------------
    if v['multidot']:
        # What the SimC APL does and the YAML cannot: spread the DoTs over every
        # target instead of only the one under the cursor.
        aoe_dots = [
            'moonfire,target_if=refreshable&spell_targets<%d' % v['mf_cap'],
            'sunfire,target_if=refreshable',
        ]
    else:
        aoe_dots = [
            a('moonfire', 'spell_targets<%d' % v['mf_cap'], 'dot.moonfire.refreshable'),
            a('sunfire', 'dot.sunfire.refreshable'),
        ]
    sf_main = {
        'floor': a('starfall', 'astral_power>%d' % v['sf_ap']),
        'cost': a('starfall', 'buff.eclipse.down&astral_power.deficit<20'
                  '|buff.eclipse.up&action.starfall.cost>1'),
        'approx': a('starfall', 'buff.eclipse.up&astral_power>=40'
                    '|buff.eclipse.down&astral_power.deficit<20'),
    }[v['spender']]
    emit('aoe', [
        a('starfall', 'astral_power>=%d' % SF_PANIC),
    ] + aoe_dots + [
        eclipse, inc, foe, eclipse2, asc,
        a('starfall', 'buff.starweavers_weft.react|buff.touch_the_cosmos.react')
        if v['starweaver_lines'] else a('starfall', 'buff.touch_the_cosmos.react'),
        sf_main,
        a('starsurge', 'buff.starfall.up&(buff.starweavers_warp.up|buff.touch_the_cosmos.react)')
        if v['starweaver_lines'] else
        a('starsurge', 'buff.starfall.up&buff.touch_the_cosmos.react'),
        'starfire',
    ])

    return '\n'.join(L) + '\n'


def inc_ready(v):
    """`var.inc_ready_to_cast`: charges left, not already bursting, FoE aligned."""
    parts = ['cooldown.ca_inc.up', '!' + CD_ACTIVE]
    if v['inc_foe_align']:
        parts.append('(cooldown.fury_of_elune.remains<2|buff.fury_of_elune.up)')
    return '&'.join(parts)


DEFAULTS = dict(inc_foe_align=True, eclipse_yields_to_inc=True, cds_first=False,
                starweaver_lines=True, ss_ap=SS_AP, sf_ap=SF_AP, wrath_filler=True,
                foe_gate='', trinkets='ferraz', aoe_threshold=2, opener_simc=False,
                eclipse_timings=False, ascendant_fires=False, spender='floor',
                multidot=False, prepot=False, st_starfall='off', thorn='off',
                hotw='off', mf_cap=MOONFIRE_CAP)

VARIANTS = {
    'ferraz':        ({}, 'A rotacao atual do FerrazBalance.yaml'),
    'inc_asap':      (dict(inc_foe_align=False), 'Incarnation sem esperar Fury of Elune'),
    'ecl_over_inc':  (dict(eclipse_yields_to_inc=False), 'Eclipse mesmo com Incarnation pronto'),
    'cds_first':     (dict(cds_first=True), 'Eclipse/Inc/FoE na frente dos DoTs'),
    'no_starweaver': (dict(starweaver_lines=False), 'Remove as linhas mortas de Starweaver'),
    'ss_ap_50':      (dict(ss_ap=50), 'Starsurge em AP>50 (gasta mais cedo)'),
    'ss_ap_70':      (dict(ss_ap=70), 'Starsurge em AP>70 (segura mais)'),
    'ss_ap_80':      (dict(ss_ap=80), 'Starsurge so perto do cap'),
    'sf_ap_40':      (dict(sf_ap=40), 'Starfall em AP>40 no AoE'),
    'sf_ap_60':      (dict(sf_ap=60), 'Starfall em AP>60 no AoE'),
    'no_wrath':      (dict(wrath_filler=False), 'So Starfire de filler no ST'),
    # Is the <6 Moonfire cap still the right cutoff on the current gear?
    'nw_mf_99':      (dict(wrath_filler=False, mf_cap=99), 'Sem Wrath + Moonfire sem cap de alvos'),
    'nw_mf_4':       (dict(wrath_filler=False, mf_cap=4), 'Sem Wrath + Moonfire so ate 4 alvos'),
    # DEFAULTS carries wrath_filler=True, but the YAML ships it OFF — so
    # `no_wrath` is the real baseline for the file, not `ferraz`. These
    # variants re-test the AP floor against that correct baseline.
    'nw_ss_50':      (dict(wrath_filler=False, ss_ap=50), 'Sem Wrath + Starsurge em AP>50'),
    'nw_ss_70':      (dict(wrath_filler=False, ss_ap=70), 'Sem Wrath + Starsurge em AP>70'),
    'nw_ss_80':      (dict(wrath_filler=False, ss_ap=80), 'Sem Wrath + Starsurge perto do cap'),
    'foe_off_cd':    (dict(foe_gate='cooldown.ca_inc.remains>10|talent.lunation'),
                      'Fury of Elune com o gate do APL padrao'),
    'no_trinkets':   (dict(trinkets='off'), 'Trinkets/pocao desligados, como o default do YAML'),
    'trinkets_simc': (dict(trinkets='simc'), 'Trinkets sem exigir Fury of Elune em CD'),
    'trinkets_free': (dict(spender='approx', trinkets='free'), 'Trinkets sempre que prontos, fora do burst'),
    'v2_trinkets_burst': (dict(spender='approx'), 'ferraz_v2: trinkets presos ao burst (atual)'),
    'aoe_at_3':      (dict(aoe_threshold=3), 'So entra na lista aoe com 3+ alvos'),
    'aoe_at_4':      (dict(aoe_threshold=4), 'So entra na lista aoe com 4+ alvos'),
    'opener_simc':   (dict(opener_simc=True), 'Tres Wraths de precombat, como o SimC'),
    # --- o que o APL padrao faz e a rotacao nao ------------------------------
    'ecl_timings':   (dict(eclipse_timings=True), 'Segunda linha de Eclipse com variable.eclipse_timings'),
    'asc_fires':     (dict(ascendant_fires=True), 'Starfire de graca com Ascendant Fires tambem parado'),
    'cost_spender':  (dict(spender='cost'), 'Gasta por action.cost>1 (Rattle the Stars) em vez de piso de AP'),
    'cost_approx':   (dict(spender='approx'), 'Idem, escrito so com expressoes que o Simia tem'),
    'multidot':      (dict(multidot=True), 'Espalha Moonfire/Sunfire com target_if no AoE'),
    'simc_like':     (dict(eclipse_timings=True, ascendant_fires=True, spender='cost',
                           multidot=True, opener_simc=True),
                      'Todas as quatro mudancas acima juntas'),
    'prepot':        (dict(prepot=True), 'Pocao no precombat, como o SimC'),
    'st_starfall':   (dict(st_starfall='always'), 'Gasta Touch the Cosmos em Starfall no ST'),
    'st_sf_cosmos':  (dict(st_starfall='cosmos'), 'Idem, mas so fora de CA/Incarnation (gate do SimC)'),
    'st_best':       (dict(st_starfall='cosmos', spender='cost', wrath_filler=False,
                           opener_simc=True),
                      'TtC em Starfall + cost_spender + so Starfire + opener do SimC'),
    'potion_2x':     (dict(trinkets='twopot', prepot=True), 'Pre-pot + pocao no fim da luta'),
    # `ferraz_v2` e o que da para escrever no YAML de fato: sem o Wrath filler,
    # Touch the Cosmos em Starfall fora do burst e o gasto amarrado ao Eclipse.
    # `ferraz_v2` is what actually landed in the YAML: the Eclipse-tied spender.
    # The Wrath filler and the Touch-the-Cosmos Starfall both won on Patchwerk and
    # LOST on DungeonSlice, so neither was applied.
    'ferraz_v2':     (dict(spender='approx'), 'A rotacao com as mudancas aplicadas no YAML'),
    'ferraz_v2_md':  (dict(spender='approx', multidot=True),
                      'ferraz_v2 + espalhar DoTs (o que a lista de mouseover busca)'),
    # --- Heart of the Wild como cooldown de dano -----------------------------
    'hotw_cd':       (dict(spender='approx', hotw='cd'), 'HotW no CD, sem alinhar com nada'),
    'hotw_burst':    (dict(spender='approx', hotw='burst'), 'HotW dentro do Incarnation'),
    'hotw_pre':      (dict(spender='approx', hotw='pre_burst'), 'HotW junto/antes do Incarnation'),
    # --- Thorn Bloom (racial Harronir; exige --race harronir) ----------------
    'tb_cd':         (dict(spender='approx', thorn='cd'), 'ferraz_v2 + Thorn Bloom puro no CD'),
    'tb_burst':      (dict(spender='approx', thorn='burst'), 'Thorn Bloom so dentro do burst'),
    'tb_aoe':        (dict(spender='approx', thorn='aoe'), 'Thorn Bloom so com 2+ alvos'),
    'tb_mixed':      (dict(spender='approx', thorn='burst_or_aoe'), 'Thorn Bloom no burst ou com 3+ alvos'),
    'v2_no_wrath':   (dict(spender='approx', wrath_filler=False),
                      'ferraz_v2 sem o Wrath filler'),
    'patchwerk_only': (dict(st_starfall='cosmos', spender='approx', wrath_filler=False),
                       'ferraz_v2 + as duas mudancas que so ganham em Patchwerk'),
    'st_best2':      (dict(st_starfall='cosmos', spender='cost', wrath_filler=False,
                           opener_simc=True, trinkets='twopot', prepot=True),
                      'st_best + as duas pocoes'),
    # --- incremental: em cima da base real do YAML (v2 + sem Wrath filler) ---
    'base_now':      (dict(spender='approx', wrath_filler=False),
                      'BASE = o que o YAML faz hoje (v2, Wrath filler OFF)'),
    'now_ecl_over':  (dict(spender='approx', wrath_filler=False, eclipse_yields_to_inc=False),
                      'BASE + Eclipse mesmo com Incarnation pronto'),
    'now_trk_free':  (dict(spender='approx', wrath_filler=False, trinkets='free'),
                      'BASE + trinkets sempre que prontos'),
    'now_inc_asap':  (dict(spender='approx', wrath_filler=False, inc_foe_align=False),
                      'BASE + Incarnation sem esperar Fury of Elune'),
    'now_pot2x':     (dict(spender='approx', wrath_filler=False, trinkets='twopot', prepot=True),
                      'BASE + pre-pot e segunda pocao'),
    'now_md':        (dict(spender='approx', wrath_filler=False, multidot=True),
                      'BASE + espalhar DoTs (multidot)'),
    'now_all':       (dict(spender='approx', wrath_filler=False, eclipse_yields_to_inc=False,
                           trinkets='free', inc_foe_align=False),
                      'BASE + as tres melhores juntas'),
    'now_pot_end':   (dict(spender='approx', wrath_filler=False, trinkets='twopot'),
                      'BASE + 2a pocao no fim da luta (SEM pre-pot)'),
    'now_prepot':    (dict(spender='approx', wrath_filler=False, prepot=True),
                      'BASE + apenas pre-pot'),
}


def run(name, error, enemies, style, race=''):
    os.makedirs(APL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    apl = os.path.join(APL_DIR, '%s.simc' % name)
    js = os.path.join(OUT_DIR, '%s_%dt_%s%s.json' % (name, enemies, style or 'patchwerk',
                                                     '_' + race if race else ''))
    if name != 'simc_default':
        v = dict(DEFAULTS)
        v.update(VARIANTS[name][0])
        with open(apl, 'w', encoding='utf-8') as fh:
            fh.write(build(v))
    cmd = [SIMC, PROFILE]
    if race:
        # Must come after the profile so it overrides the race it declares.
        cmd.append('race=' + race)
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
    error = '0.2'
    enemies = 1
    style = ''
    race = ''
    names = []
    i = 0
    while i < len(argv):
        if argv[i] == '--error':
            error = argv[i + 1]; i += 2; continue
        if argv[i] == '--race':
            race = argv[i + 1]; i += 2; continue
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
        r = run(n, error, enemies, style, race)
        results[n] = r
        print('%.0f DPS' % r[0] if r else 'failed')

    ref = results.get('ferraz')
    print('\n%-16s %10s %8s %10s  %s' % ('variant', 'DPS', '+/-', 'vs ferraz', 'what'))
    print('-' * 78)
    for n in names:
        r = results[n]
        if not r:
            continue
        mean, err, _ = r
        delta = ''
        if ref and n != 'ferraz':
            d = mean - ref[0]
            # combined error of the two means; 2x is roughly 95% confidence
            comb = 2 * (err ** 2 + ref[1] ** 2) ** 0.5
            delta = '%+.2f%%%s' % (100 * d / ref[0], '' if abs(d) > comb else ' ~')
        what = 'APL padrao do SimC' if n == 'simc_default' else VARIANTS[n][1]
        print('%-16s %10.0f %8.0f %10s  %s' % (n, mean, err, delta, what))
    print('\n"~" = dentro da margem de erro, nao e diferenca real.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

