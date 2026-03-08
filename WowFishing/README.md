# 🎣 WoW Fishing Bot

Automação de pesca para World of Warcraft usando análise de pixels.

## Como Funciona

O bot captura capturas de tela da região ao redor da boia em alta frequência (~20fps) e compara frames consecutivos. Quando a boia faz o splash (mexe), a diferença entre frames ultrapassa o limiar configurado e o bot clica com botão direito automaticamente.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

1. Abra o WoW em **Modo Janela** ou **Janela Sem Bordas**.
2. Vá para um local com água e equipe sua vara + isca.
3. Configure a keybind de pesca no arquivo (padrão: `"1"`).
4. Rode o script **como Administrador** (necessário para o `keyboard` funcionar):
   ```bash
   python wow_fisher.py
   ```
5. Quando solicitado, **lance a vara manualmente** e:
   - **Opção 1:** Mova o mouse até a boia — o script vai capturar a posição em 5 segundos.
   - **Opção 2:** Deixe o script tentar detectar a boia pela cor (vermelho/laranja).
6. Pronto! O bot vai pescar automaticamente.

## Parar o Bot

- Pressione **F8** a qualquer momento
- OU mova o mouse rapidamente para o **canto superior esquerdo** da tela (failsafe do pyautogui)
- OU pressione **Ctrl+C** no terminal

## Configurações (`wow_fisher.py`)

| Parâmetro           | Padrão | Descrição                                                  |
|---------------------|--------|------------------------------------------------------------|
| `FISHING_KEY`       | `"1"`  | Keybind da pesca no WoW                                    |
| `STOP_KEY`          | `"F8"` | Tecla para parar o bot                                     |
| `SENSITIVITY`       | `25`   | Sensibilidade (menor = mais sensível ao movimento)         |
| `BOBBER_REGION_SIZE`| `80`   | Tamanho da área monitorada em pixels                       |
| `MAX_WAIT`          | `25`   | Tempo máximo esperando peixe antes de relançar (segundos)  |
| `RECAST_DELAY`      | `1.5`  | Delay após pegar o peixe para relançar (segundos)          |
| `CLICK_DELAY_MS`    | `120`  | Delay entre detectar splash e clicar (ms)                  |

## Dicas de Tunagem

- **Clicando cedo demais / falsos positivos?** → Aumente `SENSITIVITY` (tente 35-45)
- **Não detecta o splash?** → Diminua `SENSITIVITY` (tente 15-20)
- **Perdendo peixes?** → Diminua `CLICK_DELAY_MS`
- **A boia some antes de clicar?** → Diminua `BOBBER_REGION_SIZE` para focar melhor

## Notas

- Execute como **Administrador** para o `keyboard` funcionar corretamente.
- O WoW deve estar em modo **janela** (não tela cheia exclusivo).
- A detecção automática funciona melhor em águas escuras onde a boia vermelha contrasta bem.
