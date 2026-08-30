# Simia Rotation — Documentação Completa
> **Fonte:** https://auth.simia.pro/rotation/ · **Site:** v2.0.0 · **Catálogo:** 1.0.0 (2026-08-10) · **Sincronizado em:** 2026-08-30 (dump de 112 arquivos)

---

## Índice
1. [Guia Passo-a-Passo](#1-guia-passo-a-passo)
2. [Sintaxe de Ação & Alvos](#2-sintaxe-de-ação--alvos)
3. [Modificadores de Step](#3-modificadores-de-step)
4. [Estrutura Geral do Arquivo YAML](#4-estrutura-geral-do-arquivo-yaml)
5. [Config Widgets (UI)](#5-config-widgets-ui)
6. [Variáveis & Spell Overrides](#6-variáveis--spell-overrides)
7. [Padrões Comuns, Receitas & Exemplos](#7-padrões-comuns-receitas--exemplos)
8. [Operadores SimC](#8-operadores-simc)
9. [Ações Virtuais](#9-ações-virtuais)
10. [Erros Conhecidos & Boas Práticas](#10-erros-conhecidos--boas-práticas)
11. [Catálogo de Referência de Expressões (634)](#11-catálogo-de-referência-de-expressões)
12. [Expressões Não Catalogadas](#12-expressões-não-catalogadas)

---

## 1. Guia Passo-a-Passo

Este guia passo-a-passo guiará você desde um arquivo vazio até uma rotação funcional. Vamos construir uma rotação simples para Arms Warrior.

### Passo 1: Criar o Arquivo
Crie um novo arquivo chamado `my_warrior.yaml` na sua subpasta `custom/` no diretório do aplicativo:
`app_directory/custom/my_warrior.yaml`

Comece com o mínimo necessário — o ID da especialização (spec ID) e as três listas compartilhadas obrigatórias:

```yaml
spec: 71

lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=auto_target
```

> [!IMPORTANT]
> **O que são essas três linhas?** Toda rotação deve começar com elas. `spell_queue` gerencia feitiços na fila manual, `sanity_checks` faz verificações de estado (se está vivo, não montado, etc.), e `auto_target` seleciona alvos automaticamente. Sem elas, a rotação não funcionará corretamente.
>
> [!WARNING]
> **`sanity_checks` NÃO é só verificação de estado.** Além dos cinco `return` de guarda
> (`!state.rotation`, `player.dead`, `state.blocked_inputs`, `mounted`, `travel_form`), ele
> chama por dentro: `special_actions`, `anti_cc`, `auto_freedom`, `auto_feign_death`,
> `auto_death_grip`, **`auto_dispel`**, `affix`, **`auto_purge_enrage`**, `auto_brez`,
> `auto_rez` e **`auto_combat_potion`** — ver `simia_data_dump/_shared.yaml`.
>
> Duas consequências práticas:
>
> 1. **A sua rotação já dispela e já usa poção** mesmo sem nenhuma linha sua para isso, e
>    não há como desligar peça por peça.
> 2. **Se o seu arquivo tem linha própria de `combat_potion`**, ela concorre com o
>    `auto_combat_potion` herdado: dois motoristas para a mesma poção.
>
> Para ter controle, inline o conteúdo que interessa no seu próprio arquivo e pare de
> chamar `sanity_checks` — mas **copie os cinco `return` ao pé da letra**, ou a rotação
> passa a disparar morto ou montado.

### Passo 2: Adicionar o Primeiro Feitiço
Abaixo das três listas compartilhadas, adicione um feitiço de preenchimento (filler):

```yaml
lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=auto_target
    - slam
```

Salve o arquivo. O sistema faz hot-reload automaticamente — abra o seletor de rotação no aplicativo e sua rotação deverá aparecer sob a spec Arms Warrior. O Simia verifica automaticamente se o feitiço está fora de cooldown, se você tem recursos suficientes e se o alvo está no alcance.

### Passo 3: Adicionar Prioridade
Insira `mortal_strike` **acima** de `slam`:

```yaml
    - call_action_list,name=auto_target
    - mortal_strike
    - slam
```

**A ordem importa.** O sistema avalia os feitiços de cima para baixo e escolhe o **primeiro** que passar em todas as verificações. Como `mortal_strike` está acima de `slam`, ele tem prioridade. Quando estiver em cooldown, a rotação cai para `slam`.

### Passo 4: Adicionar Condição (`if=`)
Adicione `overpower` entre `mortal_strike` e `slam`, mas apenas quando os acúmulos (stacks) forem baixos:

```yaml
    - mortal_strike
    - overpower,if=buff.overpower.stack<2
    - slam
```

A parte `if=` é a **condição**. Aqui, `buff.overpower.stack` retorna a quantidade atual de stacks, e `<2` significa "menor que 2". O feitiço só será sugerido se essa expressão for verdadeira.

### Passo 5: Adicionar Interrupt
Adicione uma linha de interrupção antes dos feitiços de dano:

```yaml
    - call_action_list,name=auto_target
    - pummel,interrupt=true,if=target.incoming_cast.kickable.ready
    - mortal_strike
```

`interrupt=true` permite interromper o próprio cast atual. `target.incoming_cast.kickable.ready` verifica se o alvo está castando algo interrompível e se seu interrupt está pronto.

### Passo 6: Organizar com Sub-Listas
À medida que a rotação cresce, organize-a em listas nomeadas:

```yaml
lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=auto_target
    - call_action_list,name=interrupts
    - call_action_list,name=defensives
    - call_action_list,name=single_target

  interrupts:
    - pummel,interrupt=true,if=target.incoming_cast.kickable.ready

  defensives:
    - victory_rush,if=buff.victorious.up&health.pct<70
    - shield_wall.player,range_check=none,if=health.pct<30

  single_target:
    - mortal_strike
    - overpower,if=buff.overpower.stack<2
    - slam
```

Observe `shield_wall.player` — o sufixo `.player` indica cast em si mesmo. E `range_check=none` pula a verificação de alcance.

### Passo 7: Metadata e Ajustes Finais
Adicione metadados para identificar a rotação no seletor:

```yaml
spec: 71
name: "My Arms Warrior"
author: "YourName"
version: "1.0.0"
description: "Rotação básica de Arms Warrior"
```

### 1.1 Carregando Rotações

O sistema procura por arquivos de rotação em uma ordem específica. Entender isso ajuda a saber onde colocar seus arquivos e como a seleção funciona.

#### Prioridade de Carregamento (do mais alto para o mais baixo)
1. **Rotação da comunidade selecionada** — Obtida de uma URL através do navegador de rotações da comunidade.
2. **Rotação customizada selecionada** — Um arquivo YAML local que você selecionou na interface (UI).
3. **Rotação local padrão** — `rotation_SPECID.yaml` no diretório do aplicativo.
4. **Fallback web** — Obtida do servidor caso não exista arquivo local.

#### Onde Colocar Rotações Customizadas
Coloque seus arquivos YAML em qualquer um destes locais (ambos são escaneados):
```yaml
# Preferido: subpasta custom/ (tem prioridade, mantém as coisas organizadas)
app_directory/custom/minha_rotacao_arms.yaml

# Também funciona: diretório principal do app
app_directory/minha_rotacao_arms.yaml
```

> [!TIP]
> Use a subpasta `custom/` para manter suas rotações pessoais separadas dos arquivos padrão do app. Arquivos em `custom/` têm prioridade sobre arquivos no diretório principal.

#### Nomenclatura de Arquivos
- Rotações customizadas podem ter **qualquer nome** terminando em `.yaml` (ex: `meu_mago_frost.yaml`, `arms_raid.yaml`).
- O arquivo deve ter um campo `spec:` válido em seus metadados — é assim que o sistema sabe a qual especialização ele pertence.
- Rotações padrão usam a convenção de nomenclatura `rotation_SPECID.yaml` (ex: `rotation_71.yaml` para Arms Warrior).
- Arquivos que começam com `_` (underscore) são considerados dados compartilhados (shared) e não aparecem na lista de rotações.

---

## 2. Sintaxe de Ação & Alvos

Formato básico de uma linha de ação:
`spell_name[.cast_target],modifier=value,...,if=condition`

### Sufixos de Alvo (Cast Targets)
| Sufixo | Descrição | Exemplo |
|---|---|---|
| `.player` | Lança o feitiço em si mesmo (@player) | `shield_wall.player` |
| `.cursor` | Lança na posição do cursor do mouse (ground AoE) | `blizzard.cursor` |
| `.focus` | Lança no alvo de foco (focus target) | `wind_shear.focus` |
| `.mouseover` | Lança no alvo sob o mouse (mouseover) | `rejuvenation.mouseover` |

### Comandos Especiais de Lista
| Ação / Comando | Descrição |
|---|---|
| `call_action_list,name=LIST` | Executa a sub-lista e, se nada for sugerido, continua a lista atual. |
| `run_action_list,name=LIST` | Executa a sub-lista e, se algo for sugerido, reinicia a rotação do topo da `main`. |
| `return` | Interrompe a execução da lista atual (geralmente usado com `if=`). |

---

## 3. Modificadores de Step

Modificadores controlam como um feitiço é avaliado e lançado. Eles vêm separados por vírgula logo após o nome do feitiço.

### Grupo: Targeting (Direcionamento)
- `range_check=`: Define a unidade testada para alcance (padrão: `target`). Use `none` para self-buffs (evita erros). Ex: `range_check=focus` ou `range_check=mob_count_8y`.
- `cycle=`: Itera sobre o grupo e escolhe o membro com menor HP que atenda à condição. Valores: `members`, `tanks`, `healers`, `dps`, `party`, `config.NAME`.
- `cycle_order=`: Altera a ordenação da iteração do cycle. Padrão é `health` — ordena por **HP bruto crescente**, então membros de vida máxima baixa vêm primeiro (triagem para dano fixo): um pano de 200k passa na frente de um tank de 600k com o mesmo HP%. Outros: `health.pct` (ordem por HP% crescente), `player_first` (jogador primeiro), `buff.SPELL.remains` (menor duração restante do buff), `buff.SPELL.remains.any`, `debuff.SPELL.remains`, `debuff.SPELL.remains.any`.
- `target=`: Alvo pré-calculado direto (mais rápido que cycle). Valores: `lowest`, `tanks.lowest`, `healers.lowest`, `dps.lowest`, `missing.SPELL.lowest`.

### Grupo: Timing (Tempo)
- `delay=` (ms): Atraso mínimo entre as pressões deste feitiço específico.
- `global_delay=` (ms): Bloqueia TODOS os feitiços por N ms após pressionar (útil para registrar canalizações).
- `after=` (ms): Aguarda N ms após a condição `if=` se tornar verdadeira antes de executar. Evita oscilações rápidas de interface.
- `line_cd=` (segundos): Cooldown interno exclusivo para esta linha específica do arquivo YAML.

### Grupo: Cast Behavior (Comportamento de Lançamento)
- `interrupt=`: Se `true`, permite que este feitiço interrompa o próprio cast do jogador. Ex: `counterspell,interrupt=true`.
- `ignore_usable=`: Se `true`, pula as checagens de CD e de recursos. O feitiço é sugerido a qualquer momento.
- `ignore_cooldown=`: Pula apenas a verificação de CD (recursos ainda são necessários).
- `ignore_movement=`: Permite o lançamento deste feitiço de tempo de cast em movimento.
- `ignore_queue=`: Ignora a verificação `isCurrentSpell`, permitindo pressionar seguidamente para encadear casts.
- `ignore_blocked=`: Ignora todas as formas de bloqueio (desabilitado pelo usuário, /blocked, CDs desligados globalmente, etc.).
- `ignore_cds_toggle=`: Ignora o bloqueio apenas quando a causa é a opção global de Cooldowns estar desligada.
- `casting_check=`: Restringe o step para rodar apenas se o jogador estiver castando ou canalizando. Valores: `any` ou nome do feitiço.
- `empower_to=`: Gerencia feitiços empoderados (Evoker). Lança e segura o empoderamento até atingir o estágio N. Ex: `empower_to=2`.

### Grupo: Resource Pooling (Reserva de Recursos)
- `resource=`: Usado com `pool_resource` para especificar o recurso a reservar (ex: `resource=holy_power`).
- `for_next=`: Usado com `pool_resource` para isentar os próximos N passos de feitiço do bloqueio de recursos.

### Grupo: Off-GCD & Keybinding (Atalhos e Sem GCD)
- `off_gcd=`: Se `true`, avalia o feitiço durante o GCD de outro feitiço (exibido como um ícone menor sobreposto).
- `override=`: Usa a atalho de teclado associada a outro feitiço (ex: `override=spell_name`).
- `hotkey=`: Define/sobrescreve o scan code do teclado (ex: tecla 1 é 49).
- `modifier=`: Define/sobrescreve a tecla modificadora (16=Shift, 17=Ctrl, 18=Alt).
- `snapshot=`: Captura um log de diagnóstico em arquivo `SpellName_YYYYMMDD_HHMMSS.log` no momento em que é sugerido.

### Grupo: Fora do Catálogo (observados no dump de 2026-08-30)

O bloco `stepModifiers` do `expression-catalog.json` lista **26** modificadores.
Os abaixo aparecem no `simia_data_dump/` e **não** estão nessa lista. Mesma regra
da seção 12: ausência do catálogo não é prova de invalidade, mas nenhum destes
foi verificado em jogo por este repositório.

| Modificador | Usos | O que parece fazer | Onde aparece |
|---|---|---|---|
| `use_off_gcd=1` | 52 | Variante de `off_gcd=true`. Vários autores usam a forma `use_off_gcd=1` em vez da catalogada. **Não é confirmado que as duas sejam a mesma coisa** — se `use_off_gcd` for ignorado pelo motor, a linha simplesmente consome um GCD normal. As rotações Guardian deste repo dependem disso para o Ironfur. | `community_Argent_Crusade_Holy_Paladin`, `community_Battle_Nurse_Paladin`, Guardian daqui |
| `use_while_casting=1` | 19 | Permite lançar durante o cast de outro feitiço. Sempre pareado com `use_off_gcd=1` + `interrupt=true` no padrão Fire Blast. | `community_Jecht_Fire_Mage` |
| `chain=1` | 4 | Encadeia canalizações — mantém o canal rodando em vez de recomeçar. | `community_Shadow_priest___TeK` (Mind Flay) |
| `interrupt_if=` | 3 | Corta a própria canalização quando a expressão vira verdadeira. Aceita número (`interrupt_if=2`, ticks) e expressão (`interrupt_if=energy.time_to_max<2`). | `community_LPOutlaw_V1`, `community_Shadow_priest___TeK` |
| `moving=1` | 6 | Marca a linha como utilizável em movimento. Distinto de `ignore_movement=` (catalogado) — nenhum arquivo usa os dois juntos. | `rotation_262.yaml` (**rotação oficial**) |
| `unit=` | 10 | Unidade fixa por token em vez de `cycle=`/`range_check=`. Valores vistos: `player`, `party1`..`party4`. Uma linha por membro. | `community_Jecht_Fire_Mage` (Remove Curse) |
| `target_if=` | 1 | Modificador do SimC. **Só aparece uma vez em todo o dump**, num fork da rotação Guardian deste repo, e todas as outras ocorrências no dump estão comentadas como import de APL do SimC. Continua sem evidência de que o motor o implemente — as rotações daqui deliberadamente usam `if=` no lugar. | `community_Ferraz_Guardian_Druid_M___Elunes_` |

---

## 4. Estrutura Geral do Arquivo YAML

Os campos de metadados vão no nível raiz do seu arquivo YAML (fora de `lists:`).

| Chave | Tipo | Descrição |
|---|---|---|
| `spec` | integer | **Obrigatório:** ID da especialização (ex: 71 Arms, 103 Feral, 104 Guardian, 105 Resto Druid) |
| `name` | string | Nome de exibição na interface do usuário (UI). Se omitido, o nome do arquivo é exibido. |
| `version` | string | String de versão da rotação. Exibida como "Nome (versão)". |
| `author` | string | Nome do autor. Exibido como "Nome (versão) - Autor". |
| `description` | string | Descrição curta da rotação. |
| `movement_allowed` | expression | Expressão SimC. Quando verdadeira, permite lançar feitiços com tempo de cast em movimento. Ex: `buff.ice_floes.up` |
| `spell_overrides` | map | Mapa de feitiços para expressões SimC. Condição global AND-ada a cada ocorrência do feitiço. |
| `config` | map | Widgets de UI personalizados (sliders, checkboxes, etc.) exibidos no painel de configurações. |
| `variables` | map | Expressões SimC nomeadas que são avaliadas a cada tick. Referenciadas via `var.NAME`. |
| `tier_sets` | map | Mapa de definições de bônus de tier set. |
| `lists` | map | Listas de prioridade de ação. O ponto de entrada obrigatório é a lista `main`. |

---

## 5. Config Widgets (UI)

Configurações criam widgets de interface (sliders, checkboxes, dropdowns, etc.) editáveis no painel de controle do Simia. São definidas no bloco `config:` e referenciadas por `cfg.NAME`.

### Tipos de Widgets Disponíveis


### Widget: `slider`
Numeric slider. Referenced as cfg.NAME (returns number).

**Exemplo de Sintaxe:**
```yaml
energy_threshold:
  section: "Resources"
  type: slider
  min: 20
  max: 80
  value: 50
```

### Widget: `checkbox`
Boolean toggle. Referenced as cfg.NAME (returns 0 or 1).

**Exemplo de Sintaxe:**
```yaml
use_defensives:
  type: checkbox
  value: true
```

### Widget: `dropdown`
Single selection dropdown. Referenced as cfg.NAME (returns selected option value).

**Exemplo de Sintaxe:**
```yaml
burst_mode:
  type: dropdown
  options:
    - label: "Conservative"
      value: 1
    - label: "Aggressive"
      value: 2
  default: 0
```

### Widget: `multi_select`
Multiple selection. Use cfg.NAME.has(VALUE) to check, cfg.NAME>=1 for count.

**Exemplo de Sintaxe:**
```yaml
burst_tools:
  type: multi_select
  options:
    - label: "Trinket 1"
      value: 1
    - label: "Trinket 2"
      value: 2
  default: [0]
```

### Widget: `unit_select`
Party/raid member selector. Use with cycle=config.NAME.

**Exemplo de Sintaxe:**
```yaml
pi_target:
  type: unit_select
  filter: dps
  max: 1
```

### Widget: `toggle`
Ephemeral boolean toggle. State always starts OFF and is never saved. Shows spell icon on overlay when active. Can be hotkeyed. Referenced as cfg.NAME (returns 0 or 1). show_override is always true.

**Exemplo de Sintaxe:**
```yaml
reju_spread:
  type: toggle
  label: "Rejuvenation Spread"
  spell: 774
  description: "Spread Rejuvenation to group members missing the HoT"
```

### Widget: `number`
Direct numeric entry (same data as slider, different widget). Referenced as cfg.NAME (returns number). If min and max are both 0, no clamping is applied. Aliases: number_input.

**Exemplo de Sintaxe:**
```yaml
trinket_ilvl_min:
  section: "Items"
  type: number
  min: 0
  max: 999
  default: 600
```

### Widget: `copy_text`
Read-only text with a Copy button. Display-only — never saved, not referencable in conditions. Useful for talent strings, WeakAura imports, macros. Aliases: copy, copytext, copy-text.

**Exemplo de Sintaxe:**
```yaml
recommended_talents:
  section: "Talents"
  type: copy_text
  label: "Recommended Talent String"
  text: "B4PAAAAAAAAAAAAAAAAAAAAAAAESLDgZmlZGTbDsZmlZmZmZmlxMmZmlZ2YmFAA"
```

### Widget: `link`
Button that opens a URL in the default browser. The label is the button text; the URL appears as a tooltip on hover. Display-only — never saved, not referencable in conditions. Alias: url.

**Exemplo de Sintaxe:**
```yaml
guide_link:
  section: "Help"
  type: link
  label: "Open Guide"
  url: "https://www.wowhead.com/guide/classes/warrior/arms/rotation-cooldowns-pve-dps"
```

### Widget: `note`
Static informational text block (wraps to width). Display-only — never saved, not referencable in conditions. Use for explanations longer than what fits in a description tooltip. Aliases: info, text.

**Exemplo de Sintaxe:**
```yaml
pvp_note:
  section: "PvP"
  type: note
  label: "PvP rotation tips"
  text: "This APL assumes Gladiator's Medallion. Without one, enable manual_dispel and bind it."
```

### Widget: `divider`
Horizontal separator line. Display-only — never saved, not referencable in conditions. Alias: separator.

**Exemplo de Sintaxe:**
```yaml
divider_after_resources:
  type: divider
```

### Widget: `button`
Clickable button. If url is set, opens the URL. Otherwise, if text is set, copies it to the clipboard. Display-only — never saved, not referencable in conditions. The action field is reserved for future named-action dispatch.

**Exemplo de Sintaxe:**
```yaml
copy_macro:
  section: "Macros"
  type: button
  label: "Copy interrupt macro"
  text: "/cast [@mouseover,harm,nodead][@target] Pummel"
```

### Não é um tipo: `bool`

`type: bool` aparece **uma vez** no dump inteiro
(`community_TeK_s_Derpwizard_Frost_mage.yaml`), contra 327 usos de `checkbox`.
Um único uso isolado não é um tipo de widget — é um erro de digitação de um
autor. Use `checkbox`.


---

## 6. Variáveis & Spell Overrides

### Variáveis (`variables:`)
As variáveis permitem definir **expressões nomeadas** que são avaliadas a cada tick do sistema. Evitam duplicação de lógica complexa e tornam a rotação mais legível. Use `var.NAME` para referenciá-las.

```yaml
variables:
  execute_phase: target.health.pct<20
  pooling: cooldown.big_cooldown.remains<5&energy<80
  burst_window: player.burst.active|cooldown.avatar.remains<gcd

lists:
  main:
    - execute,if=var.execute_phase
    - big_cooldown,if=var.burst_window&!var.pooling
```

### Spell Overrides (`spell_overrides:`)
Adiciona uma **condição lógica global** para um feitiço específico. A expressão definida é automaticamente combinada (através do operador lógico AND) com cada step que utiliza este feitiço na rotação.

```yaml
spell_overrides:
  combustion: "buff.hot_streak.up&cooldown.fire_blast.charges>=1"
  rune_of_power: "cooldown.combustion.remains<5"
  frozen_orb: "!player.moving"
```
*Isso evita duplicar as mesmas checagens de segurança (como cooldowns combinados ou restrição de movimento) em várias linhas da rotação.*

---

## 7. Padrões Comuns, Receitas & Exemplos

### Receitas Rápidas (Copy-Paste)

#### 1. Interromper Cast do Alvo
```yaml
- pummel,interrupt=true,if=target.incoming_cast.kickable.ready
```
*Permite interromper o próprio cast (`interrupt=true`) para chutar o cast do alvo se ele for interrompível (`kickable`).*

#### 2. Interromper Alvo em Foco (Focus)
```yaml
- counterspell.focus,range_check=focus,interrupt=true,if=focus.incoming_cast.kickable.ready
```
*Dispara no foco (`.focus`) com checagem de alcance correspondente (`range_check=focus`).*

#### 3. Defensivo por Limite de Vida
```yaml
- shield_wall.player,range_check=none,if=health.pct<30
```
*Usa em si mesmo (`.player`) e pula verificação de alcance (`range_check=none`).*

#### 4. Defensivos em Membros do Grupo (Cycle de HP)
```yaml
- blessing_of_protection,cycle=members,if=cycle.health.pct<20&cycle.range<=40
```
*Varre o grupo (`cycle=members`) e lança no membro com menor vida abaixo de 20%.*

#### 5. Alternar entre AoE e Single Target
```yaml
lists:
  main:
    - call_action_list,name=aoe,if=active_enemies>=3&state.aoe
    - call_action_list,name=single_target
```
*`state.aoe` respeita o botão de alternar AoE na interface do Simia.*

#### 6. Gerenciamento de Movimentação
```yaml
# Globalmente: permite qualquer feitiço em movimento se Ice Floes estiver ativo
movement_allowed: buff.ice_floes.up

# Por feitiço: permite apenas este feitiço específico
- scorch,ignore_movement=true,if=player.moving
```

#### 7. Spam de Filler (Bypass de Fila)
```yaml
- living_flame,interrupt=true,ignore_queue=true
```
*`ignore_queue=true` permite enfileirar o feitiço de forma fluida durante a própria canalização/cast anterior.*

#### 8. Uso Condicional de Cooldowns sob Controle de Botão do Usuário
```yaml
lists:
  main:
    - call_action_list,name=cooldowns,if=state.cds&cfg.use_cds
```
*Combina o atalho global do overlay (`state.cds`) com uma checkbox de configuração local (`cfg.use_cds`).*

---

### Exemplos Completos de Rotação

#### Exemplo 1: Rotação de DPS com Cooldowns (Arms Warrior)

```yaml
spec: 71
name: "Arms Warrior PvE"
author: "Rubim"
version: "2.0.0"

spell_overrides:
  avatar: "cooldown.colossus_smash.remains<gcd"

config:
  execute_hp:
    section: "Combate"
    type: slider
    min: 15
    max: 35
    value: 20
  use_cds:
    section: "Cooldowns"
    type: checkbox
    value: true

variables:
  execute_phase: target.health.pct<cfg.execute_hp
  burst_window: player.burst.active|cooldown.colossus_smash.remains<gcd

lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=auto_target
    - call_action_list,name=interrupts
    - call_action_list,name=defensives
    - call_action_list,name=cooldowns,if=state.cds&cfg.use_cds
    - call_action_list,name=aoe,if=active_enemies>=3&state.aoe
    - call_action_list,name=execute,if=var.execute_phase
    - call_action_list,name=single_target

  interrupts:
    - pummel,interrupt=true,if=target.incoming_cast.kickable.ready

  defensives:
    - shield_wall.player,range_check=none,if=health.pct<30
    - victory_rush,if=buff.victorious.up&health.pct<70

  cooldowns:
    - avatar
    - trinket1,if=trinket_1.sync

  aoe:
    - thunder_clap,if=active_enemies>=2
    - whirlwind,if=active_enemies>=3
    - cleave,if=buff.overpower.stack>=2

  execute:
    - execute

  single_target:
    - mortal_strike,if=debuff.mortal_wounds.refreshable
    - overpower,if=buff.overpower.stack<2
    - slam
```

#### Exemplo 2: Rotação de Healer (Discipline Priest)

```yaml
spec: 256
name: "Discipline Priest"
author: "SimiaPro"
version: "2.0.0"

movement_allowed: buff.body_and_soul.up

spell_overrides:
  power_infusion: "!player.moving"

config:
  emergency_hp:
    section: "Cura"
    type: slider
    min: 10
    max: 40
    value: 25
  tank_hp:
    section: "Cura"
    type: slider
    min: 30
    max: 80
    value: 60
  pi_target:
    section: "Utilitários"
    type: unit_select
    filter: dps
    max: 1

variables:
  ramp: cooldown.evangelism.remains<5

lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=emergency
    - call_action_list,name=dispels
    - call_action_list,name=cooldowns,if=state.cds
    - call_action_list,name=tank_healing
    - call_action_list,name=maintenance
    - call_action_list,name=group_healing

  emergency:
    - flash_heal,cycle=members,if=cycle.health.pct<cfg.emergency_hp&cycle.range<=40
    - desperate_prayer.player,range_check=none,if=health.pct<20

  dispels:
    - purify,cycle=members,if=cycle.dispelable.purify&cycle.range<=40

  cooldowns:
    - power_infusion,cycle=config.pi_target,if=cfg.pi_target&cooldown.power_infusion.ready
    - trinket1,if=trinket_1.ready

  tank_healing:
    - heal,cycle=tanks,if=cycle.health.pct<cfg.tank_hp&cycle.range<=40

  maintenance:
    - renew,cycle=members,if=cycle.buff.renew.refreshable&cycle.health.pct<90&cycle.range<=40
    - power_word_shield,cycle=members,if=var.ramp&cycle.buff.atonement.down&cycle.range<=40

  group_healing:
    - prayer_of_healing,if=group.count(cycle.health.pct<60)>=3
    - heal,cycle=members,if=cycle.health.pct<70&cycle.range<=40
```

#### Exemplo 3: Rotação com Janela de Burst (Fire Mage)

```yaml
spec: 63
name: "Fire Mage"
author: "SimiaPro"
version: "2.0.0"

movement_allowed: buff.ice_floes.up

spell_overrides:
  combustion: "buff.hot_streak.up&cooldown.fire_blast.charges>=1"
  rune_of_power: "cooldown.combustion.remains<5"

config:
  emergency_hp:
    section: "Defensivos"
    type: slider
    min: 10
    max: 40
    value: 20

variables:
  burst_window: player.burst.active|buff.bloodlust.up.any
  execute_phase: target.health.pct<20
  pooling: cooldown.combustion.remains<5&!var.burst_window

lists:
  main:
    - call_action_list,name=spell_queue
    - call_action_list,name=sanity_checks
    - call_action_list,name=auto_target
    - call_action_list,name=interrupts
    - call_action_list,name=defensives
    - return,if=var.pooling
    - call_action_list,name=burst,if=var.burst_window&state.cds
    - call_action_list,name=execute,if=var.execute_phase
    - call_action_list,name=standard

  interrupts:
    - counterspell,interrupt=true,if=target.incoming_cast.kickable.ready

  defensives:
    - ice_barrier.player,range_check=none,if=health.pct<30

  burst:
    - combustion,if=cooldown.combustion.ready
    - rune_of_power
    - trinket1,if=trinket_1.sync
    - fire_blast,if=cooldown.fire_blast.charges>=1
    - pyroblast,if=buff.hot_streak.up

  execute:
    - scorch,if=target.health.pct<20

  standard:
    - fireball,if=!player.moving
    - scorch,if=player.moving
```

---

## 8. Operadores SimC

### Lógicos
- `&`: AND lógico. Ambas as expressões devem ser verdadeiras.
- `|`: OR lógico. Pelo menos uma expressão deve ser verdadeira.
- `!`: NOT lógico. Nega o valor lógico seguinte.

### Comparação
`<`, `<=`, `>`, `>=`, `=`, `!=` (o símbolo `=` funciona como `==`).

### Aritméticos
- `+`, `-`, `*`, `/`: Operações aritméticas padrão.
- `>?`: Mínimo (SimC). Retorna o menor valor. `a >? b` = `min(a, b)`.
- `<?`: Máximo (SimC). Retorna o maior valor. `a <? b` = `max(a, b)`.
- `()` : Precedência de agrupamento lógico.

---

## 9. Ações Virtuais

Ações virtuais são comandos especiais que podem ser sugeridos na rotação substituindo habilidades nativas, atuando como emuladores de hardware ou lógica de UI.

| Ação | Descrição |
|---|---|

| `trinket1` | Use trinket in slot 1. |
| `trinket2` | Use trinket in slot 2. |
| `attack_target` | Start auto-attacking the target. |
| `interact_target` | Interact with target. |
| `stop_casting` | Cancel current cast. |
| `loot_a_rang` | Use Loot-A-Rang. |
| `healthstone` | Use Healthstone. |
| `augment_rune` | Use Augment Rune. |
| `health_potion` | Use Health Potion. |
| `mana_potion` | Use Mana Potion. |
| `weapon_on_use` | Activate weapon on-use effect. |
| `wrist_on_use` | Activate wrist on-use effect. |
| `helm_on_use` | Activate helm on-use effect. |
| `cloak_on_use` | Activate cloak on-use effect. |
| `belt_on_use` | Activate belt on-use effect. |
| `target_mouseover` | Target the mouseover unit. |
| `interact_mouseover` | Interact with mouseover unit. |
| `target_focus` | Target the focus unit. |
| `focus_target` | Set current target as focus. |
| `focus_mouseover` | Set mouseover as focus. |
| `target_enemy` | Target nearest enemy. |
| `one_button_assist` | Press the one-button assistant keybind directly. |
| `one_button_assist_lookup` | Look up and press the keybind for the spell suggested by the one-button assistant. |
| `pool_resource` | Resource reservation gate. When its condition is true, marks a resource as reserved so lower-priority steps that would spend it are skipped. Use resource= to name the resource explicitly, or for_next=N to auto-detect it from the next N spell steps. The directly targeted spell (for_next) is exempt from the block. Never produces a suggestion — only controls what fires below it. |


---

## 10. Erros Conhecidos & Boas Práticas

### 🛑 Não Fazer
1. **`cycle=target` ou `cycle=enemies`** — O Simia não suporta ciclar alvos inimigos diretamente pelo cycle. Para isso, use o comando `target_enemy` combinado com condições em passos subsequentes.
2. **`cycle=party`** — O termo correto para iterar sobre membros do grupo é `cycle=members`.
3. **Esquecer as listas obrigatórias** — Deixar de chamar `spell_queue`, `sanity_checks` e `auto_target` no topo da lista `main` impedirá o correto funcionamento da rotação.

### ✅ Boas Práticas
1. **Interrupt Scanning Limpo:** Use a seguinte estrutura para alternar alvos e interromper casts importantes:
   ```yaml
   - target_enemy,delay=100,name="Buscar Alvo para Chutar",if=!interrupts.target.ready&interrupts.5y.ready
   - solar_beam,name="Chutar Cast",if=interrupts.target.ready
   ```
2. **Use Sempre `name="..."`:** Adicione descrições em suas linhas de ação. Isso facilita drasticamente a depuração através dos logs de execução do Simia.
3. **Priorize `charges_fractional` sobre `charges`:** Permite otimizar habilidades com cargas dinâmicas antes que a recarga total seja atingida.
4. **Bypass de Alcance para Self-Buffs:** Sempre inclua `range_check=none` para feitiços autolançados ou self-buffs para evitar travamento da rotação se você estiver sem alvo.
5. **Checagem de Buffs Externos:** Use o sufixo `.any` para buffs que podem vir de outros jogadores do grupo (como Sede de Sangue/Bloodlust: `buff.bloodlust.up.any`).
6. **Bônus de Pandemia:** Sempre verifique se os DoTs ou HoTs estão renováveis usando `.refreshable` ou `.remains < pandemic_threshold` antes de reaplicá-los para evitar desperdício de GCD e recursos.
7. **Não existe contagem de inimigos consciente de melee.** `target.in_melee` e
   `target.melee_gap` são testes **por unidade**, não contagens. Para contar, só existem
   `enemies.Xy` e `enemies.combat.Xy` com jardagem fixa — use `enemies.combat.8y` para AoE
   melee (é o que a própria lista `auto_target` do Simia usa). O `.combat` importa: sem ele
   você conta mob que ninguém puxou.

8. **`active_enemies` é contagem de NAMEPLATE, não de inimigos engajados.** Ele inclui
   qualquer mob na tela — boneco de treino parado ao lado, pack que o tank ainda não
   alcançou, add de outra plataforma. Isso silenciosamente desliga linhas com gate de
   contagem (`active_enemies<6`) e dispara cooldown em pull que ainda não existe. Prefira
   `enemies.combat.40y` (ranged) ou `enemies.combat.8y` (melee), que contam só quem está
   em combate e no alcance.

9. **Melee: use `target.in_melee`, não `target.range<=N`:** `target.range` é distância de **borda** (já desconta o alcance de combate das duas unidades), então o valor de "melee máximo" muda com o tamanho do mob — 4.5 num mob pequeno, 2.33 num boss de reach 9. `target.in_melee` replica o cálculo do cliente e é invariante ao tamanho. Para "N jardas longe do melee" use `target.melee_gap>=N` (0 enquanto em melee, nunca negativo).
10. **Geometria e AoE: use `.distance`, não `.range`:** `target.distance` / `focus.distance` / `mouseover.distance` são distância de **centro**, sem desconto de reach e sem clamp — é a unidade em que raios de AoE e mecânicas de boss são medidos, e a única válida para geometria ou clustering. Vale a identidade `target.distance - target.range = soma dos dois reaches`.
11. **Cones e facing:** `player.facing.target[.N]` (padrão ±90°) para checar se você está de frente, `target.facing.player[.N]` para checar se o mob está de frente para você (evitar parry/frontal), e `enemies.around.angle.N[.Y]` para contar inimigos dentro de um cone — o caminho correto para habilidades em cone em vez de contar por raio.
12. **NPC específico sem precisar targetar:** `active_npc.NPC_ID.*` varre todas as nameplates do pull (count, ttd, min_ttd, range, health.pct). Adicione `.any` para NPCs que nunca entram em combate (geradores, adds neutros de objetivo).
13. **A fila de feitiços NÃO é filtrada por cooldown na ENTRADA.** O comentário do
   `_shared.yaml` promete que a fila "only casts if the queued spell is usable (valid,
   off CD, has charges)" — o "off CD" só vale no flush, nunca na entrada. Motivo: o
   addon usa `IsUsableSpell()` do WoW, que checa recurso e estado mas **ignora
   cooldown** (isso é `GetSpellCooldown`, outra chamada). Um snapshot mostra os dois
   fatos lado a lado:

   ```
   === QUEUE (1) ===
     [1] ID=106898 (Stampeding Roar)

   [106898] (Stampeding Roar) usable=YES ... cd=26.8/120.0
   ```

   O feitiço entrou na fila com 26,8s de CD restante. O flush recusou corretamente
   (`SANITY FAIL: no usable queued spell or blocked by queue_logic`), então ele não é
   castado — mas a entrada permanece, e dispara quando o CD virar.

   **Isso não é corrigível no YAML.** A fila é populada pelo Lua (`MemData[10]`) no
   instante da pressão da tecla; nenhuma expressão da rotação é avaliada nesse momento.
   O bloco `queue_logic:` gateia o **cast**, não a entrada — é a mesma barreira que já
   recusou acima. Não gaste tempo procurando uma expressão de entrada: não existe.

14. **`queue_spell` tem duas formas com significados opostos.** `queue_spell` pelado
   despeja o que o **jogador** enfileirou. `queue_spell,spell=X,if=...` faz a
   **rotação** enfileirar X — serve para off-GCD que o addon não consegue apertar
   durante um hardcast (ver `community_Jecht_Fire_Mage_v1_1.yaml`). Trocar uma pela
   outra por engano adiciona casts automáticos que ninguém pediu.

15. **`queue_spell` quer `&`, não `|`.** A forma herdada do `_shared.yaml` é
   `if=!player.casting|!player.channeling`, que é verdadeira sempre que você não está
   fazendo **pelo menos uma** das duas coisas — e as duas quase nunca se sobrepõem, então
   a condição lê verdadeiro em toda passada e não guarda nada. O correto é
   `!player.casting&!player.channeling`.

16. **`hero_tree.NOME` existe e NÃO está no catálogo.** São 26 árvores de herói
   (`hero_tree.wildstalker`, `hero_tree.druid_of_the_claw`, `hero_tree.elunes_chosen`,
   `hero_tree.diabolist`, ...) usadas por 27+ rotações oficiais do `simia_data_dump`,
   e `expression-catalog.json` não traz nenhuma delas. **Expressão ausente do
   catálogo não é prova de que é inválida** — confira as `rotation_*.yaml` oficiais
   antes de remover qualquer coisa por "não existe". O mesmo vale para
   `queue_logic` e para a descrição de `queue_spell`.

17. **`enemies.around_target` conta em volta do ALVO, não em volta de você.**
   Existe também como `enemies_around_target`. Para feitiço de área ancorado no
   alvo — Rain of Fire, Starfall — é a pergunta certa, e é o que a rotação oficial
   de Destruction usa. `enemies.combat.Xy` continua sendo o certo para "quantos
   inimigos estão me batendo".

18. **`.focus_mouseover` é sufixo de cast válido.** A tabela da seção 2 lista
   `focus_mouseover` apenas como ação avulsa ("Set mouseover as focus"), mas cinco
   rotações da comunidade e a `rotation_270.yaml` oficial usam como sufixo:
   `word_of_glory.focus_mouseover`, `riptide.focus_mouseover`.

19. **`range_check=` aceita cinco valores, não dois.** Contagem no dump:
   `none` (730), `mob` (52), `mouseover` (31), `focus` (14), `target` (1). A seção 3
   só cita `none` e `focus`.

20. **`mouseover.unitframe` é FALSO para unidade do mundo 3D.** Gatear cura nele —
   `mouseover.exists&mouseover.friendly&mouseover.unitframe` — torna impossível curar
   qualquer NPC amigo que não esteja num frame de grupo. É o gate que impedia
   qualquer linha de alcançar o Avatar of Sethraliss.

21. **Uma linha de troca de forma pode entrar em loop.** `bear_form,if=X&(moonkin.up|bear.up)`
   trava: já em urso, sugere urso, o estado não muda, a condição continua verdadeira e
   a linha come todo global. **Quebrar raiz exige MUDANÇA de forma** — trocar para a
   forma em que você já está não limpa nada. Ou exclua a forma de destino da condição,
   ou use duas linhas:

   ```yaml
   - bear_form,if=debuff_list.freedom.up&!buff.bear_form.up
   - cat_form,if=debuff_list.freedom.up&buff.bear_form.up
   ```

22. **`variable.NOME` é forma de LEITURA válida, além de `var.NOME`.** A seção 11.36
   só documenta `var.` e `cfg.`, mas `variable.` aparece em 27 rotações oficiais.

---

## 11. Catálogo de Referência de Expressões

O mecanismo de rotação Simia possui suporte a **634** expressões para formular as condições de lançamento.


### 11.1 Buffs — `buff.SPELL.PROPERTY`
Verifica buffs ativos no próprio jogador. Sem o sufixo `.any`, verifica apenas buffs aplicados pelo próprio jogador.

**Sufixo:** `.any` — Verifica buffs aplicados por qualquer fonte (ex: `buff.bloodlust.up.any`).

**Total de Expressões:** 14

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `up` | bool | Buff is currently active. | `buff.icy_veins.up` |
| `down` | bool | Buff is NOT active. | `buff.shield_wall.down` |
| `stack` | number | Current stack count (0 if not active). | `buff.bone_shield.stack>=5` |
| `remains` | number | Seconds remaining (0 if not active). | `buff.icy_veins.remains<5` |
| `duration` | number | Total duration of the buff in seconds. | `buff.icy_veins.duration` |
| `elapsed` | number | Seconds since the buff was applied. | `buff.icy_veins.elapsed>10` |
| `refreshable` | bool | Remaining time is less than 30% of duration (pandemic window). | `buff.renew.refreshable` |
| `stealable` | bool | Buff can be spell-stolen. | `buff.arcane_intellect.stealable` |
| `mine` | bool | Buff was applied by the player. | `buff.power_word_fortitude.mine` |
| `magic` | bool | Buff has Magic dispel type. | `buff.X.magic` |
| `curse` | bool | Buff has Curse dispel type. | `buff.X.curse` |
| `disease` | bool | Buff has Disease dispel type. | `buff.X.disease` |
| `poison` | bool | Buff has Poison dispel type. | `buff.X.poison` |
| `icon` | number | Texture file ID of the buff icon. | `buff.X.icon` |

### 11.2 Debuffs — `debuff.SPELL.PROPERTY`
Verifica debuffs no alvo atual do jogador.

**Sufixo:** `.any` — Verifica debuffs aplicados por qualquer fonte.

**Total de Expressões:** 15

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `up` | bool | Debuff is currently active on target. | `debuff.rip.up` |
| `ticking` | bool | Same as .up. Debuff is ticking on target. | `debuff.shadow_word_pain.ticking` |
| `down` | bool | Debuff is NOT active on target. | `debuff.rip.down` |
| `stack` | number | Current stack count. | `debuff.vulnerability.stack>=3` |
| `remains` | number | Seconds remaining. | `debuff.rip.remains<5` |
| `duration` | number | Total duration in seconds. | `debuff.rip.duration` |
| `elapsed` | number | Seconds since applied. | `debuff.rip.elapsed>3` |
| `refreshable` | bool | Within pandemic refresh window (30% of duration). | `debuff.rip.refreshable` |
| `stealable` | bool | Debuff can be stolen. | `debuff.X.stealable` |
| `mine` | bool | Debuff was applied by the player. | `debuff.X.mine` |
| `magic` | bool | Has Magic dispel type. | `debuff.X.magic` |
| `curse` | bool | Has Curse dispel type. | `debuff.X.curse` |
| `disease` | bool | Has Disease dispel type. | `debuff.X.disease` |
| `poison` | bool | Has Poison dispel type. | `debuff.X.poison` |
| `icon` | number | Texture file ID. | `debuff.X.icon` |

### 11.3 DoTs — `dot.SPELL.PROPERTY`
Alias para debuffs no alvo atual. `dot.SPELL` é semanticamente idêntico a `debuff.SPELL`.

**Total de Expressões:** 7

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `up` | bool | DoT is active on target. | `dot.shadow_word_pain.up` |
| `ticking` | bool | Same as .up. | `dot.rip.ticking` |
| `down` | bool | DoT is NOT active. | `dot.moonfire.down` |
| `remains` | number | Seconds remaining. | `dot.corruption.remains<5` |
| `stack` | number | Stack count. | `dot.agony.stack>=5` |
| `refreshable` | bool | Within pandemic window. | `dot.moonfire.refreshable` |
| `duration` | number | Total duration. | `dot.rip.duration` |

### 11.4 Cooldowns — `cooldown.SPELL.PROPERTY`
Verifica o status de tempo de recarga (cooldown) de um feitiço.

**Total de Expressões:** 11

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `ready` | bool | Spell is off cooldown and ready to use. | `cooldown.mortal_strike.ready` |
| `down` | bool | Spell is on cooldown. | `cooldown.combustion.down` |
| `remains` | number | Seconds until cooldown expires. | `cooldown.fireball.remains<3` |
| `charges` | number | Current available charges. | `cooldown.fire_blast.charges>=1` |
| `max_charges` | number | Maximum charges. | `cooldown.fire_blast.max_charges` |
| `charges_fractional` | number | Charges as a decimal (includes partial recharge). | `cooldown.fire_blast.charges_fractional>=1.5` |
| `full_recharge_time` | number | Seconds until ALL charges are recovered. | `cooldown.fire_blast.full_recharge_time<10` |
| `duration` | number | Cooldown duration in seconds. For charge-based spells, returns per-charge cooldown. | `cooldown.combustion.duration>60` |
| `cast_count` | number | Number of times the spell has been cast (from C_Spell.GetSpellCastCount). | `cooldown.fireball.cast_count>=3` |
| `blocked` | bool | Spell is user-blocked: Enabled=false in the spell list, session-blocked via /block, or CD-classified while the global CDs toggle is off. Queued spells bypass the block state. Blocked spells also report remains=99999, ready=0, duration=99999, charges=0 on the regular cooldown.* prefix — use cooldown_bypass.* to see the real CD. | `cooldown.combustion.blocked` |
| `is_cooldown` | bool | Spell is classified as a cooldown (member of cdSpells — either user-marked as CD or in the spec's default cooldown list). Independent of the effective block state; combine with state.cds to distinguish 'blocked via CDs off' (is_cooldown & !state.cds) from 'user-disabled' (blocked & !is_cooldown). | `cooldown.combustion.is_cooldown & !state.cds` |

### 11.5 Cooldown Bypass — `cooldown_bypass.SPELL.PROPERTY`
Mesmas propriedades que `cooldown`, porém **ignora o estado bloqueado** globalmente ou por TTD.

**Total de Expressões:** 10

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `ready` | bool | Spell is really off cooldown (ignores blocked state). | `cooldown_bypass.combustion.ready` |
| `down` | bool | Spell is really on cooldown (ignores blocked state). | `cooldown_bypass.combustion.down` |
| `remains` | number | Real seconds until cooldown expires (ignores blocked state). | `cooldown_bypass.big_damage.remains<5` |
| `charges` | number | Real current available charges (ignores blocked state). | `cooldown_bypass.fire_blast.charges>=1` |
| `max_charges` | number | Maximum charges. | `cooldown_bypass.fire_blast.max_charges` |
| `charges_fractional` | number | Real charges including partial progress (ignores blocked state). | `cooldown_bypass.fire_blast.charges_fractional>=1.5` |
| `full_recharge_time` | number | Real seconds until all charges recovered (ignores blocked state). | `cooldown_bypass.fire_blast.full_recharge_time<10` |
| `duration` | number | Cooldown duration in seconds. | `cooldown_bypass.combustion.duration` |
| `cast_count` | number | Number of times the spell has been cast (from C_Spell.GetSpellCastCount). | `cooldown_bypass.fireball.cast_count>=3` |
| `blocked` | bool | Same as cooldown.SPELL.blocked — spell is user-blocked. | `cooldown_bypass.combustion.blocked` |

### 11.6 Talentos — `talent.SPELL`
Verifica a seleção de talentos do jogador.

Exemplos de uso: `talent.SPELL.enabled` (ou simplesmente `talent.SPELL`) e `talent.SPELL.rank`.

**Total de Expressões:** 3

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `(bare)` | bool | Talent is learned (rank > 0). | `talent.soul_reaper` |
| `enabled` | bool | Same as bare — talent is learned. | `talent.soul_reaper.enabled` |
| `rank` | number | Talent rank (0 = not learned, 1+ = learned). | `talent.soul_reaper.rank>=2` |

### 11.7 Ações de Feitiço — `action.SPELL.PROPERTY`
Verifica dados dinâmicos sobre a execução de um feitiço.

**Total de Expressões:** 9

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `cast_time` | number | Cast time in seconds. | `action.fireball.cast_time<2` |
| `execute_time` | number | Max of cast time and GCD. | `action.fireball.execute_time` |
| `charges` | number | Current available charges. | `action.fire_blast.charges>=1` |
| `blocked` | bool | Spell/action is user-blocked (Enabled=false, session-blocked via /block, or CD-classified while the global CDs toggle is off). Queued spells bypass the block state. Mirrors cooldown.SPELL.blocked. | `action.combustion.blocked` |
| `is_cooldown` | bool | Spell/action is classified as a cooldown (member of cdSpells). Use with state.cds to detect 'blocked via CDs off' specifically: action.X.is_cooldown & !state.cds. Mirrors cooldown.SPELL.is_cooldown. | `action.combustion.is_cooldown` |
| `cooldown.remains` | number | Cooldown remaining. | `action.combustion.cooldown.remains<5` |
| `cooldown.ready` | bool | Spell is off cooldown. | `action.combustion.cooldown.ready` |
| `cooldown.down` | bool | Spell is on cooldown. | `action.combustion.cooldown.down` |
| `overlayed` | bool | Action-bar proc glow is active for this spell (from IsSpellOverlayed). Checks the override spell too, so it covers SimC's demonsurge_available-style gates. | `action.metamorphosis.overlayed` |

### 11.8 Recursos — `RESOURCE[.PROPERTY]`
Verifica recursos do jogador (rage, energy, mana, focus, combo_points, runic_power, rune, soul_shards, holy_power, chi, insanity, stagger, arcane_charges, fury, pain, maelstrom, astral_power, essence).

**Total de Expressões:** 26

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `(bare)` | number | Current value (same as .current). | `energy` |
| `current` | number | Current amount. | `energy.current` |
| `max` | number | Maximum amount. | `energy.max` |
| `deficit` | number | Missing amount (max - current). | `energy.deficit>=40` |
| `pct` | number | Percentage of max (0-100). | `mana.pct>=20` |
| `regen` | number | Regeneration rate per second (mana/energy/focus only). | `energy.regen` |
| `time_to_max` | number | Seconds until full (mana/energy/focus only). | `energy.time_to_max<3` |
| `charged` | number | Charged combo points (combo_points only, Rogue Supercharger talent, player only). Via GetUnitChargedPowerPoints. | `combo_points.charged>=1` |
| `rage` |  |  | `rage>=50` |
| `energy` |  |  | `energy>=35` |
| `mana` |  |  | `mana.pct>=20` |
| `focus` |  |  | `focus>=40` |
| `combo_points` |  |  | `combo_points>=5` |
| `runic_power` |  |  | `runic_power>=80` |
| `rune` |  |  | `rune>=3` |
| `soul_shards` |  |  | `soul_shards>=3` |
| `holy_power` |  |  | `holy_power>=3` |
| `chi` |  |  | `chi>=3` |
| `insanity` |  |  | `insanity>=60` |
| `stagger` |  |  | `stagger.pct>50` |
| `arcane_charges` |  |  | `arcane_charges>=3` |
| `fury` |  |  | `fury>=40` |
| `pain` |  |  | `pain>=60` |
| `maelstrom` |  |  | `maelstrom>=60` |
| `astral_power` |  |  | `astral_power>=40` |
| `essence` |  |  | `essence>=2` |

### 11.9 Player — `player.PROPERTY`
Propriedades de estado do próprio jogador (vida, movimento, combate, montado, buffs ativos, CC, dispelabilidade, etc.).

**Total de Expressões:** 80

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Health | `player.health.pct` | number | Player health percentage (0-100). | `player.health.pct<50` |
| Health | `player.health.current` | number | Current health points. | `player.health.current<100000` |
| Health | `player.health.max` | number | Maximum health. | `player.health.max` |
| Health | `player.health.deficit` | number | Missing health (max - current). | `player.health.deficit>50000` |
| Health | `player.health.effective.pct` | number | Effective healable health % (healthPct - healAbsorbPct + incomingHealsPct). Healer triage metric. | `player.health.effective.pct<50` |
| Absorbs & Incoming Heals | `player.absorb` | number | Damage absorb shield amount (UnitGetTotalAbsorbs). Shields like Power Word: Shield. | `absorb>0` |
| Absorbs & Incoming Heals | `player.absorb.pct` | number | Damage absorb as % of max health. | `absorb.pct>10` |
| Absorbs & Incoming Heals | `player.heal_absorb` | number | Heal absorb amount (UnitGetTotalHealAbsorbs). Debuffs that eat incoming healing. | `heal_absorb>0` |
| Absorbs & Incoming Heals | `player.heal_absorb.pct` | number | Heal absorb as % of max health. | `heal_absorb.pct>5` |
| Absorbs & Incoming Heals | `player.incoming_heals` | number | Total incoming heals from all casters (UnitGetIncomingHeals). | `incoming_heals>0` |
| Absorbs & Incoming Heals | `player.incoming_heals.pct` | number | Incoming heals as % of max health. | `incoming_heals.pct>10` |
| Status | `player.alive` | bool | Player is alive. | `player.alive` |
| Status | `player.dead` | bool | Player is dead. | `player.dead` |
| Status | `player.moving` | bool | Player is currently moving. | `player.moving` |
| Status | `player.moving.time` | number | Seconds spent moving. | `moving.time>2` |
| Status | `player.standing` | bool | Player is standing still. | `standing` |
| Status | `player.standing.time` | number | Seconds spent standing still. | `standing.time>1` |
| Status | `player.combat` | bool | Player is in combat. | `combat` |
| Status | `player.combat.time` | number | Seconds spent in combat. | `combat.time>10` |
| Status | `player.auto_attacking` | bool | Player is auto-attacking. | `auto_attacking` |
| Status | `player.mounted` | bool | Player is mounted. | `!mounted` |
| Status | `player.loot_nearby` | bool | Lootable corpse nearby. | `player.loot_nearby` |
| Status | `player.in_vehicle` | bool | Player is in a vehicle. | `!player.in_vehicle` |
| Casting | `player.casting` | bool | Player is casting a spell. | `casting` |
| Casting | `player.channeling` | bool | Player is channeling a spell. | `channeling` |
| Casting | `player.casting.spell_id` | number | Spell ID being cast. | `casting.spell_id=12345` |
| Casting | `player.casting.remains` | number | Milliseconds until cast finishes. | `casting.remains<500` |
| Casting | `player.casting.elapsed` | number | Milliseconds into cast. | `casting.elapsed>1000` |
| Casting | `player.empower_stage` | number | Current empower stage (Evoker). | `empower_stage>=2` |
| Crowd Control | `player.stunned` | bool | Player is stunned. | `stunned` |
| Crowd Control | `player.stunned.remains` | number | Seconds of stun remaining. | `stunned.remains>2` |
| Crowd Control | `player.stunned.elapsed` | number | Seconds since stun started. | `stunned.elapsed` |
| Crowd Control | `player.rooted` | bool | Player is rooted. | `rooted` |
| Crowd Control | `player.rooted.remains` | number | Seconds of root remaining. | `rooted.remains` |
| Crowd Control | `player.feared` | bool | Player is feared. | `feared` |
| Crowd Control | `player.feared.remains` | number | Seconds of fear remaining. | `feared.remains` |
| Crowd Control | `player.silenced` | bool | Player is silenced. | `silenced` |
| Crowd Control | `player.silenced.remains` | number | Seconds of silence remaining. | `silenced.remains` |
| Crowd Control | `player.incapacitated` | bool | Player is incapacitated. | `player.incapacitated` |
| Crowd Control | `player.charmed` | bool | Player is charmed. | `player.charmed` |
| Crowd Control | `player.disarmed` | bool | Player is disarmed. | `player.disarmed` |
| Crowd Control | `player.cc` | bool | Player is in ANY crowd control. | `!player.cc` |
| Stats | `player.haste_pct` | number | Haste percentage. | `haste_pct>30` |
| Stats | `player.crit_pct` | number | Critical strike percentage. | `crit_pct>25` |
| Stats | `player.versa_pct` | number | Versatility percentage. | `versa_pct>15` |
| Stats | `player.mastery_pct` | number | Mastery percentage. | `mastery_pct>50` |
| Role & Spec | `player.melee` | bool | Player is a melee spec. | `player.melee` |
| Role & Spec | `player.ranged` | bool | Player is a ranged spec. | `player.ranged` |
| Role & Spec | `player.tank` | bool | Player is a tank spec. | `player.tank` |
| Role & Spec | `player.healer` | bool | Player is a healer spec. | `player.healer` |
| Role & Spec | `player.dps` | bool | Player is a DPS spec. | `player.dps` |
| Role & Spec | `player.evoker` | bool | Player is an Evoker. | `player.evoker` |
| Instance & Content | `player.indungeon` | bool | Player is in a dungeon. | `player.indungeon` |
| Instance & Content | `player.inraid` | bool | Player is in a raid. | `player.inraid` |
| Instance & Content | `player.inmythicplus` | bool | Player is in a Mythic+ dungeon. | `player.inmythicplus` |
| Instance & Content | `player.inarena` | bool | Player is in an arena. | `player.inarena` |
| Instance & Content | `player.inpvp` | bool | Player is in any PvP content. | `player.inpvp` |
| Instance & Content | `player.ininstancedpvp` | bool | Player is in instanced PvP. | `player.ininstancedpvp` |
| Instance & Content | `player.inpvecontent` | bool | Player is in PvE content. | `player.inpvecontent` |
| Instance & Content | `player.indelve` | bool | Player is in a Delve. | `player.indelve` |
| Instance & Content | `player.inscenario` | bool | Player is in a scenario. | `player.inscenario` |
| Instance & Content | `player.keystonelevel` | number | Current Mythic+ keystone level (0 if not in M+). | `player.keystonelevel>=10` |
| Instance & Content | `player.raid_difficulty` | number | Raw raid difficulty ID from GetInstanceInfo (14=Normal, 15=Heroic, 16=Mythic, 17=LFR; 0 outside raids). | `player.raid_difficulty=16` |
| Instance & Content | `player.raid_difficulty.lfr` | bool | In LFR raid (difficulty 17). | `player.raid_difficulty.lfr` |
| Instance & Content | `player.raid_difficulty.normal` | bool | In Normal raid (difficulty 14). | `player.raid_difficulty.normal` |
| Instance & Content | `player.raid_difficulty.heroic` | bool | In Heroic raid (difficulty 15). | `player.raid_difficulty.heroic` |
| Instance & Content | `player.raid_difficulty.mythic` | bool | In Mythic raid (difficulty 16). | `player.raid_difficulty.mythic` |
| Instance & Content | `player.on_last_boss` | bool | Engaged on the M+ dungeon's final boss (boss unit frame is up and matches the last scenario-criteria step). Drives the per-spell TTD gate: on the last boss, the TTD gate is disabled so CDs dump freely. | `player.on_last_boss` |
| Burst | `player.burst.active` | bool | Any burst buff (from _spells.yaml) is currently active. | `player.burst.active` |
| Burst | `player.burst.count` | number | Count of active burst buffs. | `player.burst.count>=2` |
| Dispels (Self) | `player.has_magic_debuff` | bool | Player has a Magic debuff. | `player.has_magic_debuff` |
| Dispels (Self) | `player.has_curse` | bool | Player has a Curse debuff. | `player.has_curse` |
| Dispels (Self) | `player.has_disease` | bool | Player has a Disease debuff. | `player.has_disease` |
| Dispels (Self) | `player.has_poison` | bool | Player has a Poison debuff. | `player.has_poison` |
| Dispels (Self) | `player.dispelable` | bool | Player has any dispelable debuff (auto-detect). | `player.dispelable` |
| Dispels (Self) | `player.dispelable.SPELL` | bool | Player has debuff dispelable by SPELL. | `player.dispelable.remove_curse` |
| Dispels (Self) | `player.dispelable.list.SPELL` | bool | Same as above but uses dispel_list filtering. | `player.dispelable.list.purify` |
| Misc | `player.auto_combat` | bool | Config-based auto-combat check. | `player.auto_combat` |
| Misc | `player.boss_fight` | bool | Any boss unit frame exists. | `boss_fight` |
| Misc | `player.guid` | number | Player GUID. | `player.guid` |

### 11.10 Target — `target.PROPERTY`
Propriedades de estado do alvo atual.

**Total de Expressões:** 54

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Health | `target.health.pct` | number | Target health percentage (0-100). | `target.health.pct<20` |
| Health | `target.health.current` | number | Current health points. | `target.health.current` |
| Health | `target.health.deficit` | number | Missing health. | `target.health.deficit>100000` |
| Health | `target.health.effective.pct` | number | Target effective healable health %. | `target.health.effective.pct<50` |
| Absorbs & Incoming Heals | `target.absorb` | number | Target damage absorb shield amount. | `target.absorb>0` |
| Absorbs & Incoming Heals | `target.absorb.pct` | number | Target damage absorb as % of max health. | `target.absorb.pct>10` |
| Absorbs & Incoming Heals | `target.heal_absorb` | number | Target heal absorb amount. | `target.heal_absorb>0` |
| Absorbs & Incoming Heals | `target.heal_absorb.pct` | number | Target heal absorb as % of max health. |  |
| Absorbs & Incoming Heals | `target.incoming_heals` | number | Target total incoming heals. |  |
| Absorbs & Incoming Heals | `target.incoming_heals.pct` | number | Target incoming heals as % of max health. |  |
| Status | `target.exists` | bool | A target is selected (has GUID). | `target.exists` |
| Status | `target.alive` | bool | Target is alive. | `target.alive` |
| Status | `target.dead` | bool | Target is dead. | `target.dead` |
| Status | `target.enemy` | bool | Target is an enemy. | `target.enemy` |
| Status | `target.friendly` | bool | Target is friendly. | `target.friendly` |
| Status | `target.attackable` | bool | Target is enemy and not dead. | `target.attackable` |
| Status | `target.valid` | bool | Comprehensive check: exists, enemy, alive, in combat (PvE). | `target.valid` |
| Status | `target.boss` | bool | Target is a boss. | `target.boss` |
| Status | `target.combat` | bool | Target is in combat (extended check). | `target.combat` |
| Status | `target.los` | bool | Target is in line of sight. | `target.los` |
| Status | `target.moving` | bool | Target is moving. | `target.moving` |
| Status | `target.tank` | bool | Target role is tank. | `target.tank` |
| Status | `target.healer` | bool | Target role is healer. | `target.healer` |
| Status | `target.dps` | bool | Target role is DPS. | `target.dps` |
| Status | `target.classification` | number | Unit classification (minus/trivial/normal/rare/elite/rareelite/worldboss). | `target.classification>=3` |
| Status | `target.threat` | number | Threat level (0-3, -1 if none). | `target.threat>=2` |
| Status | `target.quest_mob` | bool | Target is a quest mob. | `target.quest_mob` |
| Status | `target.npcid` | number | NPC ID from GUID. | `target.npcid=12345` |
| Status | `target.targeting_party` | bool | Target is targeting a party/raid member. | `target.targeting_party` |
| Range & TTD | `target.range` | number | EDGE distance in yards: center distance minus both units' combat reach. Correct for spell yard gates — the server likewise adds both reaches to a spell's max range. NOT usable as a melee test (see target.in_melee), and NOT usable for AoE radii or geometry (see target.distance): it is not a metric and clamps at 0. | `target.range<=30` |
| Range & TTD | `target.distance` | number | CENTER distance in yards — no reach subtracted, no clamp. This is the space AoE radii and boss mechanics are measured in, and the only one valid for geometry or clustering. target.distance minus target.range always equals the two combat reaches summed. | `target.distance<=8` |
| Range & TTD | `target.in_melee` | bool | True when the target is in melee range, computed as the client does: CENTER distance <= max(reachA + reachB + 4/3, 5.0), plus 1.0 when either unit carries the melee-range flag. Use this instead of comparing target.range to a constant. | `target.in_melee` |
| Range & TTD | `target.melee_gap` | number | Yards still to close before reaching melee: exactly 0 while in melee, positive when short of it, never negative. This is how to express 'N yards away from melee', and it is size-invariant — at max melee target.range reads 4.5 on a small mob but 2.33 on a 9-reach boss, while melee_gap reads 0 on both. | `target.melee_gap>=2` |
| Range & TTD | `target.time_to_die` | number | Estimated seconds until target dies. | `target.time_to_die>15` |
| Casting | `target.casting` | bool | Target is casting. | `target.casting` |
| Casting | `target.channeling` | bool | Target is channeling. | `target.channeling` |
| Casting | `target.casting.spell_id` | number | Spell ID being cast. | `target.casting.spell_id` |
| Casting | `target.casting.remains` | number | Milliseconds remaining on cast. | `target.casting.remains<2000` |
| Casting | `target.casting.elapsed` | number | Milliseconds into cast. | `target.casting.elapsed` |
| Casting | `target.casting.interruptible` | bool | Cast can be interrupted. | `target.casting.interruptible` |
| Casting | `target.casting.important` | bool | Cast is marked as important (uninterruptible). | `target.casting.important` |
| Casting | `target.casting.targeting_me` | bool | Cast targets the player. | `target.casting.targeting_me` |
| Casting | `target.casting.SPELL` | bool | Target is casting a specific spell (dynamic). | `target.casting.death_bolt` |
| Dispels (Target) | `target.has_stealable` | bool | Target has a stealable buff. | `target.has_stealable` |
| Dispels (Target) | `target.has_magic_buff` | bool | Target has a magic buff. | `target.has_magic_buff` |
| Dispels (Target) | `target.has_enrage` | bool | Target has an enrage buff. | `target.has_enrage` |
| Dispels (Target) | `target.purgeable` | bool | Target has any purgeable buff (auto-detect). | `target.purgeable` |
| Dispels (Target) | `target.purgeable.list` | bool | Purgeable with dispel_list filtering. | `target.purgeable.list` |
| Dispels (Target) | `target.purgeable.magic` | bool | Target has purgeable magic buff. | `target.purgeable.magic` |
| Dispels (Target) | `target.purgeable.enrage` | bool | Target has purgeable enrage buff. | `target.purgeable.enrage` |
| Dispels (Target) | `target.dispelable.SPELL` | bool | Target has buff dispelable by SPELL. | `target.dispelable.spellsteal` |
| NPC Data | `target.bypass_combat` | bool | NPC should bypass combat requirements (from _npcdata.yaml). | `target.bypass_combat` |
| NPC Data | `target.should_stun` | bool | NPC should be stunned (from _npcdata.yaml). | `target.should_stun` |
| NPC Data | `target.should_slow` | bool | NPC should be slowed (from _npcdata.yaml). | `target.should_slow` |

### 11.11 Focus — `focus.PROPERTY`
Propriedades do alvo em foco. Possui as mesmas propriedades de Target.

**Total de Expressões:** 36

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Health & Status | `focus.exists` | bool | Focus target exists. | `focus.exists` |
| Health & Status | `focus.alive` | bool | Focus target is alive. | `focus.alive` |
| Health & Status | `focus.dead` | bool | Focus target is dead. | `focus.dead` |
| Health & Status | `focus.health.pct` | number | Focus health percentage. | `focus.health.pct<50` |
| Health & Status | `focus.health.current` | number | Focus current health. | `focus.health.current` |
| Health & Status | `focus.health.deficit` | number | Focus missing health. | `focus.health.deficit` |
| Health & Status | `focus.health.effective.pct` | number | Focus effective healable health %. |  |
| Health & Status | `focus.absorb` | number | Focus damage absorb shield amount. |  |
| Health & Status | `focus.absorb.pct` | number | Focus damage absorb as % of max health. |  |
| Health & Status | `focus.heal_absorb` | number | Focus heal absorb amount. |  |
| Health & Status | `focus.heal_absorb.pct` | number | Focus heal absorb as % of max health. |  |
| Health & Status | `focus.incoming_heals` | number | Focus total incoming heals. |  |
| Health & Status | `focus.incoming_heals.pct` | number | Focus incoming heals as % of max health. |  |
| Health & Status | `focus.enemy` | bool | Focus is an enemy. | `focus.enemy` |
| Health & Status | `focus.friendly` | bool | Focus is friendly. | `focus.friendly` |
| Health & Status | `focus.attackable` | bool | Focus is attackable. | `focus.attackable` |
| Health & Status | `focus.valid` | bool | Comprehensive validation. | `focus.valid` |
| Health & Status | `focus.range` | number | EDGE distance to focus in yards (both combat reaches subtracted). For spell range gates. | `focus.range<=40` |
| Health & Status | `focus.distance` | number | CENTER distance to focus in yards. For AoE radii and geometry. | `focus.distance<=8` |
| Health & Status | `focus.los` | bool | Focus is in line of sight. | `focus.los` |
| Health & Status | `focus.time_to_die` | number | Estimated TTD. | `focus.time_to_die>10` |
| Health & Status | `focus.moving` | bool | Focus is moving. | `focus.moving` |
| Health & Status | `focus.tank` | bool | Focus role is tank. | `focus.tank` |
| Health & Status | `focus.healer` | bool | Focus role is healer. | `focus.healer` |
| Health & Status | `focus.dps` | bool | Focus role is DPS. | `focus.dps` |
| Health & Status | `focus.boss` | bool | Focus is a boss. | `focus.boss` |
| Health & Status | `focus.combat` | bool | Focus is in combat. | `focus.combat` |
| Health & Status | `focus.npcid` | number | NPC ID. | `focus.npcid` |
| Casting | `focus.casting` | bool | Focus is casting. | `focus.casting` |
| Casting | `focus.channeling` | bool | Focus is channeling. | `focus.channeling` |
| Casting | `focus.casting.spell_id` | number | Spell ID being cast. | `focus.casting.spell_id` |
| Casting | `focus.casting.remains` | number | Cast time remaining (ms). | `focus.casting.remains` |
| Casting | `focus.casting.interruptible` | bool | Cast is interruptible. | `focus.casting.interruptible` |
| Casting | `focus.casting.important` | bool | Cast is important. | `focus.casting.important` |
| Casting | `focus.casting.targeting_me` | bool | Cast targets the player. | `focus.casting.targeting_me` |
| Casting | `focus.casting.SPELL` | bool | Focus is casting specific spell. | `focus.casting.death_bolt` |

### 11.12 Mouseover — `mouseover.PROPERTY`
Propriedades da unidade sob o cursor. Possui as mesmas propriedades de Target.

**Total de Expressões:** 34

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Health & Status | `mouseover.exists` | bool | Mouseover target exists. | `mouseover.exists` |
| Health & Status | `mouseover.alive` | bool | Mouseover is alive. | `mouseover.alive` |
| Health & Status | `mouseover.dead` | bool | Mouseover is dead. | `mouseover.dead` |
| Health & Status | `mouseover.health.pct` | number | Mouseover health percentage. | `mouseover.health.pct<30` |
| Auras | `mouseover.debuff.SPELL.PROPERTY` | varies | Debuff on the mouseover unit — `.up`, `.down`, `.remains`, `.stack`. Só conta debuffs aplicados por você; some `.any` para qualquer fonte. **Existe e funciona** — usado por `rotation_104` e `rotation_256` de fábrica. Use isto para espalhar DoT por mouseover em vez de proxies de cluster, que olham o pack em volta do SEU ALVO e não a unidade sob o mouse. | `moonfire.mouseover,if=mouseover.debuff.moonfire.down` |
| Auras | `mouseover.buff.SPELL.PROPERTY` | varies | Idem para buffs no mouseover. | `mouseover.buff.ironbark.down` |
| Health & Status | `mouseover.health.current` | number | Mouseover current health. | `mouseover.health.current` |
| Health & Status | `mouseover.health.deficit` | number | Mouseover missing health. | `mouseover.health.deficit` |
| Health & Status | `mouseover.health.effective.pct` | number | Mouseover effective healable health %. |  |
| Health & Status | `mouseover.absorb` | number | Mouseover damage absorb shield amount. |  |
| Health & Status | `mouseover.absorb.pct` | number | Mouseover damage absorb as % of max health. |  |
| Health & Status | `mouseover.heal_absorb` | number | Mouseover heal absorb amount. |  |
| Health & Status | `mouseover.heal_absorb.pct` | number | Mouseover heal absorb as % of max health. |  |
| Health & Status | `mouseover.incoming_heals` | number | Mouseover total incoming heals. |  |
| Health & Status | `mouseover.incoming_heals.pct` | number | Mouseover incoming heals as % of max health. |  |
| Health & Status | `mouseover.enemy` | bool | Mouseover is an enemy. | `mouseover.enemy` |
| Health & Status | `mouseover.friendly` | bool | Mouseover is friendly. | `mouseover.friendly` |
| Health & Status | `mouseover.attackable` | bool | Mouseover is attackable. | `mouseover.attackable` |
| Health & Status | `mouseover.valid` | bool | Comprehensive validation. | `mouseover.valid` |
| Health & Status | `mouseover.range` | number | EDGE distance to mouseover in yards (both combat reaches subtracted). For spell range gates. | `mouseover.range<=40` |
| Health & Status | `mouseover.distance` | number | CENTER distance to mouseover in yards. For AoE radii and geometry. | `mouseover.distance<=8` |
| Health & Status | `mouseover.los` | bool | Mouseover in line of sight. | `mouseover.los` |
| Health & Status | `mouseover.time_to_die` | number | Estimated TTD. | `mouseover.time_to_die>5` |
| Health & Status | `mouseover.moving` | bool | Mouseover is moving. | `mouseover.moving` |
| Health & Status | `mouseover.tank` | bool | Mouseover role is tank. | `mouseover.tank` |
| Health & Status | `mouseover.healer` | bool | Mouseover role is healer. | `mouseover.healer` |
| Health & Status | `mouseover.dps` | bool | Mouseover role is DPS. | `mouseover.dps` |
| Health & Status | `mouseover.boss` | bool | Mouseover is a boss. | `mouseover.boss` |
| Health & Status | `mouseover.combat` | bool | Mouseover is in combat. | `mouseover.combat` |
| Health & Status | `mouseover.npcid` | number | NPC ID. | `mouseover.npcid` |
| Health & Status | `mouseover.unitframe` | bool | True if the mouseover came from a UI unit frame (party/raid frame), false if from the 3D world. Use to restrict healer spells to unit frames only, preventing accidental casts on world units. Note: the .focus_mouseover cast target already implies unitframe — this is for explicit condition checks. | `riptide.mouseover,if=mouseover.exists&mouseover.unitframe` |
| Casting | `mouseover.casting` | bool | Mouseover is casting. | `mouseover.casting` |
| Casting | `mouseover.channeling` | bool | Mouseover is channeling. | `mouseover.channeling` |
| Casting | `mouseover.casting.interruptible` | bool | Cast is interruptible. | `mouseover.casting.interruptible` |
| Casting | `mouseover.casting.important` | bool | Cast is important. | `mouseover.casting.important` |
| Casting | `mouseover.casting.targeting_me` | bool | Cast targets the player. | `mouseover.casting.targeting_me` |

### 11.13 Pet — `pet.PROPERTY`
Propriedades do pet do jogador.

**Total de Expressões:** 19

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.14 GCD — `gcd[.PROPERTY]`
Propriedades do Cooldown Global (GCD). Ex: `gcd`, `gcd.max`, `gcd.remains`.

**Total de Expressões:** 3

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.15 Encontro & Combate
Informações sobre a quantidade de inimigos ativos ou tempo de luta.

Ex: `active_enemies`, `enemies.8y`, `fight_remains`, `boss_fight`, `combat.time`.

**Total de Expressões:** 22

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `active_enemies` | number | Number of nearby enemies (nameplate count). | `active_enemies>=3` |
| `enemies.Xy` | number | Enemies within X yards (e.g., enemies.8y, enemies.15y). | `enemies.8y>=2` |
| `enemies.combat.Xy` | number | Enemies in combat within X yards. | `enemies.combat.40y>=1` |
| `enemies.around.angle.N` | number | Count of enemies the player is facing within N° max half-angle (\|bearing−facing\| ≤ N). OM world pos + facing required. | `enemies.around.angle.45>=3` |
| `enemies.around.angle.N.Y` | number | Facing cone N° half-angle AND within Y yards edge-to-edge of player. Optional trailing y (e.g. .20y). | `enemies.around.angle.45.20>=3` |
| `enemies.around_target` | number | Enemies clustered near current target (default 8y world center distance). | `enemies.around_target>=3` |
| `enemies.around_target.range.N` | number | Cluster near target with max center distance N yards (1..100). | `enemies.around_target.range.12>=3` |
| `player.facing` | number | Player absolute yaw in radians (OM). Not relative to a peer. | `player.facing` |
| `player.facing.target` | bool | Player faces target. Default ±90° (front hemisphere). Single path: unit.facing.peer[.N]. | `player.facing.target` |
| `player.facing.target.N` | bool | Player faces target with \|bearing−facing\| ≤ N degrees (N=1..180). Same path as bare form. | `player.facing.target.35` |
| `player.facing.focus[.N]` | bool | Player faces focus (default ±90° or .N half-angle). | `player.facing.focus.45` |
| `player.facing.mouseover[.N]` | bool | Player faces mouseover (default ±90° or .N half-angle). | `player.facing.mouseover` |
| `player.facing.pet[.N]` | bool | Player faces pet (default ±90° or .N half-angle). | `player.facing.pet` |
| `target.facing.player[.N]` | bool | Target faces player (default ±90° or .N half-angle). | `target.facing.player.60` |
| `focus.facing.player[.N]` | bool | Focus faces player (default ±90° or .N half-angle). | `focus.facing.player` |
| `mouseover.facing.player[.N]` | bool | Mouseover faces player (default ±90° or .N half-angle). | `mouseover.facing.player` |
| `fight_remains` | number | Estimated seconds until all nameplate enemies die. | `fight_remains>30` |
| `boss_fight` | bool | Any boss unit frame exists. | `boss_fight` |
| `combat.time` | number | Seconds spent in combat. | `combat.time>10` |
| `moving.time` | number | Seconds spent moving. | `moving.time>2` |
| `standing.time` | number | Seconds spent standing still. | `standing.time>1` |
| `boss1.time_to_die` | number | TTD for boss1 unit frame (boss1-boss5). | `boss1.time_to_die>30` |

### 11.16 Referências Determinísticas de Tank — `tankN.PROPERTY`
Acesso a dados de tanques específicos no grupo (N varia de 1 a 3).

**Total de Expressões:** 16

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.17 Linha do Tempo do Encontro — `encounter.SPELL.PROPERTY`
Verifica mecânicas ou habilidades futuras no boss da luta.

**Total de Expressões:** 37

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.18 Cluster (Proximidade) — `cluster.debuff.SPELL.PROPERTY`
Verifica o acúmulo de inimigos próximos ao alvo ou jogador.

**Total de Expressões:** 14

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `enemies.around_target` | number | Count of enemies clustered near current target (default 8y world center). | `enemies.around_target>=3` |
| `enemies.around_target.range.N` | number | Cluster near target with max center distance N yards. | `enemies.around_target.range.12>=3` |
| `cluster.debuff.SPELL.count` | number | Number of cluster enemies with this debuff (player-source only). | `cluster.debuff.rip.count<enemies.around_target` |
| `cluster.debuff.SPELL.count.any` | number | Number of cluster enemies with this debuff (any source). | `cluster.debuff.rip.count.any<3` |
| `cluster.debuff.SPELL.lowest` | number | Lowest remaining duration of debuff among cluster enemies (player-source). | `cluster.debuff.moonfire.lowest<3` |
| `cluster.debuff.SPELL.lowest.any` | number | Lowest remaining duration of debuff among cluster enemies (any source). | `cluster.debuff.moonfire.lowest.any<3` |
| `cluster.debuff.SPELL.highest` | number | Highest remaining duration of debuff among cluster enemies (player-source). | `cluster.debuff.moonfire.highest>10` |
| `cluster.debuff.SPELL.highest.any` | number | Highest remaining duration of debuff among cluster enemies (any source). | `cluster.debuff.moonfire.highest.any>10` |
| `cluster.buff.SPELL.count` | number | Number of cluster enemies with this buff (player-source only). | `cluster.buff.mark_of_the_wild.count>=2` |
| `cluster.buff.SPELL.count.any` | number | Number of cluster enemies with this buff (any source). | `cluster.buff.mark_of_the_wild.count.any>=2` |
| `cluster.buff.SPELL.lowest` | number | Lowest remaining duration of buff among cluster enemies (player-source). | `cluster.buff.curse.lowest<3` |
| `cluster.buff.SPELL.lowest.any` | number | Lowest remaining duration of buff among cluster enemies (any source). | `cluster.buff.curse.lowest.any<3` |
| `cluster.buff.SPELL.highest` | number | Highest remaining duration of buff among cluster enemies (player-source). | `cluster.buff.curse.highest>10` |
| `cluster.buff.SPELL.highest.any` | number | Highest remaining duration of buff among cluster enemies (any source). | `cluster.buff.curse.highest.any>10` |

### 11.19 Histórico de Lançamento (Prev GCD / Last Cast)
Verifica feitiços lançados anteriormente. Ex: `prev_gcd.1.spell`, `lastcast.spell`.

**Total de Expressões:** 4

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.20 DoTs Ativos no Grupo — `active_dot.SPELL`
Contagem de DoTs ativos em todas as nameplates de inimigos.

**Total de Expressões:** 2

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.21 DoT Refreshable Count — `dot_refreshable_count.SPELL`
Quantidade de inimigos com DoTs na janela pandemic para renovação.

**Total de Expressões:** 1

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.22 Usabilidade — `usable.SPELL`
Verifica se o feitiço está disponível para ser lançado (recurso + CD prontos).

**Total de Expressões:** 1

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.23 Distância — `range.SPELL.UNIT`
Verifica se a unidade está no alcance de um feitiço específico.

**Total de Expressões:** 3

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.24 Cycle (Cura) — `cycle.PROPERTY`
Propriedades do membro do grupo atualmente avaliado no cycle de cura.

**Total de Expressões:** 31

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Member Properties | `cycle.health.pct` | number | Cycle member health percentage. | `cycle.health.pct<50` |
| Member Properties | `cycle.health.current` | number | Cycle member current health. | `cycle.health.current` |
| Member Properties | `cycle.health.max` | number | Cycle member max health. | `cycle.health.max` |
| Member Properties | `cycle.health.deficit` | number | Cycle member missing health. | `cycle.health.deficit>50000` |
| Member Properties | `cycle.health.effective.pct` | number | Cycle member effective healable health % (healthPct - healAbsorbPct + incomingHealsPct). | `cycle.health.effective.pct<50` |
| Member Properties | `cycle.absorb` | number | Cycle member damage absorb shield amount. | `cycle.absorb>0` |
| Member Properties | `cycle.absorb.pct` | number | Cycle member damage absorb as % of max health. |  |
| Member Properties | `cycle.heal_absorb` | number | Cycle member heal absorb amount. | `cycle.heal_absorb>0` |
| Member Properties | `cycle.heal_absorb.pct` | number | Cycle member heal absorb as % of max health. |  |
| Member Properties | `cycle.incoming_heals` | number | Cycle member total incoming heals. |  |
| Member Properties | `cycle.incoming_heals.pct` | number | Cycle member incoming heals as % of max health. |  |
| Member Properties | `cycle.range` | number | Distance to cycle member. | `cycle.range<=40` |
| Member Properties | `cycle.tank` | bool | Cycle member role is tank. | `cycle.tank` |
| Member Properties | `cycle.healer` | bool | Cycle member role is healer. | `cycle.healer` |
| Member Properties | `cycle.dps` | bool | Cycle member role is DPS. | `cycle.dps` |
| Member Properties | `cycle.spec_id` | number | Cycle member numeric specialization ID. Use with = or != to check a specific spec. | `cycle.spec_id=1473` |
| Member Properties | `cycle.time_to_die` | number | Estimated TTD of cycle member. | `cycle.time_to_die>5` |
| Auras | `cycle.buff.SPELL.up` | bool | Buff active on cycle member. | `cycle.buff.renew.up` |
| Auras | `cycle.buff.SPELL.down` | bool | Buff NOT active on cycle member. | `cycle.buff.renew.down` |
| Auras | `cycle.buff.SPELL.remains` | number | Buff seconds remaining. | `cycle.buff.renew.remains<3` |
| Auras | `cycle.buff.SPELL.stack` | number | Buff stack count. | `cycle.buff.atonement.stack` |
| Auras | `cycle.buff.SPELL.refreshable` | bool | Buff within pandemic window. | `cycle.buff.renew.refreshable` |
| Auras | `cycle.debuff.SPELL.up` | bool | Debuff active on cycle member. | `cycle.debuff.shadow_word_pain.up` |
| Auras | `cycle.debuff.SPELL.remains` | number | Debuff seconds remaining. | `cycle.debuff.shadow_word_pain.remains` |
| Dispels | `cycle.dispelable` | bool | Cycle member has any dispelable debuff. | `cycle.dispelable` |
| Dispels | `cycle.dispelable.SPELL` | bool | Has debuff dispelable by SPELL. | `cycle.dispelable.purify` |
| Dispels | `cycle.dispelable.magic` | bool | Has magic debuff. | `cycle.dispelable.magic` |
| Dispels | `cycle.dispelable.disease` | bool | Has disease debuff. | `cycle.dispelable.disease` |
| Dispels | `cycle.dispelable.poison` | bool | Has poison debuff. | `cycle.dispelable.poison` |
| Dispels | `cycle.dispelable.curse` | bool | Has curse debuff. | `cycle.dispelable.curse` |
| Dispels | `cycle.dispelable.list.SPELL` | bool | With dispel_list filtering. | `cycle.dispelable.list.purify` |

### 11.25 Grupo (Cura) — `group.SELECTOR.PROPERTY`
Estatísticas agregadas de vida e estados de buffs no grupo.

**Total de Expressões:** 25

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.26 Nameplates — `nameplates.threat/debuff/buff`
Acesso a dados agregados de nameplates em combate.

**Total de Expressões:** 8

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.27 NPC Ativo — `active_npc.NPC_ID.PROPERTY[.any]`
Agrega **todos** os inimigos do pull que carregam um NPC ID específico, sem precisar
que ele seja target/focus/mouseover — varre as nameplates inteiras (ao contrário de
`target.npcid`). `nameplates.npc.NPC_ID.PROPERTY` é alias exato.

> [!NOTE]
> "Ativo" = válido, vivo, inimigo **e** em combate com você ou seu grupo (mesma porta
> que `active_enemies` e `fight_remains` usam). Um pack patrulhando ou a próxima sala
> não conta — use `.any` para remover essa porta (necessário para NPCs que nunca entram
> em combate: geradores de escudo, adds neutros de objetivo).
> A lista de NPCs ignorados **não** é aplicada: citar um NPC ID exato sempre conta.

**Total de Expressões:** 7

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `active_npc.NPC_ID` | bool | At least one live enemy with this NPC ID is engaged with you or your group. Bare form defaults to .up. | `active_npc.260906.up` |
| `active_npc.NPC_ID.count` | number | How many live copies of this NPC ID are engaged. | `active_npc.260906.count>=2` |
| `active_npc.NPC_ID.ttd` | number | Seconds until NO copy remains — i.e. how long .up stays true. Equals .max_ttd. 0 when none is active; 9999 when the copies are taking no damage. | `active_npc.260906.ttd>10` |
| `active_npc.NPC_ID.min_ttd` | number | Seconds until the SOONEST copy dies. 0 when none is active; 9999 when it is taking no damage. | `active_npc.260906.min_ttd<5` |
| `active_npc.NPC_ID.range` | number | EDGE distance in yards to the nearest copy; 999 when none is active. Same metric as target.range. | `active_npc.260906.range<=8` |
| `active_npc.NPC_ID.health.pct` | number | Lowest health percentage across the active copies; 0 when none is active. | `active_npc.260906.health.pct<35` |
| `active_npc.NPC_ID.PROPERTY.any` | number | Same property, but also counts enemies that are not engaged with you or your group. Needed for NPCs that never enter combat (shield generators, neutral objective adds). | `active_npc.260906.up.any` |

### 11.28 Alvo do Lançamento — `[unit.]casting_target.PROPERTY`
Permite verificar dados da unidade que está sendo visada pelo cast atual de um inimigo/aliado.

**Total de Expressões:** 5

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.29 Previsão de Lançamento — `pred.buff/debuff.SPELL.PROPERTY`
Prevê se buffs/debuffs estarão ativos nos últimos 0.3s de um cast ou durante toda a sua duração (no caso de cycle).

**Total de Expressões:** 17

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Player Buff Prediction | `pred.buff.SPELL.up` | bool | Buff is active OR will be active after the current cast completes (≤ 0.3s remaining in cast, then held for max(ping, 100ms)). | `pred.buff.power_word_shield.up` |
| Player Buff Prediction | `pred.buff.SPELL.down` | bool | Buff is NOT active and is NOT predicted to be applied. | `pred.buff.power_word_shield.down` |
| Player Buff Prediction | `pred.buff.SPELL.remains` | number | Remaining seconds; returns 9999 during prediction window. | `pred.buff.power_word_shield.remains>0` |
| Player Buff Prediction | `pred.buff.SPELL.refreshable` | bool | Buff is within pandemic refresh window; returns false (0) during prediction. | `pred.buff.renew.refreshable` |
| Player Buff Prediction | `pred.buff.SPELL.react` | bool | Alias for .up — buff is active or predicted. | `pred.buff.icy_veins.react` |
| Target Debuff Prediction | `pred.debuff.SPELL.up` | bool | Debuff is active on target OR will be after the current cast. | `pred.debuff.shadow_word_pain.up` |
| Target Debuff Prediction | `pred.debuff.SPELL.down` | bool | Debuff is NOT active and NOT predicted. | `pred.debuff.shadow_word_pain.down` |
| Target Debuff Prediction | `pred.debuff.SPELL.remains` | number | Remaining seconds; returns 9999 during prediction window. | `pred.debuff.shadow_word_pain.remains>0` |
| Target Debuff Prediction | `pred.debuff.SPELL.refreshable` | bool | Debuff within pandemic window; returns false (0) during prediction. | `pred.debuff.moonfire.refreshable` |
| Target Debuff Prediction | `pred.debuff.SPELL.react` | bool | Alias for .up — debuff is active or predicted. | `pred.debuff.rip.react` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.buff.SPELL.up` | bool | Cycle member's buff is active OR predicted (cast is targeting this member). Prediction fires for the entire cast duration, not just the last 0.3s. Member is matched by unit ID (press record), focus GUID, or mouseover GUID. | `pred.cycle.buff.renew.up` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.buff.SPELL.down` | bool | Buff is NOT active on cycle member and NOT predicted. | `pred.cycle.buff.renew.down` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.buff.SPELL.remains` | number | Buff remaining on cycle member; returns 9999 during prediction. | `pred.cycle.buff.renew.remains<3` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.buff.SPELL.refreshable` | bool | Buff within pandemic window on cycle member; returns false (0) during prediction. | `pred.cycle.buff.renew.refreshable` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.debuff.SPELL.up` | bool | Cycle member's debuff is active OR predicted. | `pred.cycle.debuff.shadow_word_pain.up` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.debuff.SPELL.down` | bool | Debuff NOT active on cycle member and NOT predicted. | `pred.cycle.debuff.shadow_word_pain.down` |
| Cycle Member Buff/Debuff Prediction | `pred.cycle.debuff.SPELL.remains` | number | Debuff remaining on cycle member; returns 9999 during prediction. | `pred.cycle.debuff.shadow_word_pain.remains>0` |

### 11.30 Totens — `totem.SPELL.PROPERTY`
Propriedades de totens ativos (ex: Xamã).

**Total de Expressões:** 3

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.31 Minions (Invocações Temporárias) — `minion.NPC_ID.PROPERTY`
Guardiões/invocações temporárias que você possui, rastreados pelo registro de entidades
do cliente. Chaveados por **NPC id**, não por spell id. Separados de `pet.*` (o pet
permanente) e de `totem.*` (slots de totem).

> [!WARNING]
> Não existe `.remains` nativo: o cliente não guarda tempo de vida de guardião. O tempo
> restante é declarado como `(duration - elapsed)` via alias no `_common.yaml`.
> Prefira `.elapsed` para qualquer invocação cuja duração possa ser estendida em combate.

NPC ids conhecidos: `27829` Ebon Gargoyle (25s) · `237409` ghoul do Army of the Dead (30s)
· `163366` Magus of the Dead (15s) · `264321` Lord of the Dead (15s) · `221632-221635`
os quatro Riders (10s) · `26125` pet permanente do DK (GUID de Pet, tipo 10 — guardiões
são tipo 8, Creature).

O `_common.yaml` fornece aliases amigáveis: `minion.gargoyle.remains`,
`minion.army_ghoul.remains(.remains_min)`, `minion.magus.remains(.remains_min)`,
`minion.lord_of_the_dead.remains`, além das formas `pet.<nome>.active`.
Só os NPC ids realmente referenciados por uma rotação são coletados em parse time.

**Total de Expressões:** 5

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `minion.NPC_ID.up` | bool | We currently own at least one of this summon. | `minion.27829.up` |
| `minion.NPC_ID.down` | bool | We own none of this summon. | `minion.264321.down` |
| `minion.NPC_ID.count` | number | How many we own. Army of the Dead's 8 ghouls count as 8. | `minion.237409.count>=6` |
| `minion.NPC_ID.elapsed` | number | Seconds since the NEWEST one appeared. Returns 0 if it was already alive when the client attached, since its age is unknowable. Prefer this over a declared .remains for anything whose lifetime can be extended in combat. | `minion.27829.elapsed>20` |
| `minion.NPC_ID.max_elapsed` | number | Seconds since the OLDEST one appeared — the first of a group to expire. Backs the .remains_min aliases. | `minion.237409.max_elapsed>25` |

### 11.32 Equipamento & Berloques — `trinket_N.ready/cd/sync`
Verifica CDs de berloques, conjuntos de itens (sets) e itens ativáveis.

**Total de Expressões:** 32

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.33 Consumíveis — `healthstone.ready`
Verifica cooldowns de poções de mana/cura, pedras de vida e runas.

**Total de Expressões:** 10

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.34 Casts Inimigos & Listas de Auras — `incoming_cast.tags`
Acesso rápido a casts inimigos classificados (_casts.yaml) e auras prioritárias (_aura.yaml).

**Total de Expressões:** 47

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.35 Previsão de Dano Recebido — `incoming.pct/amount/remains`
Expressões para mitigação preditiva de dano em combate baseadas na gravidade de golpes iminentes.

**Total de Expressões:** 9

| Grupo | Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- | --- |
| Aggregate (biggest predicted hit) | `incoming.pct` | number | Biggest predicted incoming hit as % of effective health (health + absorb). | `if=incoming.pct>=config.barkskin_dmg_pct` |
| Aggregate (biggest predicted hit) | `incoming.amount` | number | Raw (key-scaled) damage of the biggest predicted hit. | `if=incoming.amount>500000` |
| Aggregate (biggest predicted hit) | `incoming.remains` | number | Seconds until the biggest predicted hit lands (0 for an active DoT). | `if=incoming.remains<0.5` |
| Mitigated (after my active defensives) | `incoming.mitigated.pct` | number | Biggest predicted hit as % of effective health AFTER applying my active defensives. | `if=incoming.mitigated.pct>=40` |
| Mitigated (after my active defensives) | `incoming.mitigated.amount` | number | Predicted hit damage after my active defensives' damage reduction. | `if=incoming.mitigated.amount>500000` |
| Per-spell | `incoming.<SPELL_ID>.pct` | number | Predicted hit from one specific spell as % of effective health. | `if=incoming.450289.pct>=80` |
| Per-spell | `incoming.<SPELL_ID>.amount` | number | Raw key-scaled damage of one specific spell's predicted hit. | `if=incoming.450289.amount>800000` |
| Per-spell | `incoming.<SPELL_ID>.remains` | number | Seconds until one specific spell's predicted hit lands. | `if=incoming.450289.remains<1` |
| Per-spell | `incoming.<SPELL_ID>.mitigated.pct` | number | One specific spell's predicted hit as % of effective health after my active defensives. | `if=incoming.450289.mitigated.pct>=80` |

### 11.36 Variáveis — `var.NAME` ou `cfg.NAME`
Acesso a valores configurados no painel ou expressões nomeadas customizadas.

**Total de Expressões:** 2

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.37 Interação Suave — `softinteract.PROPERTY`
Propriedades da unidade alvo de interação suave (soft interact) da interface do WoW.

**Total de Expressões:** 6

| Propriedade / Sintaxe | Tipo Retornado | Descrição | Exemplo |
| --- | --- | --- | --- |
| `softinteract.exists` | bool | Soft interact target exists. | `softinteract.exists` |
| `softinteract.dead` | bool | Soft interact target is dead. | `softinteract.dead` |
| `softinteract.lootable` | bool | Soft interact target is lootable. | `softinteract.lootable` |
| `softinteract.health.pct` | number | Health percentage. | `softinteract.health.pct` |
| `softinteract.npcid` | number | NPC ID. | `softinteract.npcid` |
| `softinteract.guid` | number | GUID. | `softinteract.guid` |

### 11.38 Assistente de Um Botão — `one_button_assistant.SPELL`
Verifica recomendações e temporizadores do assistente de botão único.

**Total de Expressões:** 2

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.

### 11.39 Estado do Sistema — `state.PROPERTY`
Verifica se a rotação, aoe ou cooldowns estão habilitados na interface do Simia.

**Total de Expressões:** 4

Consulte o arquivo [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para a listagem detalhada de todas as propriedades desta categoria.


> [!TIP]
> Consulte o catálogo JSON completo em [expression-catalog.json](file:///c:/Games/Python/Rotations/expression-catalog.json) para todas as 634 expressões com exemplos detalhados de uso.

---

## 12. Expressões Não Catalogadas

O `expression-catalog.json` declara **634** expressões, e a seção 11 documenta essas.
Mas as rotações oficiais e compartilhadas do próprio Simia usam mais do que isso.

A tabela abaixo saiu de uma varredura do `simia_data_dump/` (dump de 2026-08-30,
112 arquivos) atrás de expressões **estruturais** — as de vocabulário fixo, como
`player.*`, `enemies.*`, `group.*`, `interrupt.*` — que não aparecem nem no
catálogo nem no restante deste documento. Formas parametrizadas por magia
(`buff.QUALQUER_COISA.up`) foram descartadas: são o padrão genérico, não
expressões novas.

**A conclusão prática: uma expressão ausente do catálogo NÃO é prova de que ela
seja inválida.** As rotações oficiais em `simia_data_dump/rotation_*.yaml` e os
arquivos `_shared.yaml` / `_common.yaml` são a especificação de verdade. Quando
o catálogo e o dump discordarem, o dump vence.

A coluna "usos" conta ocorrências no dump inteiro, e é o dado forte aqui: prova
que a expressão existe e é aceita pelo motor.

**As descrições são inferidas** do nome e do contexto em que a expressão aparece,
não de documentação oficial nem de teste em jogo — não existe fonte publicada
para elas. Trate como ponto de partida e confirme com um snapshot antes de
apoiar uma linha importante numa delas. As duas únicas com comportamento
verificado neste repositório são `interrupt.*.check`, usada nas rotações daqui, e
`enemies.40y`, que difere de `enemies.combat.40y` justamente por não filtrar
combate — a distinção que já causou bug neste repo.

| Expressão | Usos | Descrição |
| --- | --- | --- |
| `interrupt.stun.aoe.check` | 211 | Filtro do Simia: vale a pena um stun em AoE agora. |
| `interrupt.cc.check` | 157 | Filtro do Simia para CC (nao-kick). |
| `interrupt.target.check` | 74 | Kick vale a pena no alvo atual (castando, interrompivel, no alcance, ninguem ja kickou). |
| `interrupt.mouseover.check` | 69 | Idem, na unidade sob o mouse. |
| `interrupt.focus.check` | 67 | Idem, no foco. |
| `player.ininstancedpve` | 21 | Dentro de masmorra/raide instanciada. Apareceu no dump de 2026-08-27. |
| `enemies.40y` | 17 | Contagem de inimigos em 40y. SEM o filtro de combate que enemies.combat.40y aplica. |
| `enemies.inrange` | 13 | Inimigos no alcance da habilidade avaliada. |
| `player.solo` | 12 | Sem grupo. |
| `player.group` | 12 | Em grupo. |
| `interrupt.kick.soon` | 8 | Um kick do grupo esta prestes a sair — nao gaste o seu. |
| `group.in_party` | 9 | Voce esta em party (nao raide). |
| `player.inopenworld` | 8 | No mundo aberto. |
| `player.spec_id` | 8 | ID numerico da especializacao. |
| `enemies.8y.count` | 7 | Contagem em 8y, forma explicita com .count. |
| `player.aggro` | 4 | Voce tem aggro de algum inimigo. |
| `enemies.6y` | 4 | Contagem em 6y. |
| `group.healers.lowest.range` | 4 | Distancia do healer mais ferido. |
| `player.reflectable.up` | 3 | Voce carrega algo refletivel. |
| `group.any` | 3 | O grupo tem ao menos um membro. |
| `player.mana.pct` | 3 | Mana em percentual. |
| `enemies.combat.22y` | 3 | Contagem em combate a 22y — o raio arbitrario e aceito. |
| `enemies.5y` | 3 | Contagem em 5y. |
| `player.class_id` | 3 | ID numerico da classe. |
| `enemies.combat.any` | 2 | Existe ao menos um inimigo em combate. |
| `interrupt.8y.any` | 2 | Existe algo interrompivel em 8y. |
| `player.dispelable.magic` | 2 | Voce tem debuff magico dispelavel. |
| `player.exists` | 0 | Sanidade: a unidade jogador existe. **Zerou** no dump de 2026-08-30 (tinha 2 em 27/08) — o arquivo que a usava mudou. Sem uso vivo, não é mais evidência de nada. |
| `player.meld.up` | 2 | Shadowmeld ativo. |
| `enemies.near` | 0 | Inimigos proximos. **Zerou** no dump de 2026-08-30 (tinha 2 em 27/08). Prefira o raio explícito (`enemies.combat.8y`). |
| `group.dps.lowest.range` | 1 | Distancia do dps mais ferido. |
| `enemies.around.angle.90.4` | 1 | Inimigos num cone de 90 graus, 4 unidades. |
| `player.race` | 1 | Raca do personagem. |
| `group.tank.health.pct` | 1 | Vida do tank. |
| `player.dispelable.purify_disease` | 1 | Doenca dispelavel por Purify Disease. |
| `player.threat` | 1 | Nivel de ameaca. |
| `player.dispelable.fear` | 1 | Debuff de medo dispelavel. |
| `player.dispelable.sleep` | 1 | Debuff de sono dispelavel. |
| `player.dispelable.charm` | 1 | Debuff de charm dispelavel. |
| `group.moving_count` | 1 | Quantos membros estao se movendo. |
| `player.blockable.up` | 1 | Voce carrega algo bloqueavel. |
| `player.hp` | 1 | Vida (usado em _trinkets.yaml). |
| `group.count` | 385 | Tamanho do grupo. **A expressão mais usada de todo o dump** que não está no catálogo — aparece em `_common.yaml` e em quase toda rotação da comunidade. |
| `player.dispelable.list` | 29 | Você tem um debuff que a SUA lista de dispel cobre. Usada pelas rotações deste repo no dispel de si mesmo. |
| `interrupt.stun.focus.check` | 9 | Variante de foco do filtro de stun. O catálogo só traz `interrupt.stun.aoe.check`; as três variantes por unidade abaixo existem igual. |
| `interrupt.stun.mouseover.check` | 9 | Idem, na unidade sob o mouse. |
| `interrupt.stun.target.check` | 7 | Idem, no alvo atual. |
| `player.debuff.snare.up` | 8 | Você está com slow. **Toda ocorrência no dump vem dos arquivos deste repo** — não é evidência independente. Ver aviso abaixo. |
| `player.health` | 7 | Vida bruta (não percentual). Aparece em `_aura.yaml`. |
| `player.debuff.root.up` | 6 | Você está enraizado. Mesmo aviso de `player.debuff.snare.up`. |
| `group.lowest.buff.remains` | 5 | Duração restante do buff no membro mais ferido. |
| `player.channeling.remains` | 4 | Segundos restantes da própria canalização. |
| `player.dispelable.list.fireblood` | 3 | Debuff dispelável especificamente pelo racial Fireblood. A forma `player.dispelable.list.RACIAL` filtra pelos tipos que aquele racial limpa. |
| `group.under_pct_50` | 2 | Quantos membros do grupo estão abaixo de 50% de vida. Família completa vista em `rotation_256.yaml` (**rotação oficial**): `_30`, `_50`, `_75`, `_80`, `_85`, `_90`. O limiar faz parte do nome — não é parametrizável livremente. |
| `group.lowest` | 1 | O membro mais ferido, usado como prefixo de unidade. |
| `group.lowest.dispelable.purify_disease` | 1 | O membro mais ferido tem doença dispelável. |
| `player.dispelable.list.stoneform` | 1 | Idem `fireblood`, para o racial Stoneform. |

### Aviso: as suas próprias rotações não são evidência

O `simia_data_dump/` inclui as rotações da comunidade, e as rotações **deste
repositório estão publicadas lá** (`community_Balance_Druid_Ferraz_M_`,
`community_Guardian_Druid_Ferraz_M_`, etc.). Uma contagem de usos que venha só
desses arquivos não prova nada: é o próprio repo se citando.

Isso vale hoje para `player.debuff.root.up` e `player.debuff.snare.up`, que
sustentam o Root Cleanse das rotações de druida. As duas seguem **não
verificadas em jogo** — o teste é um `/simia snapshot` enraizado.

A varredura também achou `community_Ferraz_Guardian_Druid_M___Elunes_.yaml`: um
fork da Guardian daqui, por outro autor. Ele usa `target_if=` e monta o
`tank_buster_remains` a partir de encontros nomeados (`encounter.void_slash`,
`encounter.bone_hack`, `encounter.rampage`) em vez do genérico
`encounter.next_tank`. Não é fonte oficial, mas mostra que a abordagem por
encontro nomeado é usada por gente que joga o spec.

### Formas de prefixo e parametrizadas

Estas não entram na tabela por não serem vocabulário fixo, mas aparecem no dump
e são aceitas:

- **`player.` como prefixo redundante:** `player.buff.X.up`, `player.buff.X.stacks`,
  `player.buff.X.remains`, `player.debuff.X.up` funcionam igual às formas sem
  prefixo. `_common.yaml` usa as duas.
- **`player.casting.SPELL`:** você está lançando aquele feitiço específico.
  `rotation_63.yaml` (oficial) usa `player.casting.fireball`,
  `.pyroblast`, `.flamestrike`, `.scorch`; `community_Unknown.yaml` usa o id
  numérico (`player.casting.19434`). Ou seja, aceita nome e id.
- **`player.debuff.ID.up.any`:** `_shared.yaml` usa `player.debuff.440313.up.any`
  para o afixo Devouring Rift.

Uma ocorrência é erro de digitação e não expressão: `player.player.moving`, em
`community_Vengeance.yaml`.

### 12.1 Novidades do dump de 2026-08-27

O dump anterior era de 2026-08-23. Três coisas novas que mudam o que dá para
escrever numa rotação:

**`player.ininstancedpve`** — dentro de masmorra ou raide instanciada. Entrou no
`_shared.yaml` para separar o comportamento de interrupção: dentro de PvE
instanciado o Death Grip só é gasto em cast marcado `stunnable`, nunca como kick
de reserva num cast `kickable` de boss ou trash; no mundo aberto ele volta a
poder cobrir os dois.

**`check_burst`** em `_trinkets.yaml` (versão 7 → 8) — campo novo por trinket,
marcando os que devem ser sincronizados com a janela de burst em vez de usados
na cooldown.

**Tag `no_heal`** em `_aura.yaml` — remove o alvo da lista de candidatos a cura
enquanto a aura durar. Criada para Siphoning Infection (1295224 / 1295380) na
raide da Midnight temporada 2, onde a cura chega a zero por absorção mais
redução de 100%.

Também entraram tags `freedom` e `stunnable` em vários casts de masmorra,
derivadas de logs de chave 14/15 — ou seja, a lista de "o que shapeshift/Freedom
remove" e "o que dá para parar com stun" cresceu sem que nenhuma expressão
mudasse.
