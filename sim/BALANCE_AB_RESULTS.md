# FerrazBalance vs SimulationCraft — resultados

Perfil: `sim/Ferraz_balance.simc` (gear/consumíveis do perfil MID1 Balance do SimC,
ilvl ~289, com a talent string informada). Harness: `sim/ab_test_balance.py`.
SimC 1210.01, `target_error=0.12–0.15`.

**Estilo de luta de referência: `DungeonSlice`** (M+). Patchwerk 1 alvo e 5 alvos
aparecem só como controle — várias mudanças que ganham em Patchwerk **perdem** em
DungeonSlice, então nenhuma decisão foi tomada pelo número de Patchwerk.

Talentos da string (Elune's Chosen): Boundless Moonlight, Lunar Calling, Lunation,
Atmospheric Exposure, The Eternal Moon, Incarnation: Chosen of Elune, Whirling Stars,
Fury of Elune, Touch the Cosmos, Umbral Embrace, Rattle the Stars, Meteorites,
Aetherial Kindling, Stellar Amplification, Sundered Firmament, Radiant Moonlight.
**Sem Starweaver, sem Force of Nature, sem Convoke, sem New Moon/Wild Mushroom.**

## Resultado

DungeonSlice, `target_error=0.12`:

| variante | DPS | vs atual |
|---|---|---|
| ferraz (antes) | 111.4k | — |
| **ferraz_v2 (aplicado)** | **112.3k** | **+0.77%** |
| ferraz_v2 + DoTs espalhados | 114.5k | +2.74% |
| APL padrão do SimC | 120.2k | +7.92% |
| trinkets/poção desligados (default antigo do YAML) | 103.2k | -7.36% |

## O que foi aplicado no YAML

1. **Gasto de AP amarrado ao Eclipse** (`ec_st` e `aoe`). Rattle the Stars só desconta
   o gastador enquanto um Eclipse está ativo, então o piso de AP acompanha o Eclipse:
   `astral_power>=50` (Starsurge) / `>=40` (Starfall) dentro do Eclipse, e
   `astral_power.deficit<20` fora dele, no lugar do piso fixo `>60` / `>50`.
   **+0.79% em DungeonSlice**, +0.16% em 5 alvos.
2. **Trinkets e poção ligados por padrão** (`use_trinket_1/2`, `use_potion`).
   Desligados custavam **-7.4%**. O gate do YAML (burst + Fury of Elune em CD) é ~0.2%
   melhor que usar sem checar o Fury of Elune.
3. **Lista `mouseover_dots`** chamada no `aoe`: sugere Moonfire/Sunfire no mouseover
   enquanto houver inimigo perto do alvo sem o DoT. É a versão viável de espalhar DoT —
   o Simia não cicla alvo inimigo (`target_enemy` troca de alvo de verdade, inaceitável
   em M+) e não expõe debuff do mouseover, então o gate é `cluster.debuff.X.count <
   enemies.around_target` com trava de 1.5s por feitiço. Teto medido: **+2.1 a +2.7%**.

## O que foi testado e NÃO aplicado

Ganha em Patchwerk, perde em M+:

| variante | DungeonSlice | Patchwerk 1t |
|---|---|---|
| tirar o Wrath filler do `ec_st` | **-1.44%** | +0.55% |
| Touch the Cosmos em Starfall no ST | -0.20% ~ | +0.53% |
| as duas juntas (`patchwerk_only`) | **-0.65%** | +2.6% |

O Wrath filler foi re-testado em cima do `ferraz_v2` e continua valendo 1.4% em
DungeonSlice. Ficou.

Perde em todo lugar (o desenho atual já estava certo):

| variante | DungeonSlice |
|---|---|
| `cds_first` (Eclipse/Inc/FoE na frente dos DoTs) | -3.60% |
| `aoe_at_3` (limiar de AoE em 3 alvos) | -1.48% |
| `inc_asap` (Incarnation sem esperar Fury of Elune) | -0.47% |
| `ecl_over_inc` (Eclipse mesmo com Incarnation pronto) | -0.33% |
| `sf_ap_60` | -0.31% |
| `trinkets_simc` (trinket sem checar Fury of Elune) | -0.23% |
| `asc_fires`, `ecl_timings`, `foe_off_cd`, `ss_ap_50`, `sf_ap_40` | dentro do erro |

Confirmações do desenho: alinhar Incarnation com Fury of Elune, segurar o Eclipse
quando o Incarnation está pronto, DoTs antes dos cooldowns e limiar de AoE em 2 alvos
são todos a escolha certa — cada alternativa perde DPS.

## Thorn Bloom (racial Harronir)

O perfil declara `night_elf` (é o do MID1, mantido para o número continuar comparável
com o APL padrão). Para medir a racial, rode com `--race harronir`.

DungeonSlice, sobre o `ferraz_v2`:

| posicionamento | delta |
|---|---|
| puro no CD | +0.02% ~ |
| só com 2+ alvos | -0.15% ~ |
| só dentro do burst | -0.21% ~ |
| burst ou 3+ alvos | -0.41% |

Em 5 alvos (Patchwerk) fica em **-0.24%**. O dano dela é 391 pDPS, ou **0.13%** do
total, e o GCD de 0.5s custa mais que isso. **Não é botão de dano.**

O que ela é: cura. Os coeficientes são 0.65×SP direto + 0.15×SP/s por 12s para até 8
aliados, contra 0.5×SP + 0.125×SP/s de dano — ~5x mais cura que dano. A poça cai na
**área do alvo** (10y), então alcança quem está em cima do pack: tank e melee.

Aplicado como cura no `heal_support`, no mesmo formato do FerrazRestoDruid
(`group.count(cycle.health.effective.pct<X)>=N`), com gate de alvo válido porque a poça
precisa de um alvo para cair em cima. Sem `target.in_melee` — o Resto usa isso porque
se cura junto; o Moonkin está a 40y e nunca passaria nesse gate.

## O que sobra de gap (~7.9% vs APL padrão)

Comparando o breakdown em DungeonSlice (`ferraz_v2_md` vs padrão), a diferença está em
Moonfire (9.7k vs 11.0k com o **mesmo** número de casts — o padrão espalha melhor,
inclusive fora do alcance do mouseover) e em Starfire (69 vs 82 casts — o padrão
desperdiça menos GCD). O resto do APL padrão que não dá para copiar são as listas
`opener`/`cooldowns`/`mini` dele, que dependem de `variable` com estado.

## Como rodar

```bash
python sim/ab_test_balance.py --error 0.15 --style DungeonSlice
```

Sem argumentos roda todas as variantes; `--targets N` muda o número de alvos;
`--race harronir` troca a raça do perfil (necessário para as variantes `tb_*`);
`ferraz ferraz_v2 simc_default` roda só as citadas.
