"""A/B harness: measure the Ferraz Feral (M+) rotation against the SimC
default (dreamgrove-sourced, already tuned for this exact Wildstalker talent
build and DungeonSlice), and isolate one change per variant.

The Simia YAML cannot be fed to SimulationCraft, so the damage half of
FerrazFeral.yaml is translated here into a SimC action list.

Run:
    python sim/ab_test_feral.py                    # every variant
    python sim/ab_test_feral.py ferraz simc_default
    python sim/ab_test_feral.py --error 0.2
    python sim/ab_test_feral.py --targets 3
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.62ca36f-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Ferraz_feral.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl_feral')
OUT_DIR = os.path.join(ROOT, 'sim', 'out_feral')


def a(action, *conds):
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    L = []
    add = L.append

    add('actions.precombat=snapshot_stats')
    add('actions.precombat+=/cat_form,if=buff.cat_form.down')
    add('actions.precombat+=/prowl')
    # rake_tf/rip_tf check debuff.X.visual_id in the YAML (which spell-morph
    # animation applied the DoT) — a Simia-only expression SimC has no
    # equivalent for. Pinned to 0/false: not central to this harness's
    # findings (missing CDs, TF hold, dotc formula).
    add('actions.precombat+=/variable,name=rake_tf,value=0')
    add('actions.precombat+=/variable,name=rip_tf,value=0')

    add('actions=prowl,if=buff.bs_inc.down&!buff.prowl.up&!buff.shadowmeld.up')
    add('actions+=/cat_form,if=!buff.cat_form.up')
    add('actions+=/auto_attack,if=!buff.prowl.up&!buff.shadowmeld.up')

    # Tiger's Fury: FerrazFeral.yaml's hold-for-Frantic-Frenzy clause has no
    # equivalent of the SimC default's fight_style.dungeonslice escape hatch
    # (dreamgrove disables that hold specifically in dungeon fight styles).
    # Since this file is M+-only, that escape hatch should just always apply.
    tf_hold = '' if v['tf_no_hold'] else \
        'cooldown.frantic_frenzy.remains<buff.tigers_fury.duration-1.5' \
        '|cooldown.frantic_frenzy.remains>22|!talent.frantic_frenzy|spell_targets=1'
    tf_cond = a('', '(cooldown.bs_inc.remains<=1|cooldown.bs_inc.remains>10|variable.holdBerserk)', tf_hold)
    add('actions+=/tigers_fury,use_off_gcd=1' + tf_cond)
    add('actions+=/rake,if=buff.prowl.up|buff.shadowmeld.up')
    add('actions+=/chomp,if=buff.chomp_enabler.up')
    add('actions+=/call_action_list,name=cd_variable,if=!cooldown.bs_inc.remains|!cooldown.convoke_the_spirits.remains')
    add('actions+=/call_action_list,name=cooldown')
    add('actions+=/ferocious_bite,if=buff.apex_predators_craving.up')
    add('actions+=/call_action_list,name=finisher,if=spell_targets=1')
    add('actions+=/call_action_list,name=aoe_finisher,if=spell_targets>=2')
    add('actions+=/call_action_list,name=builder,if=spell_targets=1&combo_points<=4')
    add('actions+=/call_action_list,name=aoe_builder,if=spell_targets>1&combo_points<=4')

    # --- cd_variable: holdBerserk, the only hold-logic FerrazFeral.yaml
    # already computes (verbatim from its own `variables:` block) ---
    add('actions.cd_variable=variable,name=convokeCountRemaining,'
        'value=floor(cooldown.convoke_the_spirits.charges_fractional+fight_remains%cooldown.convoke_the_spirits.duration-0.05)')
    add('actions.cd_variable+=/variable,name=zerkCountRemaining,'
        'value=floor(cooldown.bs_inc.charges_fractional+fight_remains%cooldown.bs_inc.duration-0.05)')
    add('actions.cd_variable+=/variable,name=holdBerserk,'
        'value=(variable.zerkCountRemaining=1&variable.convokeCountRemaining=1&cooldown.convoke_the_spirits.remains>10)'
        '|(cooldown.convoke_the_spirits.remains>20&variable.convokeCountRemaining=variable.zerkCountRemaining)')

    # --- cooldown: feral_frenzy/frantic_frenzy is the ONLY thing
    # FerrazFeral.yaml's `cooldown` list has today. `missing_cds` restores
    # what it never had: Berserk itself, Convoke the Spirits (talented),
    # racial, trinkets, potion. ---
    # TTD gates, mirroring the YAML's ttd_* variables. SimC has no boss flag on
    # a dummy and knows fight_remains exactly, so target.boss drops out and each
    # gate reduces to the fight_remains clause. That means TTD can only ever
    # HOLD a cooldown back here, never gain anything — the point of measuring it
    # is to confirm the cost is zero, since the real gain (trash that dies early)
    # is unmodellable.
    ttd_zerk = 'fight_remains>=15' if v['ttd'] else ''
    ttd_conv = 'fight_remains>=8' if v['ttd'] else ''
    ttd_trk = 'fight_remains>=10' if v['ttd'] else ''
    ttd_pot = 'fight_remains>=15' if v['ttd'] else ''
    cd = ['call_action_list,name=cd_variable,if=!cooldown.bs_inc.remains|!cooldown.convoke_the_spirits.remains']
    if not v['no_cds']:
        pot = '(buff.bs_inc.up&%s)|fight_remains<32' % ttd_pot if ttd_pot             else 'buff.bs_inc.up|fight_remains<32'
        cd += [
            a('use_items', ttd_trk),
            a('berserking'),
            a('potion', pot),
            a('berserk', 'buff.tigers_fury.up&!variable.holdBerserk', ttd_zerk),
        ]
    cd += [
        a('feral_frenzy', '!talent.frantic_frenzy&combo_points<=2+(2*buff.bs_inc.up)'),
        a('frantic_frenzy', 'buff.tigers_fury.up|combo_points<=2+(2*buff.bs_inc.up)'),
    ]
    if not v['no_cds']:
        # The TTD gate goes on the burst clause only, never on the trailing
        # fight_remains<5 escape — wrapping the whole expression would make the
        # escape unreachable, which is not what the YAML does (it has no such
        # escape clause at all).
        main_conv = ('buff.bs_inc.up&%sbuff.tigers_fury.up&(prev_gcd.1.rip'
                     '|prev_gcd.1.ferocious_bite|prev_gcd.1.primal_wrath'
                     '|buff.tigers_fury.remains<=1+action.convoke_the_spirits.execute_time)'
                     % (ttd_conv + '&' if ttd_conv else ''))
        cd.append(a('convoke_the_spirits', main_conv + '|fight_remains<5'))
    for i, ln in enumerate(cd):
        add('actions.cooldown%s%s' % ('=' if i == 0 else '+=/', ln))

    # --- finisher / aoe_finisher / builder: byte-for-byte from the YAML ---
    # Apex Predator's Craving fires a free finisher off the top of the list.
    # The YAML has it; it was dead on Wildstalker and is live again on DotC.
    if v['apex_ravage']:
        add('actions.finisher=ferocious_bite,if=buff.apex_predators_craving.up')
        add('actions.finisher+=/rip,if=combo_points>=5&(dot.rip.refreshable&(buff.tigers_fury.up|dot.rip.remains<cooldown.tigers_fury.remains)|buff.tigers_fury.up&!variable.rip_tf&dot.rip.ticking|buff.tigers_fury.up&buff.tigers_fury.remains<2&dot.rip.ticking)')
    else:
        add('actions.finisher=rip,if=combo_points>=5&(dot.rip.refreshable&(buff.tigers_fury.up|dot.rip.remains<cooldown.tigers_fury.remains)|buff.tigers_fury.up&!variable.rip_tf&dot.rip.ticking|buff.tigers_fury.up&buff.tigers_fury.remains<2&dot.rip.ticking)')
    if v.get('bite_pool'):
        add('actions.finisher+=/pool_resource,for_next=1')
        add('actions.finisher+=/ferocious_bite,max_energy=1,if=combo_points>=5')
    else:
        add('actions.finisher+=/pool_resource,for_next=1,if=energy<50')
        add('actions.finisher+=/ferocious_bite,if=combo_points>=5')

    add('actions.aoe_finisher=primal_wrath,if=combo_points>=5&spell_targets>1&(dot.rip.remains<6.5&!buff.bs_inc.up|dot.rip.refreshable)')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5&!talent.primal_wrath&spell_targets>=2+(3*!talent.rampant_ferocity)')
    add('actions.aoe_finisher+=/rip,if=combo_points>=5&!talent.primal_wrath&(!dot.rip.ticking|dot.rip.refreshable&(buff.tigers_fury.up|!variable.rip_tf))')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5&(talent.rampant_ferocity|buff.ravage.up&spell_targets<8|dot.bloodseeker_vines.ticking&spell_targets<5)')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5&(talent.rampant_ferocity|spell_targets<8|dot.bloodseeker_vines.ticking&spell_targets<5)')
    add('actions.aoe_finisher+=/primal_wrath,if=combo_points>=5')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5')

    add('actions.builder=prowl,if=!buff.shadowmeld.up&(!variable.rake_tf|dot.rake.refreshable)')
    add('actions.builder+=/rake,if=(buff.tigers_fury.up|dot.rake.remains<cooldown.tigers_fury.remains)&(dot.rake.refreshable&(buff.tigers_fury.up|!variable.rake_tf)|dot.rake.remains<2|buff.tigers_fury.up&!variable.rake_tf)')
    if v['sudden_ambush_shred']:
        # dreamgrove keeps a Druid-of-the-Claw-only Shred on a Sudden Ambush
        # proc. It measured +2.35% in the raid file; the M+ build only became
        # eligible for it when it moved back to Druid of the Claw.
        add('actions.builder+=/shred,if=buff.sudden_ambush.up&hero_tree.druid_of_the_claw')
    add('actions.builder+=/shred')

    # --- aoe_builder: the dotc_rake_threshold formula is the one place the
    # YAML's own math diverges from the real APL's (talent.wild_slashes &
    # talent.merciless_claws, not the YAML's talent.wild_slashes &
    # !talent.infected_wounds). Both give the same number on THIS build
    # (wild_slashes untalented either way -> 99), so `dotc_fix` is here to
    # measure it, not because it is expected to move the needle.
    dotc_threshold = ('variable,name=dotc_rake_threshold,op=set,value=99\n'
                       'actions.precombat+=/variable,name=dotc_rake_threshold,op=set,'
                       'if=talent.wild_slashes&talent.merciless_claws,value=5\n'
                       'actions.precombat+=/variable,name=dotc_rake_threshold,op=set,'
                       'if=talent.wild_slashes&!talent.merciless_claws,value=8') if v['dotc_fix'] else \
        ('variable,name=dotc_rake_threshold,'
         'value=5-2*(talent.wild_slashes&!talent.infected_wounds)+3*(!talent.wild_slashes&talent.infected_wounds)')
    add('actions.precombat+=/' + dotc_threshold)

    add('actions.aoe_builder=rake,if=dot.rake.refreshable&((talent.doubleclawed_rake&(!talent.lunar_inspiration|!talent.panthers_guile|active_dot.rake<5))|hero_tree.wildstalker&(active_dot.rake<2+!talent.panthers_guile+talent.lunar_inspiration))')
    add('actions.aoe_builder+=/moonfire_cat,if=talent.lunar_inspiration&dot.moonfire.refreshable')
    add('actions.aoe_builder+=/swipe_cat,if=hero_tree.druid_of_the_claw&buff.bs_inc.up|buff.clearcasting.react&spell_targets>2&(hero_tree.druid_of_the_claw|spell_targets<7)')
    add('actions.aoe_builder+=/swipe_cat,if=buff.sudden_ambush.up&spell_targets>=5+(2*hero_tree.wildstalker)')
    add('actions.aoe_builder+=/rake,if=dot.rake.refreshable&(hero_tree.wildstalker|spell_targets<=variable.dotc_rake_threshold)')
    add('actions.aoe_builder+=/rake,if=buff.tigers_fury.up&!variable.rake_tf&spell_targets=2')
    add('actions.aoe_builder+=/shred,if=combo_points<=1&spell_targets=2&talent.panthers_guile')
    add('actions.aoe_builder+=/swipe_cat,if=combo_points>1|spell_targets>2|!talent.panthers_guile')

    return '\n'.join(L) + '\n'


DEFAULTS = dict(no_cds=True, tf_no_hold=False, dotc_fix=False, bite_pool=False,
                sudden_ambush_shred=False, apex_ravage=False, ttd=False)

VARIANTS = {
    'ferraz':        ({}, 'A rotacao atual: sem Berserk/Convoke/trinkets/pocao'),
    'ttd_gates':     (dict(no_cds=False, ttd=True), 'BASE + gates de TTD no burst (Berserk/Convoke/trinkets/pocao)'),
    'fixed_cds':     (dict(no_cds=False), 'Adiciona Berserk, Convoke, racial, trinkets, pocao'),
    'fixed_tf_hold': (dict(no_cds=False, tf_no_hold=True), '+ remove o hold de Tigers Fury (M+ only, sem sentido aqui)'),
    'fixed_all':     (dict(no_cds=False, tf_no_hold=True, dotc_fix=True), 'Todas as 3 correcoes juntas'),
    'dotc_fix_only': (dict(dotc_fix=True), 'So a formula do dotc_rake_threshold corrigida'),
    # --- Wildstalker: em cima da base real (com CDs) --------------------------
    'ws_base':       (dict(no_cds=False), 'BASE Wildstalker = o que o YAML faz hoje'),
    'ws_bite_pool':  (dict(no_cds=False, bite_pool=True),
                      'BASE + Bite com max_energy (ganhou +2.87% na build de raid)'),
    # --- Druid of the Claw: a build de M+ voltou para DotC ------------------
    'dotc_sa_shred': (dict(no_cds=False, sudden_ambush_shred=True),
                      'BASE + Shred no proc de Sudden Ambush (ganhou +2.35% no raid)'),
    'dotc_apex':     (dict(no_cds=False, apex_ravage=True),
                      'BASE + linha de Apex Predators Craving no topo do finisher'),
    'dotc_both':     (dict(no_cds=False, sudden_ambush_shred=True, apex_ravage=True),
                      'BASE + as duas'),
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
        print('FAILED %s\n%s' % (name, (r.stdout or '')[-1500:]))
        return None
    d = json.load(open(js, encoding='utf-8'))
    dps = d['sim']['players'][0]['collected_data']['dps']
    return dps['mean'], dps['mean_std_dev']


def main(argv):
    error = '0.2'
    enemies = 1
    style = 'DungeonSlice'
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
        names = list(VARIANTS)

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
        mean, err = r
        delta = ''
        if ref and n != 'ferraz':
            d = mean - ref[0]
            comb = 2 * (err ** 2 + ref[1] ** 2) ** 0.5
            delta = '%+.2f%%%s' % (100 * d / ref[0], '' if abs(d) > comb else ' ~')
        print('%-16s %10.0f %8.0f %10s  %s' % (n, mean, err, delta, VARIANTS[n][1]))
    print('\n"~" = dentro da margem de erro, nao e diferenca real.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
