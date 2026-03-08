# Changelog — FKB Remote

Formato: `MAJOR.MINOR.PATCH`
- **MAJOR** → reescrita ou quebra de compatibilidade
- **MINOR** → nova funcionalidade
- **PATCH** → correção de bug ou ajuste pequeno

---

## [2.0.0] — 2026-03-08

### Adicionado
- `class Box` — context manager para caixas Unicode; elimina as chamadas espalhadas de `_box_topo/_box_sep/_box_row/_box_fim` por toda a UI (13 menus convertidos)
- `BACKUP_CONFIG_PATH` — constante para `fkb_config.bak.json`, arquivo de backup automático do config
- `_validar_cfg()` — validação e normalização de schema ao carregar o config; garante que `teclas` é lista, `ordem` é valor válido, cada entrada tem `nome` e `tecla` como strings

### Alterado
- `salvar_config()` — agora faz backup do config atual em `.bak.json` **antes** de sobrescrever; protege contra corrupção por falha na escrita
- `carregar_config()` — sistema de cascata em 3 tentativas:
  1. `fkb_config.json` (normal)
  2. `fkb_config.bak.json` (backup automático) — exibe tela de aviso ao usuário
  3. Reconstrução a partir dos arquivos do disco — exibe tela de aviso detalhada
- `reconstruir_config()` — agora exibe tela clara informando quais perfis foram recuperados e o que foi perdido (datas, ordem de adição, modo de ordenação)

---

## [1.9.5] — 2026-03-08

### Corrigido
- Menu desinstalar: `_lim` recalculado corretamente (`W-18=62`) — antes o path estourava a borda da caixa em nomes de usuário longos

---

## [1.9.4] — 2026-03-08

### Corrigido
- `restaurar_backup`: `payload['perfis']` verificado como `isinstance(dict)` antes de iterar — evitava `TypeError` com backup malformado

---

## [1.9.3] — 2026-03-08

### Corrigido
- `restaurar_backup`: nomes vindos de backups externos passam por `_sanitizar_nome()` antes de criar a pasta do perfil

---

## [1.9.2] — 2026-03-08

### Corrigido
- `menu_teste_teclas`: `HTTPServer` envolvido em `try/except OSError` — porta 9877 ocupada agora exibe erro em vez de matar a thread silenciosamente

---

## [1.9.1] — 2026-03-08

### Corrigido
- `restaurar_backup`: `'dados' in payload` verificado antes do acesso — evitava `KeyError` com backup malformado sem a chave `dados`

---

## [1.9.0] — 2026-03-08

### Corrigido
- `_sanitizar_nome`: `rstrip('.')` adicionado — Windows rejeita pastas com nome terminando em ponto (ex: `'perfil.'` falharia no `os.makedirs`)

---

## [1.8.9] — 2026-03-08

### Corrigido
- Editar tecla: chave em `ordem_adicao` atualizada junto com a nova tecla — antes a entrada perdia sua posição na ordem de adição

---

## [1.8.8] — 2026-03-08

### Corrigido
- `br_print()` removida — função definida mas nunca chamada em lugar algum
- `verificar_ur_rodando`: `.strip()` adicionado antes de `.lower()` no input de confirmação
- `reconstruir_config`: nomes lidos do XML passam por `html.unescape()` — corrige nomes com `&`, `<`, `>`
- `os.rename` no renomear perfil envolvido em `try/except` — evita crash se pasta de destino já existe como órfã

---

## [1.8.7] — 2026-03-08

### Corrigido / Refatorado
- Bootstrap: caixa de boas-vindas corrigida de 82 para 80 chars
- `import tempfile` removido de `salvar_config` — era importado mas nunca usado
- Wrapper `baixar_motor()` de uma linha removido — chamada vai direto para `_baixar_com_progresso()`

---

## [1.8.6] — 2026-03-08

### Adicionado
- `_limpar_backups_completos()` — mantém máximo 3 backups completos, chamada automaticamente após `fazer_backup_tudo`

---

## [1.8.5] — 2026-03-08

### Refatorado
- `TEST_PORT=9877` elevada de variável local para constante global
- Guard redundante de `ordem_adicao` em `reconstruir_perfil` removido
- `Image.LANCZOS` aplicado nos dois `resize` de ícone para melhor qualidade

---

## [1.8.4] — 2026-03-08

### Corrigido
- `reconstruir_perfil`: guard adicionado — `teclas` e `ordem_adicao` garantidas como listas mesmo com JSON corrompido
- `fazer_backup_tudo`: `pausa_erro()` ao falhar (antes usava `print` avulso sem pausa)
- Menu desinstalar: paths longos truncados com `…` para não estourar a borda da caixa

---

## [1.8.3] — 2026-03-08

### Adicionado
- `_sanitizar_nome()` — remove caracteres inválidos para pastas Windows (`\/:*?"<>|`), strip, `rstrip('.')`, `[:20]`; aplicada ao criar e ao renomear perfis; fallback para nome padrão se resultado ficar vazio

---

## [1.8.2] — 2026-03-07

### Corrigido
- Erro de backup agora exibe `pausa_erro()` em vez de sair silenciosamente
- Restart do servidor enviado uma única vez ao restaurar N perfis (antes enviava N vezes)
- `salvar_config` usa escrita atômica via `os.replace` — JSON nunca fica corrompido

---

## [1.8.1] — 2026-03-07

### Corrigido
- Crash: variável `PORT` indefinida no modo teste
- Injeção XML: nomes de botão passam por `_xml_escape()` no `layout.xml`
- `_limpar_backups_antigos` envolvida em `try/except` — não quebra se arquivo estiver bloqueado
- Menu inicial usa `input()` para suportar 10+ perfis com números de dois dígitos

---

## [1.8.0] — 2026-03-07 · redesign visual W=80

### Adicionado / Alterado
- Largura das caixas ampliada de W=64 para **W=80**
- Primitivos `_box_topo/_box_fim/_box_sep/_box_row/_box_br` extraídos como helpers reutilizáveis
- Respiro vertical (`_box_br`) adicionado em todos os menus

---

## [1.7.1] — 2026-03-06

### Corrigido
- Caixa do menu de perfil corrigida após redesign
- `cls()` adicionado no início de todas as ações de menu
- `[C]=cancelar` funciona consistentemente em todos os inputs numéricos

---

## [1.7.0] — 2026-03-06 · redesign visual

### Adicionado
- Redesign visual completo: caixas Unicode `╔═╗║╚═╝` em toda a interface
- Helpers padronizados: `msg_ok (✓)` · `msg_info (·)` · `msg_aviso (⚠)` · `pausa_erro (✕)`
- Largura de caixa padronizada W=64

---

## [1.6.0] — 2026-03-06

### Adicionado
- Preview da ordenação antes de confirmar — exibe lista reordenada para aprovação
- Menu de configurações por perfil: ícone, ordenação e backup agrupados

---

## [1.5.0] — 2026-03-06

### Adicionado
- Backup de todos os perfis de uma vez em JSON único (backup completo)
- Restauração de backup completo ou individual a partir do mesmo fluxo
- Ao restaurar nome existente: escolha entre Substituir, Criar cópia ou Cancelar
- Restart do servidor enviado uma única vez ao restaurar múltiplos perfis

---

## [1.4.0] — 2026-03-06

### Adicionado
- Servidor HTTP de teste na porta 9877 — exibe teclas pressionadas no celular em tempo real
- `fkb_test.flag` criado ao entrar no modo teste e apagado ao sair
- `fkb.ahk` atualizado: envia POST para o servidor de teste quando o flag estiver presente
- `[V]` sem Enter para sair do modo teste

---

## [1.3.2] — 2026-03-06

### Alterado
- "Adicionar outra tecla" volta direto para o mesmo modificador aberto
- Numeração 1–45 nos menus de adição; número global (1–360) só aparece na confirmação e na lista do perfil

---

## [1.3.1] — 2026-03-06

### Adicionado
- Desinstalação exibe barra de progresso em tempo real por pasta
- "Pressione qualquer tecla para sair" ao final da desinstalação

---

## [1.3.0] — 2026-03-06

### Adicionado
- Tela de boas-vindas na primeira execução com descrição dos componentes e confirmação
- Barra de progresso para instalação de dependências pip e para download do motor
- Programa renomeado para **FKB Remote** (Full Keyboard Remote)

---

## [1.2.0] — 2026-03-06

### Adicionado / Alterado
- Campo `ordem_adicao` separado no JSON — preserva sequência original independente do modo de ordenação ativo
- Menu de modificadores expandido para 8 opções fixas: Simples, Shift, Ctrl, Alt, Shift+Ctrl, Shift+Alt, Ctrl+Alt, Shift+Ctrl+Alt
- Numeração global 1–360 exibida na lista de teclas por modificador

---

## [1.1.0] — 2026-03-06

### Adicionado / Alterado
- Layout visual melhorado com caracteres `═ ─ ◈ │`
- "Adicionar outra tecla" volta direto para o mesmo modificador aberto
- Caminho do exe no Lua calculado em tempo de execução
- `[V]` para voltar padronizado em todos os submenus
- Pasta de backup em branco usa pasta do `.py` automaticamente

---

## [1.0.0] — 2026-03-06 · reescrita completa

### Adicionado
- Reescrita completa com sistema de **múltiplos perfis** independentes
- Cada perfil é um remote separado salvo em `ProgramData`
- `fkb_config.json` como controle global — bloqueia teclas entre todos os perfis
- Config corrompido reconstruído automaticamente lendo pastas do disco
- Menu inicial com nome, quantidade de teclas e data de modificação por perfil
- Criação de perfil com nome automático `fkb-1`, `fkb-2`...
- Exclusão de perfil com backup opcional antes de apagar
- Validação de nome duplicado ao criar e renomear
- Ordenação por nome alfabético, código numérico ou ordem de adição
- Editar tecla só salva e reinicia servidor se algo mudou de fato
- Ícone por perfil (arquivo local ou URL)
- Backup com nome automático; máximo 3 por perfil, rotação automática
- UR não instalado: avisa e encerra; UR parado: pergunta se quer iniciar
- Restart automático fire-and-forget após toda modificação

---

## [0.7.0] — 2025-03-05

### Alterado / Removido
- Opção "Limpar todas" removida por ser redundante com Remover
- Histórico de versões movido para `CHANGELOG.txt` separado
- Menu renumerado: Reiniciar=6, Desinstalar=7, Sair=8

---

## [0.6.x] — 2025-03-05

- **0.6.2** — Permanece na lista de teclas ao digitar entrada inválida; removidos todos os `input("Enter para continuar")`
- **0.6.1** — Restart fire-and-forget; opção de reiniciar servidor manualmente
- **0.6.0** — Autobackup antes de remover teclas; data do último backup no menu; função `pedir_indice()` reutilizável

---

## [0.5.x] — 2025-03-05

- **0.5.1** — Restart via API HTTP (`localhost:9510`); restart automático em todas as alterações
- **0.5.0** — Verificação de integridade do `fkb.exe`; sistema de backup/restauração em JSON; validação de formato de imagem

---

## [0.4.x] — 2025-03-05

- **0.4.2** — Instalação de dependências silenciosa; Enter entre menus removido; nome de tecla opcional
- **0.4.1** — Numeração fixa 1–45; teclas em uso marcadas; contador de livres/em uso
- **0.4.0** — EXE_URL corrigido; confirmação `'CONFIRMAR'` na desinstalação; erros de download detalhados

---

## [0.3.5] — original

Versão base recebida para refatoração — script funcional básico de mapeamento de teclas para o Unified Remote.
