"""A/B harness: measure the Ferraz Feral (Raid) rotation against the SimC
default (dreamgrove-sourced) for the raid talent build, on Patchwerk.

The Simia YAML cannot be fed to SimulationCraft, so the damage half of
FerrazFeralRaid.yaml is translated here into a SimC action list.

The raid build differs from the M+ one in ways that matter to the priority:
  * NO Frantic Frenzy  -> the feral_frenzy line is the live one
  * NO Primal Wrath    -> aoe_finisher falls through to Rip/Bite
  * NO Apex Predator's Craving -> that whole opener line is dead
  * NO Rampant Ferocity, NO Double-Clawed Rake, NO Heart of the Wild
  * HAS Ashamane's Guidance -> Convoke may fire OUTSIDE Berserk, which the
    M+ file's Convoke line does not allow. This is what `convoke_ag` prices.
  * HAS Merciless Claws, Panther's Guile, Saber Jaws, Focused Frenzy

Run:
    python sim/ab_test_feral_raid.py
    python sim/ab_test_feral_raid.py ferraz convoke_ag
    python sim/ab_test_feral_raid.py --targets 2
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMC = os.path.join(ROOT, 'sim', 'tools', 'simc-1210.01.fd069a4-win64', 'simc.exe')
PROFILE = os.path.join(ROOT, 'sim', 'Ferraz_feral_raid.simc')
APL_DIR = os.path.join(ROOT, 'sim', 'apl_feral_raid')
OUT_DIR = os.path.join(ROOT, 'sim', 'out_feral_raid')


def a(action, *conds):
    conds = [c for c in conds if c]
    return action + (',if=' + '&'.join('(%s)' % c if '|' in c else c for c in conds) if conds else '')


def build(v):
    L = []
    add = L.append

    add('actions.precombat=snapshot_stats')
    add('actions.precombat+=/cat_form,if=buff.cat_form.down')
    add('actions.precombat+=/prowl')
    # rake_tf/rip_tf read debuff.X.visual_id in the YAML — Simia-only, pinned here.
    add('actions.precombat+=/variable,name=rake_tf,value=0')
    add('actions.precombat+=/variable,name=rip_tf,value=%d' % (1 if v['rip_tf_true'] else 0))
    add('actions.precombat+=/variable,name=moonfire_tf,value=%d' % (1 if v['rip_tf_true'] else 0))
    add('actions.precombat+=/variable,name=dotc_rake_threshold,op=set,value=99')
    add('actions.precombat+=/variable,name=dotc_rake_threshold,op=set,'
        'if=talent.wild_slashes&talent.merciless_claws,value=5')
    add('actions.precombat+=/variable,name=dotc_rake_threshold,op=set,'
        'if=talent.wild_slashes&!talent.merciless_claws,value=8')

    add('actions=prowl,if=buff.bs_inc.down&!buff.prowl.up&!buff.shadowmeld.up')
    add('actions+=/cat_form,if=!buff.cat_form.up')
    add('actions+=/auto_attack,if=!buff.prowl.up&!buff.shadowmeld.up')
    add('actions+=/tigers_fury,use_off_gcd=1,if=(cooldown.bs_inc.remains<=1'
        '|cooldown.bs_inc.remains>10|variable.holdBerserk)')
    add('actions+=/rake,if=buff.prowl.up|buff.shadowmeld.up')
    add('actions+=/chomp,if=buff.chomp_enabler.up')
    add('actions+=/call_action_list,name=cd_variable,'
        'if=!cooldown.bs_inc.remains|!cooldown.convoke_the_spirits.remains')
    add('actions+=/call_action_list,name=cooldown')
    add('actions+=/ferocious_bite,if=buff.apex_predators_craving.up')
    add('actions+=/call_action_list,name=finisher,if=spell_targets=1')
    add('actions+=/call_action_list,name=aoe_finisher,if=spell_targets>=2')
    add('actions+=/call_action_list,name=builder,if=spell_targets=1&combo_points<=4')
    add('actions+=/call_action_list,name=aoe_builder,if=spell_targets>1&combo_points<=4')

    add('actions.cd_variable=variable,name=convokeCountRemaining,'
        'value=floor(cooldown.convoke_the_spirits.charges_fractional'
        '+fight_remains%cooldown.convoke_the_spirits.duration-0.05)')
    add('actions.cd_variable+=/variable,name=zerkCountRemaining,'
        'value=floor(cooldown.bs_inc.charges_fractional+fight_remains%cooldown.bs_inc.duration-0.05)')
    add('actions.cd_variable+=/variable,name=holdBerserk,'
        'value=(variable.zerkCountRemaining=1&variable.convokeCountRemaining=1'
        '&cooldown.convoke_the_spirits.remains>10)'
        '|(cooldown.convoke_the_spirits.remains>20'
        '&variable.convokeCountRemaining=variable.zerkCountRemaining)')

    # --- cooldown ---
    cd = ['call_action_list,name=cd_variable,'
          'if=!cooldown.bs_inc.remains|!cooldown.convoke_the_spirits.remains']
    if v['cds']:
        cd += [a('use_items'), a('berserking'),
               a('potion', 'buff.bs_inc.up|fight_remains<32'),
               a('berserk', 'buff.tigers_fury.up&!variable.holdBerserk')]
    cd += [a('feral_frenzy', '!talent.frantic_frenzy&combo_points<=2+(2*buff.bs_inc.up)'),
           a('frantic_frenzy', 'buff.tigers_fury.up|combo_points<=2+(2*buff.bs_inc.up)')]
    if v['cds']:
        # The M+ file gates Convoke on being inside Berserk. With Ashamane's
        # Guidance (raid-only here) the real APL also allows it outside, when
        # Berserk is far away — that is what `convoke_ag` turns on.
        conv_window = ('buff.bs_inc.up|talent.ashamanes_guidance'
                       '&(cooldown.bs_inc.remains>45|variable.holdBerserk)') \
            if v['convoke_ag'] else 'buff.bs_inc.up'
        cd.append(a('convoke_the_spirits',
                    '(%s)&buff.tigers_fury.up&(prev_gcd.1.rip|prev_gcd.1.ferocious_bite'
                    '|prev_gcd.1.primal_wrath'
                    '|buff.tigers_fury.remains<=1+action.convoke_the_spirits.execute_time)'
                    '|fight_remains<5' % conv_window))
    for i, ln in enumerate(cd):
        add('actions.cooldown%s%s' % ('=' if i == 0 else '+=/', ln))

    # --- finisher (single target: the raid case that matters) ---
    # Rip condition: the M+ file carries two extra Tiger's Fury re-snapshot
    # clauses on top of plain `refreshable`. `simple_rip` prices dropping them.
    if v['simple_rip']:
        add('actions.finisher=rip,if=combo_points>=5&dot.rip.refreshable'
            '&(buff.tigers_fury.up|dot.rip.remains<cooldown.tigers_fury.remains)')
    else:
        add('actions.finisher=rip,if=combo_points>=5&(dot.rip.refreshable'
            '&(buff.tigers_fury.up|dot.rip.remains<cooldown.tigers_fury.remains)'
            '|buff.tigers_fury.up&!variable.rip_tf&dot.rip.ticking'
            '|buff.tigers_fury.up&buff.tigers_fury.remains<2&dot.rip.ticking)')
    # Bite: max_energy=1 makes it wait for the full 50-energy cost, which is
    # what doubles its damage. Saber Jaws (raid-only) raises the payoff.
    if v['bite_max_energy']:
        add('actions.finisher+=/pool_resource,for_next=1')
        add('actions.finisher+=/ferocious_bite,max_energy=1,if=combo_points>=5')
    else:
        add('actions.finisher+=/pool_resource,for_next=1,if=energy<50')
        add('actions.finisher+=/ferocious_bite,if=combo_points>=5')

    add('actions.aoe_finisher=primal_wrath,if=combo_points>=5&spell_targets>1'
        '&(dot.rip.remains<6.5&!buff.bs_inc.up|dot.rip.refreshable)')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5&!talent.primal_wrath'
        '&spell_targets>=2+(3*!talent.rampant_ferocity)')
    add('actions.aoe_finisher+=/rip,if=combo_points>=5&!talent.primal_wrath'
        '&(!dot.rip.ticking|dot.rip.refreshable&(buff.tigers_fury.up|!variable.rip_tf))')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5&(talent.rampant_ferocity'
        '|buff.ravage.up&spell_targets<8|dot.bloodseeker_vines.ticking&spell_targets<5)')
    add('actions.aoe_finisher+=/primal_wrath,if=combo_points>=5')
    add('actions.aoe_finisher+=/ferocious_bite,if=combo_points>=5')

    # --- builder ---
    add('actions.builder=prowl,if=!buff.shadowmeld.up&(!variable.rake_tf|dot.rake.refreshable)')
    if v['sudden_ambush_shred']:
        # dreamgrove keeps a Druid-of-the-Claw-only Shred on Sudden Ambush.
        add('actions.builder+=/shred,if=buff.sudden_ambush.up&hero_tree.druid_of_the_claw')
    add('actions.builder+=/rake,if=(buff.tigers_fury.up'
        '|dot.rake.remains<cooldown.tigers_fury.remains)'
        '&(dot.rake.refreshable&(buff.tigers_fury.up|!variable.rake_tf)'
        '|dot.rake.remains<2|buff.tigers_fury.up&!variable.rake_tf)')
    # Lunar Inspiration. The YAML carries a Tiger's Fury re-snapshot version
    # AHEAD of the plain refreshable one (FerrazFeralRaid.yaml:213 and :218);
    # the harness only ever had the plain one. LI is untalented on the Druid
    # of the Claw build, so it never mattered until the raid build moved to
    # Wildstalker. `li_full` prices the YAML's real pair.
    if v['li_full']:
        add('actions.builder+=/moonfire_cat,if=talent.lunar_inspiration'
            '&(buff.tigers_fury.up|dot.moonfire.remains<cooldown.tigers_fury.remains)'
            '&(dot.moonfire.refreshable&(buff.tigers_fury.up|!variable.moonfire_tf)'
            '|dot.moonfire.remains<2|buff.tigers_fury.up&!variable.moonfire_tf)')
    add('actions.builder+=/moonfire_cat,if=talent.lunar_inspiration&dot.moonfire.refreshable')
    add('actions.builder+=/shred')

    # --- aoe_builder ---
    add('actions.aoe_builder=rake,if=dot.rake.refreshable&((talent.doubleclawed_rake'
        '&(!talent.lunar_inspiration|!talent.panthers_guile|active_dot.rake<5))'
        '|hero_tree.wildstalker&(active_dot.rake<2+!talent.panthers_guile'
        '+talent.lunar_inspiration))')
    add('actions.aoe_builder+=/moonfire_cat,if=talent.lunar_inspiration&dot.moonfire.refreshable')
    add('actions.aoe_builder+=/swipe_cat,if=hero_tree.druid_of_the_claw&buff.bs_inc.up'
        '|buff.clearcasting.react&spell_targets>2'
        '&(hero_tree.druid_of_the_claw|spell_targets<7)')
    add('actions.aoe_builder+=/swipe_cat,if=buff.sudden_ambush.up'
        '&spell_targets>=5+(2*hero_tree.wildstalker)')
    add('actions.aoe_builder+=/rake,if=dot.rake.refreshable'
        '&(hero_tree.wildstalker|spell_targets<=variable.dotc_rake_threshold)')
    add('actions.aoe_builder+=/rake,if=buff.tigers_fury.up&!variable.rake_tf&spell_targets=2')
    add('actions.aoe_builder+=/shred,if=combo_points<=1&spell_targets=2&talent.panthers_guile')
    add('actions.aoe_builder+=/swipe_cat,if=combo_points>1|spell_targets>2'
        '|!talent.panthers_guile')

    return '\n'.join(L) + '\n'


DEFAULTS = dict(cds=True, convoke_ag=False, bite_max_energy=False,
                sudden_ambush_shred=False, simple_rip=False, rip_tf_true=False,
                li_full=False)

VARIANTS = {
    'ferraz':        ({}, 'Porte direto da rotacao de M+ para a build de raid'),
    'no_cds':        (dict(cds=False), 'Controle: sem Berserk/Convoke/trinkets/pocao'),
    'convoke_ag':    (dict(convoke_ag=True),
                      'Convoke tambem FORA do Berserk (Ashamane\'s Guidance)'),
    'bite_pool':     (dict(bite_max_energy=True),
                      'SO o Bite com max_energy (pooling ate 50 de energia)'),
    'simple_rip':    (dict(simple_rip=True),
                      'SO simplificar a condicao do Rip (tira re-snapshot de TF)'),
    'riptf_base':    (dict(rip_tf_true=True),
                      'CONTROLE: rotacao atual com rip_tf=1 (como fica no jogo)'),
    'riptf_simple':  (dict(rip_tf_true=True, simple_rip=True),
                      'CONTROLE: simple_rip com rip_tf=1'),
    # --- medidos contra a baseline correta (rip_tf=1) ------------------------
    'rt_convoke_ag': (dict(rip_tf_true=True, convoke_ag=True),
                      "BASE + Convoke fora do Berserk (Ashamane Guidance)"),
    'rt_bite_pool':  (dict(rip_tf_true=True, bite_max_energy=True),
                      'BASE + Bite com max_energy'),
    'rt_sa_shred':   (dict(rip_tf_true=True, sudden_ambush_shred=True),
                      'BASE + Shred em Sudden Ambush'),
    'rt_all':        (dict(rip_tf_true=True, convoke_ag=True, bite_max_energy=True,
                           sudden_ambush_shred=True), 'BASE + as tres juntas'),
    'rt_li_full':    (dict(rip_tf_true=True, li_full=True),
                      'BASE + a linha completa de Lunar Inspiration do YAML'),
    'rt_no_cds':     (dict(rip_tf_true=True, cds=False),
                      'CONTROLE: BASE sem Berserk/Convoke/trinkets/pocao'),
    'rip_and_pool':  (dict(simple_rip=True, bite_max_energy=True),
                      'simple_rip + bite_pool'),
    'sa_shred':      (dict(sudden_ambush_shred=True),
                      'Shred em Sudden Ambush (linha DotC do dreamgrove)'),
    'ag_pool':       (dict(convoke_ag=True, bite_max_energy=True),
                      'convoke_ag + bite_pool'),
    'all':           (dict(convoke_ag=True, bite_max_energy=True, sudden_ambush_shred=True),
                      'convoke_ag + bite_pool + sa_shred'),
    'all_plus_rip':  (dict(convoke_ag=True, bite_max_energy=True, sudden_ambush_shred=True,
                           simple_rip=True), 'Todas as quatro juntas'),
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
    error, enemies, style, names = '0.15', 1, 'Patchwerk', []
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
        sys.stdout.write('running %-14s ... ' % n)
        sys.stdout.flush()
        r = run(n, error, enemies, style)
        results[n] = r
        print('%.0f DPS' % r[0] if r else 'failed')

    ref = results.get('ferraz')
    print('\n%-14s %10s %7s %11s  %s' % ('variant', 'DPS', '+/-', 'vs ferraz', 'what'))
    print('-' * 88)
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
        print('%-14s %10.0f %7.0f %11s  %s' % (n, mean, err, delta, VARIANTS[n][1]))
    print('\n"~" = dentro da margem de erro, nao e diferenca real.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
