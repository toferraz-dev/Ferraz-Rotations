"""A/B harness: measure the Ferraz Guardian rotation against the SimC default,
and isolate one change per variant.

The Simia YAML cannot be fed to SimulationCraft, so the damage half of
FerrazGuardianElune.yaml is translated here into a SimC action list. Everything
the sim does not model is dropped on purpose: defensives, taunt, interrupts,
mouseover casts, the tank-buster prediction, and auto_heal.

Each variant differs from `ferraz` by exactly one edit, so the delta is
attributable. Run:

    python sim/ab_test.py                # every variant
    python sim/ab_test.py ferraz no_gory # just these
    python sim/ab_test.py --error 0.1    # tighter (slower)
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.2165324-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Tassiana_guardian.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl')
OUT_DIR = os.path.join(ROOT, 'sim', 'out')

# --- config values, mirrored from the YAML defaults --------------------------
RAGE_DEFICIT_MAUL = 20      # config.rage_deficit_maul
RAGE_CAP = 100              # Fount of Strength is not talented
MAUL_RAGE = RAGE_CAP - RAGE_DEFICIT_MAUL
HOTW_DELAY = 8              # config.hotw_delay
HOTW_HP = 80                # config.hotw_hp_pct

# --- spell_overrides, AND-ed into every occurrence of the spell --------------
# var.heavy_incoming has no SimC equivalent: on Patchwerk incoming damage is
# flat, so the predictive branch never flips. It is treated as always false,
# which is the rotation's own damage-favouring path.
OV_MANGLE = ('buff.bear_form.down|rage<=30&buff.gore.up&!cooldown.thrash.up'
             '&active_enemies<=3')
OV_MOONFIRE = '!talent.lunar_calling.enabled|!cooldown.thrash.up'
OV_INCARN = '!buff.incarnation_guardian_of_ursoc.up'

THRASH_STACKS = ('dot.thrash.refreshable|dot.thrash.stack<5&talent.flashing_claws.rank=2'
                 '|dot.thrash.stack<4&talent.flashing_claws.rank=1'
                 '|dot.thrash.stack<3&!talent.flashing_claws.enabled')
MANGLE_RAGE = ('((rage<88)&!talent.fount_of_strength.enabled)'
               '|((rage<83)&!talent.fount_of_strength.enabled&talent.soul_of_the_forest.enabled)'
               '|((rage<108)&talent.fount_of_strength.enabled)'
               '|((rage<103)&talent.fount_of_strength.enabled&talent.soul_of_the_forest.enabled)')


def a(action, *conds):
    """Join an action with its conditions, dropping empties."""
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    """Emit the action lists for one variant. `v` holds the toggles."""
    L = []
    add = L.append
    # Toggles that blank out a whole override for the A/B.
    global OV_MANGLE_CUR, OV_MOONFIRE_CUR
    OV_MANGLE_CUR = {
        'full': OV_MANGLE,
        'gore': 'buff.bear_form.down|buff.gore.up',
        'rage_gore': 'buff.bear_form.down|rage<=30&buff.gore.up',
        'none': '',
    }[v['mangle_override']]
    OV_MOONFIRE_CUR = {
        'full': OV_MOONFIRE,
        'gcd': '!talent.lunar_calling.enabled|cooldown.thrash.remains>gcd',
        'gcd2': '!talent.lunar_calling.enabled|cooldown.thrash.remains>2*gcd',
        'none': '',
    }[v['moonfire_override']]

    add('actions.precombat=snapshot_stats')
    add('actions.precombat+=/bear_form')

    add('actions=auto_attack')
    add('actions+=/call_action_list,name=hotw')
    add('actions+=/call_action_list,name=cooldowns')
    add('actions+=/call_action_list,name=bear')
    thr = v['aoe_threshold']
    add('actions+=/call_action_list,name=aoe,if=active_enemies>=%d' % thr)
    add('actions+=/call_action_list,name=st,if=active_enemies<%d' % thr)

    # --- Heart of the Wild weave (from `main`) --------------------------------
    drop = v['hotw_drop']
    parts = ['talent.heart_of_the_wild.enabled', 'cooldown.heart_of_the_wild.up']
    if 'time' not in drop:
        parts.append('time>=%d' % HOTW_DELAY)
    if 'hp' not in drop:
        parts.append('health.pct>=%d' % HOTW_HP)
    if 'ironfur' not in drop:
        parts.append('buff.ironfur.up')
    parts += ['!buff.incarnation_guardian_of_ursoc.up', '!buff.berserk.up']
    weave = '&'.join(parts)
    if v['hotw_weave']:
        add('actions.hotw=' + a('cat_form', weave + '&buff.cat_form.down'))
    else:
        add('actions.hotw=bear_form,if=!buff.bear_form.up')
    add('actions.hotw+=/' + a('heart_of_the_wild',
                              'buff.cat_form.up&cooldown.heart_of_the_wild.up'))
    add('actions.hotw+=/' + a('bear_form',
                              'buff.cat_form.up&(!cooldown.heart_of_the_wild.up'
                              '|health.pct<%d)' % HOTW_HP))

    # --- cooldowns ------------------------------------------------------------
    lunar = 'cooldown.incarnation_guardian_of_ursoc.up|cooldown.berserk.up' if v['lunar_sync'] else ''
    # Berserk/Incarnation after the HotW window, the way SimC orders them.
    burst_gate = '!cooldown.heart_of_the_wild.up' if v['burst_after_hotw'] else ''
    add('actions.cooldowns=use_items')
    # Barkskin is kept because Matted Fur turns it into an absorb, which shows up
    # in the ability breakdown (it does not move the dps metric, but it makes the
    # breakdown comparable to the SimC default APL, which also casts it).
    # Frenzied Regeneration is deliberately NOT here: `frenzied_regeneration,
    # if=health.pct<=75` segfaults simc 1210-01 on any multi-target sim. It
    # contributed nothing to dps at one target, so nothing is lost by omitting it.
    add('actions.cooldowns+=/' + a('barkskin', 'buff.bear_form.up'))
    add('actions.cooldowns+=/' + a('lunar_beam', lunar))
    # Only `berserk` here: in SimC, Incarnation is a parse-time redirect off
    # berserk when the talent is taken, so an explicit incarnation action does
    # not exist. The Simia YAML needs both lines; SimC refuses the second one.
    add('actions.cooldowns+=/' + a('berserk', OV_INCARN, burst_gate))
    # Combat potion. 'burst' rides the Berserk/Incarnation buff (in SimC
    # Incarnation is a redirect off berserk, so both buff names are checked);
    # 'cd' fires it the moment it is ready, which is what measures whether the
    # sync is worth anything at all. fight_remains<32 stops a potion being
    # carried unused to the end of the fight.
    if v['potion'] == 'burst':
        add('actions.cooldowns+=/' + a('potion',
            'buff.berserk.up|buff.incarnation_guardian_of_ursoc.up|fight_remains<32'))
    elif v['potion'] == 'cd':
        add('actions.cooldowns+=/potion')
    elif v['potion'] == 'burst_or_early':
        # Prefers the burst window, but refuses to sit on the potion when
        # Berserk/Incarnation is still far away (the rotation holds it for
        # the HotW weave, so 'wait for burst' can mean waiting a long time).
        add('actions.cooldowns+=/' + a('potion',
            'buff.berserk.up|buff.incarnation_guardian_of_ursoc.up'
            '|cooldown.berserk.remains>30|fight_remains<32'))
    add('actions.cooldowns+=/' + a('wild_guardian', 'buff.lunar_beam.up'))
    for r in ('blood_fury', 'berserking', 'fireblood', 'ancestral_call'):
        add('actions.cooldowns+=/' + r)

    # --- bear: form, rage spending -------------------------------------------
    ofg = ',use_off_gcd=1' if v['ironfur_off_gcd'] else ''
    dump = 40 if v['ironfur_rage40'] else 80
    add('actions.bear=' + a('bear_form', '!buff.bear_form.up&!buff.cat_form.up'))
    if v['bear_mangle']:
        add('actions.bear+=/' + a('mangle', 'rage<=30', OV_MANGLE_CUR))
    if v['mf_gg'] == 'bear':
        add('actions.bear+=/' + a('moonfire', 'buff.galactic_guardian.up', OV_MOONFIRE_CUR))
    add('actions.bear+=/' + a('ironfur' + ofg, 'buff.ironfur.remains<2'))
    add('actions.bear+=/' + a('ironfur' + ofg, 'rage>=%d' % dump))
    if v['gory_fur']:
        add('actions.bear+=/' + a('maul', 'buff.gory_fur_maul.up&!talent.raze.enabled'
                                  '&active_enemies<3&buff.ironfur.up'))
        add('actions.bear+=/' + a('raze', 'buff.gory_fur_maul.up&talent.raze.enabled'
                                  '&buff.ironfur.up'))
    if v['raze_aoe_gate']:
        # the pre-fix shape: Maul ungated, Raze held for 3+ targets
        add('actions.bear+=/' + a('maul', 'buff.ironfur.up&rage>=%d' % MAUL_RAGE))
        add('actions.bear+=/' + a('raze', 'talent.raze.enabled&active_enemies>=3'
                                  '&buff.ironfur.up&rage>=%d' % MAUL_RAGE))
    else:
        add('actions.bear+=/' + a('maul', '!talent.raze.enabled&buff.ironfur.up'
                                  '&rage>=%d' % MAUL_RAGE))
        add('actions.bear+=/' + a('raze', 'talent.raze.enabled&buff.ironfur.up'
                                  '&rage>=%d' % MAUL_RAGE))

    def emit(name, lines):
        """Write one action list, fixing up the '=' vs '+=/' on the first entry."""
        lines = [x for x in lines if x]
        for i, ln in enumerate(lines):
            add('actions.%s%s%s' % (name, '=' if i == 0 else '+=/', ln))

    mangle_burst = (a('mangle', '(buff.incarnation_guardian_of_ursoc.up|buff.berserk.up)'
                      '&buff.feline_potential_counter.stack<6&talent.wildpower_surge.enabled',
                      OV_MANGLE_CUR) if v['wildpower_line'] else '')
    mangle_main = a('mangle', '(buff.incarnation_guardian_of_ursoc.up|buff.berserk.up)|'
                    + MANGLE_RAGE, OV_MANGLE_CUR)
    # Lunation Moonfire, optionally carrying the target cap SimC puts on it.
    lunation_cond = 'talent.lunation.enabled&buff.bear_form.up'
    if v['mf_lunation_capped']:
        lunation_cond += '&active_enemies<3'

    # --- st -------------------------------------------------------------------
    mf_maint = a('moonfire', 'dot.moonfire.refreshable', OV_MOONFIRE_CUR) if v['mf_maintain'] else ''
    emit('st', [
        mf_maint if v['mf_maintain_first'] else '',
        a('thrash', 'cooldown.thrash.up&talent.lunar_calling.enabled'),
        (a('moonfire', 'talent.lunar_calling.enabled&buff.bear_form.up') if v['lc_companion'] else ''),
        a('thrash', 'cooldown.thrash.up', THRASH_STACKS),
        '' if v['mf_maintain_first'] else mf_maint,
        a('moonfire', 'cooldown.mangle.remains<=gcd', OV_MOONFIRE_CUR) if v['mf_st_prio'] else '',
        mangle_burst,
        mangle_main,
        a('moonfire', 'buff.galactic_guardian.up', OV_MOONFIRE_CUR) if v['mf_gg'] == 'late' else '',
        a('thrash', 'cooldown.thrash.up'),
        a('moonfire', lunation_cond, OV_MOONFIRE_CUR) if v['mf_lunation'] else '',
        'swipe_bear',
    ])

    # --- aoe ------------------------------------------------------------------
    emit('aoe', [
        a('thrash', 'cooldown.thrash.up&talent.lunar_calling.enabled'),
        (a('moonfire', 'talent.lunar_calling.enabled&buff.bear_form.up') if v['lc_companion'] else ''),
        a('thrash', 'cooldown.thrash.up', THRASH_STACKS),
        a('moonfire', 'dot.moonfire.refreshable', OV_MOONFIRE_CUR) if v['mf_maintain'] else '',
        mangle_burst,
        mangle_main,
        a('moonfire', 'buff.galactic_guardian.up', OV_MOONFIRE_CUR) if v['mf_gg'] == 'late' else '',
        a('thrash', 'cooldown.thrash.up'),
        'swipe_bear',
    ])

    return '\n'.join(L) + '\n'


DEFAULTS = dict(ironfur_off_gcd=True, gory_fur=True, raze_aoe_gate=False,
                ironfur_rage40=False, lunar_sync=False, burst_after_hotw=True,
                mf_maintain=True, mf_st_prio=False, mf_lunation=True,
                mf_lunation_capped=False, mf_gg='late', wildpower_line=True,
                mangle_override='none', moonfire_override='full', lc_companion=False,
                mf_maintain_first=True, bear_mangle=False, hotw_weave=True, hotw_drop=(), aoe_threshold=2,
                potion='off')

VARIANTS = {
    'ferraz':        ({}, 'A rotacao atual, apos os fixes de hoje'),
    'potion_burst':  (dict(potion='burst'), 'Combat potion junto com Incarnation/Berserk'),
    'potion_cd':     (dict(potion='cd'), 'Combat potion assim que fica pronto, sem sync'),
    'potion_mid':    (dict(potion='burst_or_early'), 'Potion no burst, mas nao espera se Berserk esta longe'),
    'no_off_gcd':    (dict(ironfur_off_gcd=False), 'Ironfur volta a comer GCD (mede o item 1)'),
    'no_gory':       (dict(gory_fur=False), 'Sem as linhas de Gory Fur (mede o item 2)'),
    'raze_gated':    (dict(raze_aoe_gate=True), 'Raze preso em 3+ alvos (mede o item 3)'),
    'ironfur_40':    (dict(ironfur_rage40=True), 'Dump de Ironfur em rage>=40 como o SimC'),
    'lunar_sync':    (dict(lunar_sync=True), 'Lunar Beam sincronizado com Incarnation/Berserk'),
    'burst_early':   (dict(burst_after_hotw=False), 'Volta Incarnation/Berserk imediatos'),
    'mf_no_maintain': (dict(mf_maintain=False), 'Sem Moonfire (maintain)'),
    'mf_st_prio_back': (dict(mf_st_prio=True), 'Devolve Moonfire (ST prio)'),
    'mf_no_lunation': (dict(mf_lunation=False), 'Sem Moonfire (Lunation)'),
    'mf_lun_capped': (dict(mf_lunation_capped=True), 'Moonfire (Lunation) so com <3 alvos, como o SimC'),
    'mf_no_gg':      (dict(mf_gg='off'), 'Sem Moonfire (GG proc)'),
    'mf_gg_early':   (dict(mf_gg='bear'), 'Devolve o GG proc para o topo do bear'),
    'mf_combo':      (dict(mf_st_prio=False, mf_gg='off'), 'Sem ST prio E sem GG'),
    'mf_combo_late': (dict(mf_st_prio=False, mf_gg='late'), 'Sem ST prio, GG movido para depois do Mangle'),
    'mf_simc_like':  (dict(mf_maintain=False, mf_st_prio=False, mf_lunation_capped=True),
                      'So GG + Lunation capado, como o SimC'),
    'no_wildpower':  (dict(wildpower_line=False), 'Remove as linhas mortas de Wildpower Surge'),
    'mangle_ov_full': (dict(mangle_override='full'), 'Volta o override antigo do Mangle'),
    'mf_ov_gcd':     (dict(moonfire_override='gcd'), 'Moonfire so se o Thrash faltar >1 GCD'),
    'mf_ov_gcd2':    (dict(moonfire_override='gcd2'), 'Moonfire so se o Thrash faltar >2 GCDs'),
    'mf_ov_none':    (dict(moonfire_override='none'), 'Moonfire sem override nenhum'),
    'lc_companion':  (dict(lc_companion=True), 'Linha Moonfire companheira do Thrash (estilo rotation_104)'),
    'mf_maint_late': (dict(mf_maintain_first=False), 'Moonfire (maintain) depois das duas linhas de Thrash'),
    'bear_mangle_back': (dict(bear_mangle=True), 'Devolve o Mangle filler de rage<=30'),
    'thrash_first':  (dict(mf_maintain_first=False, bear_mangle=False), 'Thrash na frente de tudo'),
    'mf_only_gg':    (dict(mf_maintain=False, mf_lunation=False), 'So o Moonfire de GG proc, sem maintain nem Lunation'),
    'mf_only_gg_tf': (dict(mf_maintain=False, mf_lunation=False, bear_mangle=False),
                      'So GG proc + sem o Mangle filler'),
    'best_guess':    (dict(mf_lunation=False, mf_maintain_first=False, bear_mangle=False),
                      'Sem Lunation, maintain tarde, sem Mangle filler'),
    'mangle_ov_gore': (dict(mangle_override='gore'), 'Mangle so exige proc de Gore'),
    'mangle_ov_rage': (dict(mangle_override='rage_gore'), 'Mangle: rage<=30 & Gore, sem as clausulas de Thrash/alvos'),
    'hotw_no_time':  (dict(hotw_drop=('time',)), 'Gate do HotW sem o delay de 8s'),
    'hotw_no_hp':    (dict(hotw_drop=('hp',)), 'Gate do HotW sem o piso de 80% HP'),
    'hotw_no_if':    (dict(hotw_drop=('ironfur',)), 'Gate do HotW sem exigir Ironfur ativo'),
    'hotw_loose':    (dict(hotw_drop=('time', 'hp', 'ironfur')), 'Gate do HotW sem as tres clausulas'),
    'no_hotw':       (dict(hotw_weave=False), 'Sem o weave de Heart of the Wild'),
    'aoe_at_3':      (dict(aoe_threshold=3), 'Volta o limiar de AoE para 3 alvos'),
    'aoe_at_4':      (dict(aoe_threshold=4), 'So entra na lista aoe com 4+ alvos'),
    'combo':         (dict(burst_after_hotw=True, aoe_threshold=2), 'burst_late + aoe_at_2 juntos'),
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
    error = '0.2'
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
