# Changelog — FKB Remote

Todas as mudanças relevantes de cada versão estão documentadas aqui.  
O versionamento segue [Semantic Versioning](https://semver.org/).

---

## [exe] v1.0.0 — Primeira versão estável

> Build compilado com PyInstaller. Motor AHK embutido — não requer internet na primeira execução.

### Adicionado
- Executável único `fkb-remote.exe` — sem necessidade de instalar Python
- Motor AHK (`fkb.exe`) embutido no bundle — instalado offline na primeira execução
- Título da janela do terminal exibe `FKB Remote` em vez do caminho do executável
- Detecção automática de build (`exe` ou `py`) via `sys._MEIPASS`
- Versionamento independente: `VERSION_EXE` e `VERSION_PY` em `constants.py`
- Tela de confirmação antes de instalar o motor com descrição do que ele faz
- Opção `[C] Cancelar` ao definir pasta de destino do backup
- Opção `[2] Remover ícone` no menu de configurações do perfil
- Tela de confirmação dedicada para exclusão de perfil com opção `[B] Backup e excluir`
- Tela de confirmação dedicada para remoção de tecla

### Corrigido
- Navegação sem precisar de Enter em perguntas `[S]/[N]` — usa `msvcrt.getwch()`
- Opções `[5] Desinstalar` e `[6] Testar teclas` estavam trocadas no menu de configurações
- Menções ao `.py` substituídas por `executável` nas mensagens de backup e desinstalação
- Tela de boas-vindas e instalação de dependências suprimidas no build compilado (desnecessárias)

---

## [py] v2.4.0

> Sincronização com o ciclo de desenvolvimento do build exe. Todas as melhorias de UX e correções aplicadas ao exe agora estão disponíveis no script.

### Adicionado
- Versionamento independente: `VERSION_PY` e `VERSION_EXE` em `constants.py`
- Indicador de build `(py)` no cabeçalho de todos os menus
- Opção `[2] Remover ícone` no menu de configurações do perfil
- Opção `[C] Cancelar` ao definir pasta de destino do backup
- Tela de confirmação dedicada para exclusão de perfil com opção `[B] Backup e excluir`
- Tela de confirmação dedicada para remoção de tecla

### Corrigido
- Navegação sem precisar de Enter em perguntas `[S]/[N]` — usa `msvcrt.getwch()`
- Opções `[5] Desinstalar` e `[6] Testar teclas` estavam trocadas no menu de configurações
- Menções ao `.py` atualizadas para linguagem neutra nas mensagens de backup

---

## [py] v2.3.1 — Base do executável

> Última versão estável do script antes do início do desenvolvimento do build exe.

### Adicionado
- Cache TTL de 10 segundos para verificação de status do Unified Remote
- Timeout de `ur_esta_rodando()` reduzido de 2s para 0.5s — navegação mais ágil

---

## [py] v2.3.0 — Redesign completo de UI

### Adicionado
- Breadcrumb em todos os menus — `FKB Remote › perfil › ação`
- Status do Unified Remote no cabeçalho — `● Online` / `○ Offline`
- Barra de progresso por perfil no menu inicial — `████░░░░  8/24`
- Contador global de teclas disponíveis no cabeçalho
- Indicador `⚠ incompleto` para perfis com menos de 6 teclas
- Status persistente da última ação no menu do perfil — `✓ 'nome' adicionada com sucesso`
- Teclas exibidas por extenso — `Ctrl + Alt · F13` em vez de `#{42}`
- Ordenação atual visível no cabeçalho do menu do perfil
- Status do ícone visível no cabeçalho do perfil e nas configurações
- Data formatada como `DD/MM/AAAA HH:MM`
- Destaque `⚠ [tecla · EM USO]` na grade de seleção de tecla
- Ações organizadas em grid por seção em todos os menus
- Legenda `⚠ = perfil incompleto` no rodapé do menu inicial

---

## [py] v2.2.0

### Adicionado
- `MAX_PERFIS_VAZIOS = 2` — máximo de perfis sem nenhuma tecla simultâneos
- `MIN_TECLAS_PERFIL = 6` — mínimo de teclas para perfil não ser considerado vazio
- Limpeza automática de perfis vazios excedentes ao carregar configuração
- Label `[C]` com três estados: `Criar` / `Complete um perfil` / `Limite atingido`

---

## [py] v2.1.2

### Adicionado
- `MAX_TECLAS_POR_PERFIL = 24` — limite de teclas por perfil
- `MAX_PERFIS = 18` — limite de perfis criáveis
- Truncamento automático de perfis com mais de 24 teclas ao carregar
- Bloqueio de criação com mensagem específica por motivo
- Labels dinâmicos: `[1]` vira `Perfil cheio`, `[C]` vira `Limite atingido`

### Corrigido
- Aviso de corrupção exibido indevidamente na primeira execução limpa

---

## [py] v2.1.1

### Corrigido
- `backup.py`: `pasta_py` importada de módulo errado — definida localmente
- `config.py`: aviso de reconstrução exibido na primeira execução sem configuração

---

## [py] v2.1.0 — Modularização

### Adicionado
- Separação em módulos: `constants`, `ui`, `motor`, `config`, `perfil`, `backup`, `menus`
- Entry point `fkb_remote.py` com bootstrap de dependências antes dos imports

---

## [py] v2.0.0 — Versão inicial

### Adicionado
- Script único com interface em caixas Unicode
- Criação, edição, renomeação e exclusão de perfis
- Seleção de teclas com grade de modificadores (8) × teclas base (45) = 360 combinações
- Geração automática de `layout.xml`, `remote.lua` e `meta.prop` para o Unified Remote
- Aplicação de ícone por arquivo local ou URL
- Backup por perfil e backup completo com limpeza automática de backups antigos
- Restauração de backup com opção de criar cópia em caso de conflito
- Teste de teclas em tempo real via servidor HTTP local
- Download automático do motor AHK na primeira execução
- Reinício automático do servidor Unified Remote após alterações
