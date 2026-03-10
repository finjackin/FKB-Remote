import os, sys, subprocess, time

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    _WINDOWS = False

from .constants import (
    FKB_DIR, EXE_PATH, EXE_URL, EXE_TAMANHO_ESPERADO,
    UR_PORT, UR_API_URL, UR_EXES,
)


def _barra(pct, tam=40):
    preenchido = int(tam * pct / 100)
    barra      = "█" * preenchido + "░" * (tam - preenchido)
    print(f"\r  [{barra}] {pct:3.0f}%", end="", flush=True)


def _baixar_com_progresso(url, destino):
    """Baixa arquivo exibindo barra de progresso em tempo real."""
    import requests
    headers = {'User-Agent': 'Mozilla/5.0'}
    print("\n  Instalando motor binário...")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30,
                          allow_redirects=True) as r:
            r.raise_for_status()
            total   = int(r.headers.get('content-length', 0))
            baixado = 0
            _barra(0)
            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        baixado += len(chunk)
                        if total:
                            _barra(baixado * 100 / total)
        _barra(100)
        kb = os.path.getsize(destino) // 1024
        print(f"  ✅  ({kb} KB)")
        return True
    except requests.exceptions.ConnectionError:
        print("\n  ❌ Falha: sem conexão com a internet.")
    except requests.exceptions.Timeout:
        print("\n  ❌ Falha: tempo de conexão esgotado.")
    except requests.exceptions.HTTPError as e:
        print(f"\n  ❌ Falha no servidor: {e}")
    except Exception as e:
        print(f"\n  ❌ Erro inesperado: {e}")
    return False


def _bundle_exe():
    """Retorna o caminho do fkb.exe embutido no bundle PyInstaller, ou None."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = os.path.join(meipass, "fkb.exe")
        if os.path.exists(p):
            return p
    return None


def verificar_motor():
    precisa = False
    if not os.path.exists(EXE_PATH):
        precisa = True
    elif os.path.getsize(EXE_PATH) == 0:
        precisa = True
    elif EXE_TAMANHO_ESPERADO > 0:
        atual  = os.path.getsize(EXE_PATH)
        margem = EXE_TAMANHO_ESPERADO * 0.10
        if not (EXE_TAMANHO_ESPERADO - margem <= atual <= EXE_TAMANHO_ESPERADO + margem):
            precisa = True

    if not precisa:
        return False

    # ── perguntar antes de instalar ───────────────────────────
    print()
    print("  ╔" + "═" * 74 + "╗")
    print("  ║" + "  Motor binário — FKB".center(74) + "║")
    print("  ╠" + "═" * 74 + "╣")
    print("  ║" + "                                                                          ║")
    print("  ║  O motor é um componente pequeno que roda em segundo plano e           ║")
    print("  ║  executa os comandos de teclado quando você pressiona um botão          ║")
    print("  ║  no celular. Sem ele o FKB Remote não funciona.                        ║")
    print("  ║                                                                          ║")
    print("  ╠" + "═" * 74 + "╣")
    print("  ║" + "                                                                          ║")
    print("  ║  Deseja instalar o motor agora?   [S] Sim   [N] Não                    ║")
    print("  ║                                                                          ║")
    print("  ╚" + "═" * 74 + "╝")
    print()
    try:
        import msvcrt as _m
        resp = _m.getwch().lower()
    except Exception:
        resp = input().strip().lower()
    if resp != "s":
        print("\n  Motor não instalado. O programa pode não funcionar corretamente.")
        print("  Execute novamente para instalar.")
        import time as _t; _t.sleep(3)
        sys.exit()

    os.makedirs(FKB_DIR, exist_ok=True)

    # ── modo compilado: copiar do bundle ──────────────────────
    embutido = _bundle_exe()
    if embutido:
        import shutil
        print("\n  Instalando motor...")
        _barra(0)
        try:
            shutil.copy2(embutido, EXE_PATH)
            _barra(100)
            kb = os.path.getsize(EXE_PATH) // 1024
            print(f"  ✅  ({kb} KB)")
            return True
        except Exception as e:
            print(f"\n  ❌ Falha ao copiar motor: {e}")
            sys.exit()

    # ── modo script: baixar da internet ───────────────────────
    if not _baixar_com_progresso(EXE_URL, EXE_PATH):
        print("\n  ❌ Falha ao instalar o motor. Verifique sua conexão e tente novamente.")
        sys.exit()
    return True


# ── Unified Remote ────────────────────────────────────────────
def ur_exe():
    for p in UR_EXES:
        if os.path.exists(p):
            return p
    return None


def verificar_ur_instalado():
    if not ur_exe():
        print("\n❌ ERRO: Unified Remote Server não detectado!")
        print("   Instale o Unified Remote antes de usar este programa.\n")
        sys.exit()


def ur_esta_rodando():
    import requests as _req
    try:
        _req.get(f"http://localhost:{UR_PORT}/", timeout=0.5)
        return True
    except Exception:
        return False


def verificar_ur_rodando():
    if ur_esta_rodando():
        return True
    print("\n⚠️  O servidor do Unified Remote não está rodando.")
    print("  Deseja iniciá-lo agora?  [S] Sim   [N] Não")
    print()
    try:
        import msvcrt as _m
        ch = _m.getwch().lower()
    except Exception:
        ch = input().strip().lower()
    if ch == 's':
        exe = ur_exe()
        try:
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("  Iniciando servidor", end="", flush=True)
            for _ in range(15):
                time.sleep(1)
                print(".", end="", flush=True)
                if ur_esta_rodando():
                    print("\n✅ Servidor iniciado com sucesso!")
                    return True
            print("\n⚠️  Servidor demorou para responder. Continuando mesmo assim.")
        except Exception as e:
            print(f"\n❌ Não foi possível iniciar o servidor: {e}")
    return False


def reiniciar_servidor_ur():
    import requests as _req
    try:
        _req.post(UR_API_URL,
                  json={"id": "Unified.ServerManager", "action": "restart"},
                  timeout=3)
    except Exception:
        pass
