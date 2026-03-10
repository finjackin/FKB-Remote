import os, sys, time

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    _WINDOWS = False

from .constants import W


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# ── primitivos de caixa ───────────────────────────────────────
def _box_topo():      print("╔" + "═" * (W - 2) + "╗")
def _box_fim():       print("╚" + "═" * (W - 2) + "╝")
def _box_sep(c="═"):  print("╠" + c * (W - 2) + "╣")
def _box_row(txt=""):  print(f"║{txt:<{W-2}}║")
def _box_br():        print(f"║{'':<{W-2}}║")


class Box:
    """Context manager para caixas Unicode. Garante _box_fim() mesmo em erro.

    Uso:
        with Box("TÍTULO", "subtítulo") as b:
            b.row("  conteúdo")
            b.sep("─")
            b.br()
        # _box_fim() chamado automaticamente ao sair
    """
    def __init__(self, titulo="", sub=""):
        self._titulo = titulo
        self._sub    = sub

    def __enter__(self):
        _box_topo()
        if self._titulo and self._sub:
            _box_row(f"  {self._titulo}  ›  {self._sub}")
        elif self._titulo:
            _box_row(f"  {self._titulo}")
        return self

    def __exit__(self, *_):
        _box_fim()

    def row(self, txt=""): _box_row(txt)
    def sep(self, c="═"):  _box_sep(c)
    def br(self):          _box_br()


# ── mensagens soltas (fora de caixa) ──────────────────────────
def msg_ok(txt):    print(); print(f"  ✓  {txt}")
def msg_info(txt):  print(); print(f"  ·  {txt}")
def msg_aviso(txt): print(); print(f"  ⚠  {txt}")


def pausa_erro(msg):
    print(); print(f"  ✕  {msg}")
    aguardar_ou_timeout(3)


def tecla(prompt="  › "):
    print(prompt, end="", flush=True)
    if _WINDOWS:
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            msvcrt.getwch()
            return ''
        print(ch)
        return ch.lower()
    else:
        return input().strip().lower()


def aguardar_ou_timeout(segundos=3):
    fim = time.time() + segundos
    if _WINDOWS:
        while time.time() < fim:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\r', '\n', ' '):
                    return
            time.sleep(0.05)
    else:
        time.sleep(segundos)


def br():
    print()
