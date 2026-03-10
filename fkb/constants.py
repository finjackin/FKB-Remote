import os

# ── CONFIGURAÇÕES EDITÁVEIS ───────────────────────────────────
EXE_URL              = "https://github.com/finjackin/FKB-Remote/releases/download/v2.0.0/fkb.exe"
UR_PORT              = 9510
EXE_TAMANHO_ESPERADO = 0

# ── VERSÕES ───────────────────────────────────────────────────
# Versionamento independente por build
# py  → script Python puro
# exe → executável compilado (PyInstaller)
import sys as _sys
_COMPILADO   = getattr(_sys, "_MEIPASS", None) is not None
VERSION_PY   = "2.4.0"
VERSION_EXE  = "1.0.0"
VERSION      = VERSION_EXE if _COMPILADO else VERSION_PY
BUILD        = "exe" if _COMPILADO else "py"

# ── CONSTANTES INTERNAS ───────────────────────────────────────
AUTHOR      = "finjackin"
APPDATA     = os.environ.get('APPDATA', os.path.expanduser('~'))
PROGRAMDATA = os.environ.get('PROGRAMDATA', r'C:\ProgramData')
FKB_DIR     = os.path.join(APPDATA, "Unified Remote", "Custom", "FKB")
EXE_PATH    = os.path.join(FKB_DIR, "fkb.exe")
CONFIG_PATH        = os.path.join(FKB_DIR, "fkb_config.json")
BACKUP_CONFIG_PATH = os.path.join(FKB_DIR, "fkb_config.bak.json")
REMOTES_DIR = os.path.join(PROGRAMDATA, "Unified Remote", "Remotes", "Custom")
UR_API_URL  = f"http://localhost:{UR_PORT}/client/request"
UR_EXES     = [
    r"C:\Program Files (x86)\Unified Remote 3\RemoteServerWin.exe",
    r"C:\Program Files (x86)\Unified Remote 3\RemoteServer.exe",
]
TEST_PORT        = 9877
FORMATOS_IMAGEM  = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}
MAX_TECLAS_POR_PERFIL = 24   # limite de teclas por perfil
MAX_PERFIS            = 18   # limite de perfis criáveis
MAX_PERFIS_VAZIOS     =  2   # máximo de perfis sem nenhuma tecla
MIN_TECLAS_PERFIL     =  6   # mínimo de teclas para perfil não ser considerado vazio
ORDEM_ADICAO     = "adicao"
ORDEM_ALFABETICA = "alfabetica"
ORDEM_NUMERICA   = "numerica"

W = 80  # largura das caixas Unicode

TECLAS_BASE = [
    "vk0E","vk0F","vk16","vk1A","vk3A","vk3B","vk3C","vk3D","vk3E","vk3F",
    "vk40","vk88","vk89","vk8A","vk8B","vk8C","vk8D","vk8E","vk8F","vk97",
    "vk98","vk99","vk9A","vk9B","vk9C","vk9D","vk9E","vk9F","vkD8","vkD9",
    "vkDA","vKE8","vkFF","F13","F14","F15","F16","F17","F18","F19","F20",
    "F21","F22","F23","F24",
]

# 8 modificadores fixos — ordem define o bloco para numeração global (1-360)
MODIFICADORES = [
    ("",    "Simples"),
    ("+",   "Shift"),
    ("^",   "Ctrl"),
    ("!",   "Alt"),
    ("+^",  "Shift + Ctrl"),
    ("+!",  "Shift + Alt"),
    ("^!",  "Ctrl + Alt"),
    ("+^!", "Shift + Ctrl + Alt"),
]


def numero_global(tecla_str):
    for bloco, (pref, _) in enumerate(MODIFICADORES):
        if tecla_str.startswith(pref):
            cod = tecla_str[len(pref):].strip("{}")
            if cod in TECLAS_BASE:
                return bloco * 45 + TECLAS_BASE.index(cod) + 1
    return 9999
