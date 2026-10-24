# FerrazBalanceRaid vs SimulationCraft — resultados

Perfil: `sim/Ferraz_balance_raid.simc` (gear/consumíveis do MID1 Balance, ilvl ~289,
com a talent string de raid). Harness: `sim/ab_test_balance_raid.py`. SimC 1210.01,
`target_error=0.12`. **Estilo de referência: Patchwerk** — é raid, não M+.

## O achado principal

A talent string **não é Keeper of the Grove**, apesar do nome do arquivo. É
**Elune's Chosen com Lunar Calling**, e não carrega Force of Nature, Wild Mushroom,
New/Half/Full Moon nem Starweaver. Carrega Power of Goldrinn, Nature's Balance,
Sundered Firmament, Denizen of the Dream, Rattle the Stars, Touch the Cosmos.

A rotação estava escrita para o build de Grove. O filler era a parte cara disso.

## Resultado

1 alvo, Patchwerk:

| variante | DPS | vs atual |
|---|---|---|
| rotação como estava | 111.9k | — |
| **com as mudanças aplicadas** | **124.3k** | **+11.06%** |
| APL padrão do SimC | 128.4k | +14.8% |

3 alvos: 194.0k → 193.8k, dentro do erro. Nada regrediu.

## O que foi aplicado

| mudança | 1 alvo |
|---|---|
| **Filler Starfire em vez de Wrath** | **+11.06%** |
| Piso de AP amarrado ao Eclipse (Rattle the Stars) | +1.28% |
| `solar_eclipse` → `lunar_eclipse` | não medível |

O filler é quase tudo. As duas linhas de filler terminavam em Wrath com Starfire
como caso especial — a forma de Grove. Em Lunar Calling é o contrário, e tirar o
Wrath por completo do `st` vale 11%.

**Atenção**: o arquivo de M+ mantém a linha de Wrath, onde ela vale +1.44%. Estilos
de luta diferentes, respostas opostas. Não copiar linhas entre os dois arquivos.

O `solar_eclipse` virou `lunar_eclipse` por coerência de build — o SimC modela Eclipse
como um feitiço só, então não dá para medir. É correção de build, não de número.

## Poção — o arquivo não tinha nenhuma

O `trinkets` só tinha trinket 1 e 2. Não existia linha de poção. Medido em cima da
rotação já corrigida:

| variante | 1 alvo |
|---|---|
| sem poção (como estava) | 117.6k |
| poção dentro do burst | 124.3k (**+5.67%**) |
| poção no burst **ou** com a luta acabando | 124.9k (**+6.17%**) |

Aplicada a segunda: numa luta de 300s cabem duas poções se a primeira sair cedo, e a
cláusula `fight_remains<=30` pega a segunda de graça.

AVISO sobre os números da seção anterior: o harness emitia poção nos dois lados, então
os DPS absolutos ali estavam otimistas. Os deltas continuam válidos — os dois braços
tinham poção — mas o baseline real da rotação antiga era mais baixo.

## Sliders de Time To Die — não fazem sentido aqui

O arquivo de M+ tem cinco. Cada variável TTD lá começa com `target.boss|...`, então em
boss elas são sempre verdadeiras e não gatilham nada. Existem para trash de dungeon,
que morre antes de um cooldown de 3 minutos pagar. Em raid o alvo é boss quase sempre,
e os cortes que importam já estão inline (`fight_remains<20` no Incarnation e no Fury
of Elune). Não foram portados de propósito.

## O que foi testado e não mudou nada

| variante | 1 alvo |
|---|---|
| remover as linhas mortas de Grove (FoN/Mushroom/Moons) | +0.01% ~ |
| Incarnation alinhado com Fury of Elune | +0.14% ~ |
| Incarnation sem esperar Ascendant Stars cair | -0.04% ~ |
| refrescar DoT no pandemic dentro do Eclipse | **-0.94%** |
| remover as listas de opener | **-1.6%** |

As linhas mortas de Grove ficaram no arquivo, sinalizadas inline, do mesmo jeito que
o arquivo de M+ mantém as de Starweaver: custam nada e o arquivo continua correto se
o build voltar.

Confirmações do desenho: a cláusula `&var.eclipse_down` no refresh de DoT está certa
(refrescar dentro do Eclipse joga fora o snapshot), o gate de Ascendant Stars no
Incarnation está certo, e as listas de opener valem 1.6% — elas rodam antes de **todo**
burst, não só no pull.

## O que sobra (~3.7% vs APL padrão)

Starfire: 60 casts contra 88 do APL padrão. O padrão desperdiça menos GCD, com listas
`opener`/`cooldowns`/`mini` que dependem de `variable` com estado.

## Como rodar

```bash
python sim/ab_test_balance_raid.py --error 0.12
```


## Build com Starweaver (2026-10-24)

SimC `1210.01.73a372b` (atualizado nesta data; o antigo `7bc1071` estava 13 commits atrás, com
APL de Balance trocada e dados 70529). Perfil `sim/Ferraz_balance_raid_sw.simc`
(talentos: Starweaver, Meteorites, Meteor Storm, Radiant Moonlight, Lunation; mesma hero
Elune's Chosen). Rodar com `BAL_BUILD=sw python sim/ab_test_balance_raid.py --error 0.12 ...`.
Patchwerk, target_error=0.12. `nb_base` = o arquivo v10 como estava, sem Starweaver.

| variante | 1 alvo | 3 alvos |
|---|---|---|
| nb_base (v10) | 110186 | 197160 |
| nb_sw (Warp->Starfall, Weft->Starsurge) | **+4.49%** | **+5.49%** |
| nb_sw_tc (+ Touch the Cosmos para Starfall em ST) | +4.67% | +5.42% |
| nb_sw_foe (+ Fury of Elune solto em AoE) | +4.48% | +5.49% |
| APL padrao do SimC | +17.11% | +20.46% |

Aplicado na v11: so `nb_sw`. Touch the Cosmos para Starfall em alvo unico rende +0.18% (no limite
do erro) e nada em 3 alvos, entao a decisao da v9 (Starsurge) fica. Fury de Elune solto em AoE nao
mexe nada no modelo. Os pisos de AP (50) nao foram re-medidos separadamente.

**Folga restante: 12-14% contra o APL padrao nesta build** (era 3.7% na build antiga). A diferenca
nao foi decomposta; candidatos: Eclipse/Fury timings (`variable` com estado), Meteorites com Starfall
em alvo unico, lista `mini`, e o piso de AP agora sem Rattle the Stars.


## Rodada 2 (2026-10-24): harness fiel ao v11 e build antiga x nova

Harness corrigido: o Fury of Elune em alvo unico nao tem gate no arquivo (o harness aplicava um gate
antigo) e a pocao ja esta no arquivo (burst/fim da luta). Com isso a folga contra o APL padrao cai de
12-14% para ~3.5% (1 alvo) e ~7% (3 alvos), igual a da build antiga (3.9% / 7.2%): o "12-14%" da
primeira rodada era artefato do harness.

Mesmo SimC (73a372b), mesmo equipamento, target_error=0.12:

| alvos | build antiga + v10 (`r2_old`) | build nova + v11 (`r2_ss40`) | |
|---|---|---|---|
| 1 | 127310 | 124976 | antiga +1.8% |
| 2 | 155608 | 180379 | nova +15.9% |
| 3 | 196594 | 220612 | nova +12.2% |

Fica a build nova (ganha com >=2 alvos; empata a media se so ~10% da luta tem add). A string antiga
fica no guia para luta de alvo unico puro.

Ajustes da rodada (build nova, 1 alvo / 3 alvos): piso de AP do Starsurge em Eclipse 40: +0.41% / neutro
(aplicado; 30 da +0.49% mas e o mesmo que 40 porque o custo do feitico ja trava); Starsurge sempre que nao
for gratis: +0.15% ~; Touch the Cosmos para Starfall em ST: +0.25% / -0.08% (nao aplicado); Starfall AoE a
partir de 45 AP: neutro. Moonfire em 3 alvos: o APL padrao lanca 24.9 contra 14.3 porque cicla alvos,
coisa que o Simia nao faz (so por mouseover); nao e corrigivel na rotacao.
