# FKB Remote

Transforma seu celular em um **Stream Deck** usando o [Unified Remote](https://www.unifiedremote.com/).

O FKB Remote cria remotes personalizados que disparam teclas "fantasmas" do Windows — teclas que existem no sistema operacional mas que nenhum teclado físico comum possui (F13–F24, vkXX), combinadas com modificadores (Shift, Ctrl, Alt). Como essas teclas não são usadas por nenhum programa ou atalho do sistema, qualquer aplicativo pode recebê-las sem conflito — OBS, Discord, jogos, editores de vídeo, etc.

---

## Como funciona

1. O FKB Remote cria perfis de botões no Unified Remote
2. Cada botão é mapeado para uma combinação de tecla fantasma + modificador
3. Ao pressionar um botão no celular, o Unified Remote envia o comando para o PC
4. O motor FKB executa a tecla no Windows
5. O programa que você configurou para ouvir aquela tecla executa a ação

---

## Pré-requisitos

- Windows 10 ou superior
- [Unified Remote Server](https://www.unifiedremote.com/download) instalado e rodando no PC
- Aplicativo Unified Remote instalado no celular

---

## Download

| Build | Versão | Para quem |
|-------|--------|-----------|
| [fkb-remote.exe](../../releases/latest) | v1.0.0 | Quer só usar, sem instalar Python |
| [Código fonte (.py)](../../releases) | v2.4.0 | Quer modificar ou contribuir |

---

## Instalação

### Executável (.exe) — recomendado

1. Baixe o `fkb-remote.exe` na página de [releases](../../releases/latest)
2. Coloque em qualquer pasta
3. Execute — na primeira abertura o motor será instalado automaticamente

### Script Python (.py)

**Requisitos:**
- Python 3.8 ou superior
- pip

```
pip install requests Pillow
python fkb_remote.py
```

Na primeira execução as dependências e o motor são instalados automaticamente.

---

## Uso

Ao abrir o FKB Remote você verá o menu inicial com seus perfis. A navegação é feita pelo teclado — sem mouse.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  FKB Remote  ·  v1.0.0 (exe)  ·  finjackin              ● Online           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PERFIS  ·  1 de 18                                  342 teclas disponíveis ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   1     meu-perfil     ████████░░░░░░░░   8/24      01/01/2025  12:00      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  AÇÕES                                                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   [C]  Criar              [R]  Renomear        [E]  Excluir                 ║
║   [O]  Configurações                           [S]  Sair                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Criando um perfil

1. Pressione `C` para criar um novo perfil
2. Digite um nome (ou Enter para usar o nome padrão)
3. Dentro do perfil, pressione `1` para adicionar uma tecla
4. Escolha o modificador (Simples, Shift, Ctrl, Alt, etc.)
5. Escolha a tecla base (F13–F24 ou vkXX)
6. Digite um nome para o botão
7. O perfil é criado automaticamente no Unified Remote

### Limites

| Item | Limite |
|------|--------|
| Perfis | 18 |
| Teclas por perfil | 24 |
| Combinações disponíveis | 360 (45 teclas × 8 modificadores) |
| Perfis vazios simultâneos | 2 |

---

## Estrutura do projeto

```
FKB-Remote/
├── fkb_remote.py        ← entry point
└── fkb/
    ├── constants.py     ← constantes e configurações
    ├── ui.py            ← primitivos de interface
    ├── motor.py         ← instalação e controle do motor AHK
    ├── config.py        ← carregar/salvar configuração
    ├── perfil.py        ← geração dos arquivos do remote
    ├── backup.py        ← backup e restauração
    └── menus.py         ← todos os menus
```

---

## Compilando o executável

Requisitos: Python 3.8+, PyInstaller

```
pip install pyinstaller
pyinstaller fkb-remote.spec
```

O executável será gerado em `dist/fkb-remote.exe`.

> **Antes de compilar:** coloque o `fkb.exe` (motor) na raiz do projeto.
> Download: [releases/download/v2.0.0/fkb.exe](../../releases/download/v2.0.0/fkb.exe)

---

## Arquivos gerados

| Arquivo | Localização |
|---------|-------------|
| Configuração | `%APPDATA%\Unified Remote\Custom\FKB\fkb_config.json` |
| Motor | `%APPDATA%\Unified Remote\Custom\FKB\fkb.exe` |
| Perfis | `%PROGRAMDATA%\Unified Remote\Remotes\Custom\FKB-{nome}\` |

---

## Licença

MIT — veja [LICENSE](LICENSE)

---

*finjackin*
