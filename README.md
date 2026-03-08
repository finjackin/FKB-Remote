# FKB Remote

Configurador CLI para o plugin **FKB-StreamDeck** do [Unified Remote](https://www.unifiedremote.com/).  
Mapeia teclas especiais do teclado (F13–F24, vk0E–vkFF) para botões no app do celular, funcionando como um Stream Deck improvisado.

> Autoria original do conceito: **finjackin**

---

## O que faz

- Cria e gerencia **perfis** (remotes) no Unified Remote via interface de linha de comando
- Cada perfil mapeia teclas especiais para botões na tela do celular
- Ao pressionar um botão no app, o PC executa a tecla correspondente via AutoHotkey
- **Teclas bloqueadas globalmente** entre perfis — sem conflito

---

## Requisitos

| Componente | Notas |
|---|---|
| Windows 10/11 | Único SO suportado |
| Python 3.8+ | Deve estar no PATH |
| [Unified Remote Server](https://www.unifiedremote.com/download) | Instalado e rodando |
| `fkb.exe` | Baixado automaticamente na primeira execução |

As dependências Python (`requests`, `Pillow`) são instaladas automaticamente.

---

## Como usar

1. Instale o **Unified Remote Server** no PC e o app no celular
2. Execute:
   ```
   python fkb_remote.py
   ```
3. Na primeira execução: confirme a instalação dos componentes
4. Crie um perfil, adicione teclas, abra o remote no app

---

## Estrutura de arquivos gerada

```
AppData\Roaming\Unified Remote\Custom\FKB\
    fkb.exe                  ← motor de execução de teclas (AutoHotkey)
    fkb_config.json          ← controle global de perfis e teclas
    fkb_config.bak.json      ← backup automático do config
    fkb_setup.flag           ← marca que a instalação foi concluída

ProgramData\Unified Remote\Remotes\Custom\
    FKB-NomeDoPerfil\
        meta.prop
        layout.xml
        remote.lua
        icon.png  (opcional)
        tray.png  (opcional)
```

---

## Teclas disponíveis

**360 teclas** no total — 8 grupos de modificadores × 45 teclas cada:

| # | Modificador | Exemplo |
|---|---|---|
| 1 | Simples | `{F13}` |
| 2 | Shift | `+{F13}` |
| 3 | Ctrl | `^{F13}` |
| 4 | Alt | `!{F13}` |
| 5 | Shift+Ctrl | `+^{F13}` |
| 6 | Shift+Alt | `+!{F13}` |
| 7 | Ctrl+Alt | `^!{F13}` |
| 8 | Shift+Ctrl+Alt | `+^!{F13}` |

---

## Funcionalidades

- **Múltiplos perfis** com teclas independentes entre si
- **Ordenação** por nome alfabético, código numérico ou ordem de adição
- **Ícone personalizado** por perfil (arquivo local ou URL)
- **Backup por perfil ou completo** (máximo 3 de cada, rotação automática)
- **Restauração** com escolha entre substituir, criar cópia ou cancelar
- **Modo teste** de teclas em tempo real via celular (porta 9877)
- **Recuperação em cascata**: config principal → backup automático → reconstrução do disco

---

## fkb.ahk / fkb.exe

O motor `fkb.exe` é compilado a partir de `fkb.ahk` (AutoHotkey v2).  
Recebe a tecla como argumento, executa no sistema e, em modo teste, envia um POST para o servidor local na porta 9877.

```
fkb.exe "{F13}"        ← executa F13
fkb.exe "+^{vk1B}"    ← executa Shift+Ctrl+Esc
```

Para recompilar manualmente: instale o [AutoHotkey v2](https://www.autohotkey.com/) e compile `fkb.ahk`.

---

## Roadmap

- [ ] Separação em módulos (`config.py`, `ui.py`, `backup.py`, etc.)
- [ ] Interface gráfica nativa (PyQt6 ou tkinter)
- [ ] Layout visual espelhando a tela do Unified Remote em tempo real
- [ ] Empacotamento como `.exe` standalone via PyInstaller
- [ ] `fkb.exe` embutido no executável final (sem download na primeira execução)

---

## Versão atual

**v2.0.0** — veja [CHANGELOG.md](CHANGELOG.md) para o histórico completo.
