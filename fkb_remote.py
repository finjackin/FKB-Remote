import os, sys, subprocess

# Título da janela do terminal
if os.name == "nt":
    os.system("title FKB Remote")

# ── BOOTSTRAP (roda antes de qualquer import do pacote fkb) ───
# Precisa ficar aqui: o pacote fkb importa 'requests' e 'PIL' no
# nível de módulo; se o bootstrap estivesse dentro de fkb/, o
# próprio `import fkb` já falharia antes de instalar as deps.

_APPDATA    = os.environ.get('APPDATA', os.path.expanduser('~'))
_FKB_DIR    = os.path.join(_APPDATA, "Unified Remote", "Custom", "FKB")
_FLAG_SETUP = os.path.join(_FKB_DIR, "fkb_setup.flag")
_EXE_PATH   = os.path.join(_FKB_DIR, "fkb.exe")


def _lib_ok(lib):
    import importlib.util
    return importlib.util.find_spec(lib) is not None


def _barra(pct, tam=40):
    preenchido = int(tam * pct / 100)
    barra      = "█" * preenchido + "░" * (tam - preenchido)
    print(f"\r  [{barra}] {pct:3.0f}%", end="", flush=True)


def _instalar_dependencias():
    _LIBS = [('requests', 'requests'), ('PIL', 'Pillow')]
    faltam = [(imp, pkg) for imp, pkg in _LIBS if not _lib_ok(imp)]
    if not faltam:
        return True
    print("\n  Instalando dependências...")
    _barra(0)
    try:
        for i, (_, pkg) in enumerate(faltam, 1):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            _barra(int(100 * i / len(faltam)))
        print("  ✅")
        return True
    except Exception:
        print("\n  ❌ Falha ao instalar dependências. Rode como ADMINISTRADOR.")
        return False


def _verificar_deps_silencioso():
    if _lib_ok('requests') and _lib_ok('PIL'):
        return True
    print("\n  ⚠️  Dependências ausentes. Reinstalando...")
    if not _instalar_dependencias():
        print("  ❌ Não foi possível restaurar as dependências. Rode como ADMINISTRADOR.")
        sys.exit()
    return True


def _primeira_execucao():
    """Tela de boas-vindas apenas na primeira execução (controlada por flag)."""
    # No bundle compilado as deps já estão embutidas — pula instalação
    _compilado = getattr(sys, "_MEIPASS", None) is not None

    if _compilado:
        os.makedirs(_FKB_DIR, exist_ok=True)
        try:
            open(_FLAG_SETUP, 'w').close()
        except Exception:
            pass
        return

    ja_instalado = os.path.exists(_FLAG_SETUP)

    if ja_instalado:
        _verificar_deps_silencioso()
        return

    deps_ok  = _lib_ok('requests') and _lib_ok('PIL')
    motor_ok = os.path.exists(_EXE_PATH)

    print("╔" + "═" * 78 + "╗")
    print("║" + "  FKB Remote — Primeira execução".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print("  Este programa precisa instalar alguns componentes")
    print("  para funcionar corretamente:")
    print()
    if not deps_ok:
        print("  • Dependências — bibliotecas de suporte para")
        print("    comunicação com a internet e processamento")
        print()
    if not motor_ok:
        print("  • Motor binário — componente responsável por")
        print("    executar os comandos")
        print()
    print("  Deseja continuar com a instalação?  [S] Sim   [N] Não")
    print()
    try:
        import msvcrt as _m
        resp = _m.getwch().lower()
    except Exception:
        resp = input().strip().lower()
    if resp != 's':
        print("\n  Instalação necessária para continuar. Encerrando.")
        sys.exit()

    if not deps_ok:
        if not _instalar_dependencias():
            sys.exit()

    os.makedirs(_FKB_DIR, exist_ok=True)
    try:
        open(_FLAG_SETUP, 'w').close()
    except Exception:
        pass


_primeira_execucao()

# ── A partir daqui as deps estão garantidas ───────────────────
from fkb.constants import FKB_DIR, VERSION, W
from fkb.motor     import verificar_ur_instalado, verificar_ur_rodando, verificar_motor
from fkb.config    import carregar_config
from fkb.menus     import menu_inicial

if __name__ == "__main__":
    try:
        verificar_ur_instalado()
        verificar_ur_rodando()
        os.makedirs(FKB_DIR, exist_ok=True)
        motor_instalado = verificar_motor()
        if motor_instalado:
            print("\n  Instalação concluída! Iniciando...\n")
            import time; time.sleep(1)
        cfg = carregar_config()
        menu_inicial(cfg)
    except Exception:
        import traceback
        os.system('cls' if os.name == 'nt' else 'clear')
        print()
        print("=" * W)
        print("  ERRO INESPERADO  —  FKB Remote")
        print("=" * W)
        print()
        traceback.print_exc()
        print()
        print("=" * W)
        print()
        print("  Copie o texto acima e reporte o erro.")
        print()
        print("  Pressione qualquer tecla para sair...")
        try:
            import msvcrt as _m; _m.getch()
        except Exception:
            input()
