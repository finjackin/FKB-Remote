import os, sys, subprocess, shutil, re, time, json, glob, html
from io import BytesIO
try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    _WINDOWS = False

# ── CAMINHOS ANTECIPADOS (necessários antes do resto carregar) ─
_APPDATA     = os.environ.get('APPDATA', os.path.expanduser('~'))
_FKB_DIR     = os.path.join(_APPDATA, "Unified Remote", "Custom", "FKB")
_FLAG_SETUP  = os.path.join(_FKB_DIR, "fkb_setup.flag")
_EXE_PATH    = os.path.join(_FKB_DIR, "fkb.exe")

def _lib_ok(lib):
    """Verifica se lib está instalada usando importlib para evitar cache."""
    import importlib.util
    return importlib.util.find_spec(lib) is not None

def _barra(pct, tam=40):
    preenchido = int(tam * pct / 100)
    barra      = "█" * preenchido + "░" * (tam - preenchido)
    print(f"\r  [{barra}] {pct:3.0f}%", end="", flush=True)

def _instalar_dependencias():
    # Mapeia nome de import para nome do pacote pip
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
    """Verifica deps em execuções normais. Se faltarem, tenta reinstalar sem perguntar."""
    if _lib_ok('requests') and _lib_ok('PIL'):
        return True
    print("\n  ⚠️  Dependências ausentes. Reinstalando...")
    if not _instalar_dependencias():
        print("  ❌ Não foi possível restaurar as dependências. Rode como ADMINISTRADOR.")
        sys.exit()
    return True

def _primeira_execucao():
    """Tela de boas-vindas apenas na primeira execução (controlada por flag)."""
    ja_instalado = os.path.exists(_FLAG_SETUP)

    if ja_instalado:
        # Execuções normais: só verifica deps silenciosamente
        _verificar_deps_silencioso()
        return

    # ── Primeira vez ──────────────────────────────────────────
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
    resp = input("  Deseja continuar com a instalação? (s/n): ").strip().lower()
    if resp != 's':
        print("\n  Instalação necessária para continuar. Encerrando.")
        sys.exit()

    if not deps_ok:
        if not _instalar_dependencias():
            sys.exit()

    # Cria o flag — próximas execuções não mostram essa tela
    os.makedirs(_FKB_DIR, exist_ok=True)
    try:
        open(_FLAG_SETUP, 'w').close()
    except Exception:
        pass

_primeira_execucao()
import requests
from PIL import Image

def _baixar_com_progresso(url, destino):
    """Baixa arquivo exibindo barra de progresso em tempo real."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    print("\n  Instalando motor binário...")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30,
                          allow_redirects=True) as r:
            r.raise_for_status()
            total    = int(r.headers.get('content-length', 0))
            baixado  = 0
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

# ── CONFIGURAÇÕES EDITÁVEIS ───────────────────────────────────
EXE_URL              = "https://github.com/finjackin/FKB-Remote/releases/download/v2.0.0/fkb.exe"
UR_PORT              = 9510
EXE_TAMANHO_ESPERADO = 0

# ── CONSTANTES INTERNAS ───────────────────────────────────────
VERSION     = "2.0.0"
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
ORDEM_ADICAO     = "adicao"
ORDEM_ALFABETICA = "alfabetica"
ORDEM_NUMERICA   = "numerica"
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

# ── UTILITÁRIOS ───────────────────────────────────────────────
W = 80  # largura da caixa

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# ── primitivos de caixa ───────────────────────────────────────
def _box_topo():  print("╔" + "═" * (W - 2) + "╗")
def _box_fim():   print("╚" + "═" * (W - 2) + "╝")
def _box_sep(c="═"): print("╠" + c * (W - 2) + "╣")
def _box_row(txt=""): print(f"║{txt:<{W-2}}║")
def _box_br():    print(f"║{'':<{W-2}}║")


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

def pasta_py():
    return os.path.dirname(os.path.abspath(__file__))

def perfil_dir(nome):
    return os.path.join(REMOTES_DIR, f"FKB-{nome}")

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

def br(): print()  # usado em backup e UR

# ── UNIFIED REMOTE ────────────────────────────────────────────
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
    try:
        requests.get(f"http://localhost:{UR_PORT}/", timeout=2)
        return True
    except Exception:
        return False

def verificar_ur_rodando():
    if ur_esta_rodando():
        return True
    print("\n⚠️  O servidor do Unified Remote não está rodando.")
    if input("  Deseja iniciá-lo agora? (s/n): ").strip().lower() == 's':
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
    try:
        requests.post(UR_API_URL,
                      json={"id": "Unified.ServerManager", "action": "restart"},
                      timeout=3)
    except Exception:
        pass

# ── MOTOR BINÁRIO ─────────────────────────────────────────────
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
    if precisa:
        os.makedirs(FKB_DIR, exist_ok=True)
        if not _baixar_com_progresso(EXE_URL, EXE_PATH):
            print("\n  ❌ Falha ao instalar o motor. Verifique sua conexão e tente novamente.")
            sys.exit()
        return True
    return False

# ── CONFIG GLOBAL ─────────────────────────────────────────────
def config_vazio():
    return {"perfis": {}}

def salvar_config(cfg):
    os.makedirs(FKB_DIR, exist_ok=True)
    # Faz backup do config atual ANTES de sobrescrever — protege contra falha na escrita
    if os.path.exists(CONFIG_PATH):
        try:
            shutil.copy2(CONFIG_PATH, BACKUP_CONFIG_PATH)
        except Exception:
            pass
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    # Renomeia atomicamente — garante que o JSON nunca fica corrompido
    os.replace(tmp, CONFIG_PATH)

def _validar_cfg(cfg):
    """Normaliza e corrige o config garantindo schema correto.
    Retorna cfg com todos os campos obrigatórios presentes e com tipo correto.
    """
    if not isinstance(cfg, dict):
        return config_vazio()
    if not isinstance(cfg.get("perfis"), dict):
        cfg["perfis"] = {}
    ORDENS_VALIDAS = {ORDEM_ALFABETICA, ORDEM_NUMERICA, ORDEM_ADICAO}
    for nome in list(cfg["perfis"].keys()):
        d = cfg["perfis"][nome]
        if not isinstance(d, dict):
            cfg["perfis"][nome] = d = {}
        if not isinstance(d.get("teclas"), list):
            d["teclas"] = []
        else:
            # Garante que cada entrada de tecla é um dict com nome e tecla strings
            d["teclas"] = [
                e for e in d["teclas"]
                if isinstance(e, dict)
                and isinstance(e.get("nome"), str)
                and isinstance(e.get("tecla"), str)
            ]
        if not isinstance(d.get("ordem_adicao"), list):
            d["ordem_adicao"] = list(d["teclas"])
        if d.get("ordem") not in ORDENS_VALIDAS:
            d["ordem"] = ORDEM_ALFABETICA
        if not isinstance(d.get("criado"), str):
            d["criado"] = "desconhecido"
        if not isinstance(d.get("modificado"), str):
            d["modificado"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return cfg

def carregar_config():
    """Carrega config em cascata:
      1. fkb_config.json  (arquivo principal)
      2. fkb_config.bak.json  (backup automático) — avisa o usuário
      3. reconstrução a partir dos arquivos do disco — avisa o usuário
    """
    # ── Tentativa 1: arquivo principal ───────────────────────────
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        return _validar_cfg(cfg)
    except Exception:
        pass

    # ── Tentativa 2: backup automático ───────────────────────────
    try:
        with open(BACKUP_CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        cfg = _validar_cfg(cfg)
        # Notifica o usuário de que o backup foi restaurado
        cls()
        print()
        print("╔" + "═" * (W - 2) + "╗")
        print(f"║{'  ⚠  ATENÇÃO — CONFIGURAÇÃO RESTAURADA':^{W-2}}║")
        print("╠" + "═" * (W - 2) + "╣")
        print(f"║{'':<{W-2}}║")
        print(f"║{'  O arquivo de configuração principal estava corrompido ou':^{W-2}}║")
        print(f"║{'  ausente. O backup automático foi restaurado com sucesso.':^{W-2}}║")
        print(f"║{'':<{W-2}}║")
        print(f"║{'  Se algo parecer diferente, é porque o backup pode estar':^{W-2}}║")
        print(f"║{'  alguns instantes atrás do último estado salvo.':^{W-2}}║")
        print(f"║{'':<{W-2}}║")
        print("╚" + "═" * (W - 2) + "╝")
        print()
        print("  Pressione qualquer tecla para continuar...")
        if _WINDOWS:
            import msvcrt as _m; _m.getch()
        else:
            input()
        # Grava o config restaurado no arquivo principal
        salvar_config(cfg)
        return cfg
    except Exception:
        pass

    # ── Tentativa 3: reconstrução a partir dos arquivos do disco ─
    return reconstruir_config()

def reconstruir_config():
    """Reconstrói config lendo os arquivos do disco (último recurso).
    Recupera: nomes e códigos das teclas.
    Perde: data de criação, ordem de adição, modo de ordenação.
    Exibe aviso claro ao usuário antes de continuar.
    """
    cfg       = config_vazio()
    pastas    = [p for p in glob.glob(os.path.join(REMOTES_DIR, "FKB-*"))
                 if os.path.isdir(p)]
    perfis_ok = []

    for pasta in pastas:
        nome = os.path.basename(pasta).replace("FKB-", "", 1)
        lua  = os.path.join(pasta, "remote.lua")
        xml  = os.path.join(pasta, "layout.xml")
        teclas_cod, nomes_tec = [], []
        if os.path.exists(lua):
            with open(lua, 'r', encoding='utf-8') as f:
                m = re.search(r'local teclas = \{(.*?)\}', f.read(), re.DOTALL)
                if m:
                    teclas_cod = [t.strip().strip('"') for t in m.group(1).split(",") if t.strip()]
        if os.path.exists(xml):
            with open(xml, 'r', encoding='utf-8') as f:
                nomes_tec = [html.unescape(n) for n in re.findall(r'text="(.*?)"', f.read())]
        cfg["perfis"][nome] = {
            "teclas":      [{"nome": n, "tecla": t} for n, t in zip(nomes_tec, teclas_cod)],
            "ordem_adicao":[{"nome": n, "tecla": t} for n, t in zip(nomes_tec, teclas_cod)],
            "ordem":       ORDEM_ALFABETICA,
            "criado":      "desconhecido",
            "modificado":  time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if nomes_tec or teclas_cod:
            perfis_ok.append(f"{nome} ({len(nomes_tec)} tecla(s))")

    salvar_config(cfg)

    # Avisa o usuário sobre o que foi recuperado e o que foi perdido
    cls()
    print()
    print("╔" + "═" * (W - 2) + "╗")
    print(f"║{'  ⚠  ATENÇÃO — CONFIGURAÇÃO RECONSTRUÍDA':^{W-2}}║")
    print("╠" + "═" * (W - 2) + "╣")
    print(f"║{'':<{W-2}}║")
    print(f"║  O arquivo de configuração estava ausente ou corrompido e{'':<{W-2-57}}║")
    print(f"║  não havia backup disponível. Os perfis foram reconstruídos{'':<{W-2-61}}║")
    print(f"║  lendo os arquivos do Unified Remote no disco.{'':<{W-2-47}}║")
    print(f"║{'':<{W-2}}║")
    if perfis_ok:
        print(f"║  Perfis recuperados:{'':<{W-2-20}}║")
        for p in perfis_ok:
            print(f"║    · {p:<{W-8}}║")
    else:
        print(f"║  Nenhum perfil encontrado no disco.{'':<{W-2-36}}║")
    print(f"║{'':<{W-2}}║")
    print(f"║  O que foi PERDIDO (não é possível recuperar):{'':<{W-2-47}}║")
    print(f"║    · Datas de criação dos perfis{'':<{W-2-33}}║")
    print(f"║    · Ordem de adição das teclas{'':<{W-2-32}}║")
    print(f"║    · Modo de ordenação de cada perfil{'':<{W-2-38}}║")
    print(f"║{'':<{W-2}}║")
    print(f"║  Recomendação: faça um backup agora em Configurações.{'':<{W-2-54}}║")
    print(f"║{'':<{W-2}}║")
    print("╚" + "═" * (W - 2) + "╝")
    print()
    print("  Pressione qualquer tecla para continuar...")
    if _WINDOWS:
        import msvcrt as _m; _m.getch()
    else:
        input()
    return cfg

def teclas_em_uso_global(cfg, excluir_perfil=None):
    usadas = set()
    for nome, dados in cfg["perfis"].items():
        if nome == excluir_perfil:
            continue
        for e in dados.get("teclas", []):
            usadas.add(e["tecla"])
    return usadas

def _sanitizar_nome(nome):
    """Remove caracteres inválidos para nomes de pasta no Windows."""
    return re.sub(r'[\\/:*?"<>|]', '', nome).strip().rstrip('.')[:20]

def proximo_nome_padrao(cfg):
    i = 1
    while f"fkb-{i}" in cfg["perfis"]:
        i += 1
    return f"fkb-{i}"

# ── ORDENAÇÃO ─────────────────────────────────────────────────
def ordenar_teclas(entradas, modo, ordem_adicao):
    if modo == ORDEM_ALFABETICA:
        return sorted(entradas, key=lambda e: e["nome"].lower())
    elif modo == ORDEM_NUMERICA:
        return sorted(entradas, key=lambda e: numero_global(e["tecla"]))
    elif modo == ORDEM_ADICAO:
        # Reconstrói pela sequência original de adição
        idx = {e["tecla"]: i for i, e in enumerate(ordem_adicao)}
        return sorted(entradas, key=lambda e: idx.get(e["tecla"], 9999))
    return list(entradas)

# ── ARQUIVOS DO PERFIL ────────────────────────────────────────
def _xml_escape(txt):
    """Escapa caracteres especiais para uso seguro em atributos XML."""
    return (txt.replace("&", "&amp;")
               .replace('"', "&quot;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))

def reconstruir_perfil(nome, cfg, _reiniciar=True):
    dados = cfg["perfis"][nome]
    modo  = dados.get("ordem", ORDEM_ALFABETICA)

    # Garante que teclas é sempre uma lista válida
    if not isinstance(dados.get("teclas"), list):
        dados["teclas"] = []
    if not isinstance(dados.get("ordem_adicao"), list):
        dados["ordem_adicao"] = []

    exibir = ordenar_teclas(dados["teclas"], modo, dados["ordem_adicao"])
    # Atualiza a lista principal com a ordem de exibição correta
    dados["teclas"] = exibir

    dados["modificado"] = time.strftime("%Y-%m-%d %H:%M:%S")
    pasta    = perfil_dir(nome)
    os.makedirs(pasta, exist_ok=True)
    nomes_t  = [e["nome"]  for e in exibir]
    teclas_t = [e["tecla"] for e in exibir]

    xml_c = '<?xml version="1.0" encoding="utf-8"?>\n<layout>\n'
    for i in range(0, len(nomes_t), 3):
        xml_c += '    <row weight="1">\n'
        for j in range(i, min(i + 3, len(nomes_t))):
            xml_c += f'        <button text="{_xml_escape(nomes_t[j])}" ontap="c{j+1}" />\n'
        xml_c += '    </row>\n'
    xml_c += '</layout>'
    with open(os.path.join(pasta, "layout.xml"), 'w', encoding='utf-8') as f:
        f.write(xml_c)

    # Sempre usa EXE_PATH atual, com barras duplas para Lua
    exe_lua = EXE_PATH.replace("\\", "\\\\")
    lua_c = (f'local server = libs.server;\n'
             f'local fkb_path = "{exe_lua}";\n'
             f'local teclas = {{')
    if teclas_t:
        lua_c += '"' + '", "'.join(teclas_t) + '"'
    lua_c += ('}\n\nfor i, tecla in ipairs(teclas) do\n'
              '    actions["c" .. i] = function ()\n'
              '        os.start(fkb_path, tecla);\n'
              '    end\nend')
    with open(os.path.join(pasta, "remote.lua"), 'w', encoding='utf-8') as f:
        f.write(lua_c)

    prop = (f"meta.name: FKB {nome}\nmeta.author: {AUTHOR}\n"
            "meta.description: FKB StreamDeck Profile\n"
            "meta.tags: fkb, streamdeck, teclado")
    with open(os.path.join(pasta, "meta.prop"), 'w', encoding='utf-8') as f:
        f.write(prop)

    salvar_config(cfg)
    if _reiniciar:
        reiniciar_servidor_ur()

# ── BACKUP ────────────────────────────────────────────────────
def pedir_pasta_destino():
    cls()
    br()
    print("  Pasta de destino — arraste ou cole o caminho.")
    print("  Enter em branco = mesma pasta do .py")
    br()
    pasta = input("  › ").strip('"').strip()
    if not pasta:
        return pasta_py()
    if not os.path.isdir(pasta):
        msg_aviso("Pasta inválida. Usando pasta do .py.")
        aguardar_ou_timeout(2)
        return pasta_py()
    return pasta

def fazer_backup_perfil(nome, cfg, pasta_destino):
    ts       = time.strftime("%Y-%m-%d-%Hh%M")
    filename = f"perfil-{nome}-{ts}.json"
    caminho  = os.path.join(pasta_destino, filename)
    payload  = {"versao": VERSION, "perfil": nome, "data": ts, "dados": cfg["perfis"][nome]}
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        msg_ok(f"Backup salvo: {caminho}")
        _limpar_backups_antigos(nome, pasta_destino)
        return True
    except Exception as e:
        pausa_erro(f"Erro ao salvar backup: {e}")
        return False

def _limpar_backups_antigos(nome, pasta):
    backups = sorted(glob.glob(os.path.join(pasta, f"perfil-{nome}-*.json")))
    while len(backups) > 3:
        try: os.remove(backups.pop(0))
        except Exception: pass

def _limpar_backups_completos(pasta):
    backups = sorted(glob.glob(os.path.join(pasta, "fkb-backup-completo-*.json")))
    while len(backups) > 3:
        try: os.remove(backups.pop(0))
        except Exception: pass

def fazer_backup_tudo(cfg, pasta_destino):
    ts       = time.strftime("%Y-%m-%d-%Hh%M")
    caminho  = os.path.join(pasta_destino, f"fkb-backup-completo-{ts}.json")
    payload  = {"versao": VERSION, "data": ts, "perfis": cfg["perfis"]}
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        msg_ok(f"Backup completo salvo: {caminho}")
        _limpar_backups_completos(pasta_destino)
        return True
    except Exception as e:
        pausa_erro(f"Erro ao salvar backup completo: {e}")
        return False

def restaurar_backup(cfg):
    cls()
    br()
    print("  Arraste o arquivo de backup (.json) ou cole o caminho:")
    br()
    caminho = input("  › ").strip('"').strip()
    if not os.path.exists(caminho):
        pausa_erro("Arquivo não encontrado.")
        return cfg
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception:
        pausa_erro("Arquivo inválido ou corrompido.")
        return cfg
    if "perfis" in payload and isinstance(payload["perfis"], dict):
        for nome, dados in payload["perfis"].items():
            cfg = _restaurar_perfil_unico(_sanitizar_nome(nome) or nome[:20], dados, cfg, reiniciar=False)
        reiniciar_servidor_ur()
    elif "perfil" in payload and "dados" in payload:
        cfg = _restaurar_perfil_unico(_sanitizar_nome(payload["perfil"]) or payload["perfil"][:20], payload["dados"], cfg, reiniciar=True)
    else:
        pausa_erro("Formato de backup não reconhecido.")
    return cfg

def _restaurar_perfil_unico(nome, dados, cfg, reiniciar=True):
    if nome in cfg["perfis"]:
        cls()
        br()
        msg_aviso(f"Perfil '{nome}' já existe.")
        br()
        print("  [S] Substituir   [C] Criar como cópia   [V] Cancelar")
        br()
        opt = tecla()
        if opt == "c":
            i = 1
            while f"{nome}-restored-{i}" in cfg["perfis"]:
                i += 1
            nome = f"{nome}-restored-{i}"
            msg_info(f"Será restaurado como '{nome}'.")
        elif opt != "s":
            msg_info("Restauração cancelada.")
            aguardar_ou_timeout(2)
            return cfg
    cfg["perfis"][nome] = dados
    reconstruir_perfil(nome, cfg, _reiniciar=reiniciar)
    msg_ok(f"Perfil '{nome}' restaurado!")
    aguardar_ou_timeout(2)
    return cfg

# ── ÍCONE ─────────────────────────────────────────────────────
def aplicar_icone(nome_perfil):
    pasta    = perfil_dir(nome_perfil)
    formatos = ", ".join(sorted(FORMATOS_IMAGEM))
    cls()
    br()
    print(f"  Formatos: {formatos}")
    print("  Cole um link da web ou arraste um arquivo do PC.")
    br()
    print("  [C] Cancelar")
    br()
    entrada = input("  › ").strip('"').strip()
    if entrada.lower() == "c":
        return

    img = None
    if entrada.lower().startswith("http"):
        try:
            print("  [*] Baixando imagem...")
            r = requests.get(entrada, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
        except Exception as e:
            pausa_erro(f"Erro ao baixar imagem: {e}")
            return
    else:
        if not os.path.exists(entrada):
            pausa_erro("Arquivo não encontrado.")
            return
        ext = os.path.splitext(entrada)[1].lower()
        if ext not in FORMATOS_IMAGEM:
            pausa_erro(f"Formato '{ext}' não suportado.")
            return
        try:
            img = Image.open(entrada)
        except Exception as e:
            pausa_erro(f"Erro ao abrir imagem: {e}")
            return

    try:
        img.resize((512, 510), Image.LANCZOS).save(os.path.join(pasta, "icon.png"))
        img.resize((64, 64), Image.LANCZOS).save(os.path.join(pasta, "tray.png"))
        msg_ok("Ícones salvos!")
        aguardar_ou_timeout(2)
        reiniciar_servidor_ur()
    except Exception as e:
        pausa_erro(f"Erro ao salvar ícones: {e}")

# ── SELEÇÃO DE TECLA ──────────────────────────────────────────
def exibir_teclas_com_status(pref, usadas_global):
    livres  = 0
    celulas = []
    for i, tec in enumerate(TECLAS_BASE, 1):
        em_uso = (pref + "{" + tec + "}") in usadas_global
        marca  = "·uso" if em_uso else "    "
        if not em_uso:
            livres += 1
        celulas.append(f"  {i:>2}. {tec:<6} {marca}")
    col_w = (W - 2) // 3
    for i in range(0, len(celulas), 3):
        grupo   = celulas[i:i+3]
        txt     = "".join(f"{g:<{col_w}}" for g in grupo)
        print(f"║{txt:<{W-2}}║")
    return livres

def _tela_teclas(idx_mod, usadas_global):
    pref, label = MODIFICADORES[idx_mod]
    cls()
    with Box("TECLAS", label) as b:
        b.sep("─")
        b.br()
        livres = exibir_teclas_com_status(pref, usadas_global)
        b.br()
        if livres == 0:
            b.sep()
            b.row("  Todas as teclas deste modificador estão em uso.")
        else:
            b.sep()
            b.br()
            b.row(f"  {livres} livre(s)   ·   {len(TECLAS_BASE) - livres} em uso")
            b.row("  Número (1-45)   ou   [V] Voltar")
            b.br()
    if livres == 0:
        aguardar_ou_timeout(3)
        return None, idx_mod
    print()
    while True:
        raw = input("  › ").strip().lower()
        if raw == "v":
            return None, None
        try:
            num = int(raw) - 1
            if not (0 <= num < len(TECLAS_BASE)):
                raise IndexError
            escolha = pref + "{" + TECLAS_BASE[num] + "}"
            if escolha in usadas_global:
                pausa_erro(f"Tecla '{TECLAS_BASE[num]}' já está em uso.")
                continue
            num_g = idx_mod * 45 + num + 1
            msg_ok(f"Tecla selecionada:  {escolha}   (#{num_g})")
            aguardar_ou_timeout(1)
            return escolha, idx_mod
        except (ValueError, IndexError):
            pausa_erro("Número inválido. Digite entre 1 e 45.")

def configurar_tecla(usadas_global, idx_mod_inicial=None):
    idx_mod = idx_mod_inicial
    while True:
        if idx_mod is None:
            cls()
            with Box("SELECIONAR TECLA", "Modificador") as b:
                b.sep()
                b.br()
                for i, (_, lbl) in enumerate(MODIFICADORES, 1):
                    b.row(f"   [{i}]  {lbl}")
                b.br()
                b.sep()
                b.br()
                b.row("  Número   ou   [V] Voltar")
                b.br()
            print()
            opt = tecla()
            if opt == "v":
                return None, None
            try:
                idx_mod = int(opt) - 1
                if not (0 <= idx_mod < len(MODIFICADORES)):
                    raise IndexError
            except (ValueError, IndexError):
                pausa_erro("Opção inválida.")
                idx_mod = None
                continue
        t_val, _ = _tela_teclas(idx_mod, usadas_global)
        if t_val is not None:
            return t_val, idx_mod
        idx_mod = None

# ── CONFIGURAÇÕES DO PERFIL ───────────────────────────────────
def menu_configuracoes_perfil(nome, cfg):
    while True:
        cls()
        with Box("CONFIG", nome) as b:
            b.sep()
            b.br()
            for k, desc in [("1","Alterar ícone"), ("2","Ordenar teclas"),
                            ("3","Backup deste perfil"), ("V","Voltar")]:
                b.row(f"   [{k}]  {desc}")
            b.br()
        print()
        opt = tecla()

        if opt == "1":
            aplicar_icone(nome)

        elif opt == "2":
            dados_p = cfg["perfis"][nome]
            while True:
                cls()
                with Box("ORDENAR", f"{nome}   ·   atual: {dados_p.get('ordem', ORDEM_ALFABETICA)}") as b:
                    b.sep("─")
                    b.br()
                    for i, e in enumerate(dados_p["teclas"], 1):
                        b.row(f"   {i:>2}.   {e['nome']:<28}  #{numero_global(e['tecla'])}")
                    if not dados_p["teclas"]:
                        b.row("   (nenhuma tecla cadastrada)")
                    b.br()
                    b.sep()
                    b.br()
                    for k, desc in [("1","Alfabética"), ("2","Numérica"),
                                     ("3","Ordem de adição"), ("V","Voltar")]:
                        b.row(f"   [{k}]  {desc}")
                    b.br()
                print()
                o = tecla()
                modos = {"1": ORDEM_ALFABETICA, "2": ORDEM_NUMERICA, "3": ORDEM_ADICAO}
                if o == "v":
                    break
                if o not in modos:
                    pausa_erro("Opção inválida.")
                    continue
                modo_escolhido = modos[o]
                preview = ordenar_teclas(
                    dados_p["teclas"], modo_escolhido,
                    dados_p.get("ordem_adicao", dados_p["teclas"])
                )
                cls()
                with Box("PREVIEW", modo_escolhido) as b:
                    b.sep("─")
                    b.br()
                    for i, e in enumerate(preview, 1):
                        b.row(f"   {i:>2}.   {e['nome']:<28}  #{numero_global(e['tecla'])}")
                    b.br()
                    b.sep()
                    b.br()
                    b.row("  [S] Confirmar   [N] Escolher outra")
                    b.br()
                print()
                if tecla() == "s":
                    dados_p["ordem"] = modo_escolhido
                    reconstruir_perfil(nome, cfg)
                    msg_ok(f"Ordenação → '{modo_escolhido}'")
                    aguardar_ou_timeout(2)
                    break

        elif opt == "3":
            fazer_backup_perfil(nome, cfg, pedir_pasta_destino())

        elif opt == "v":
            break
        else:
            pausa_erro("Opção inválida.")

    return cfg

# ── MENU DO PERFIL ────────────────────────────────────────────
def menu_perfil(nome, cfg):
    while True:
        dados    = cfg["perfis"][nome]
        entradas = dados["teclas"]
        livres_g = len(TECLAS_BASE) * 8 - len(teclas_em_uso_global(cfg))

        cls()
        with Box("PERFIL", nome) as b:
            b.row(f"  {len(entradas)} tecla(s)   ·   {livres_g} livre(s) globalmente")
            b.sep("─")
            b.br()
            if entradas:
                for i, e in enumerate(entradas, 1):
                    b.row(f"   {i:>2}.   {e['nome']:<28}  #{numero_global(e['tecla'])}")
            else:
                b.row("   (nenhuma tecla cadastrada)")
            b.br()
            b.sep()
            b.br()
            b.row("   [1] Adicionar   [2] Remover   [3] Editar   [4] Config   [V] Voltar")
            b.br()
        print()
        opt = tecla()

        # ── ADICIONAR ─────────────────────────────────────────
        if opt == "1":
            idx_mod = None
            while True:
                t_val, idx_mod = configurar_tecla(teclas_em_uso_global(cfg), idx_mod_inicial=idx_mod)
                if not t_val:
                    break
                cls()
                print()
                nome_t = input(f"  Nome  (Enter = usar '{t_val}'): ").strip()
                if not nome_t:
                    nome_t = t_val
                dados["teclas"].append({"nome": nome_t, "tecla": t_val})
                if "ordem_adicao" not in dados:
                    dados["ordem_adicao"] = []
                dados["ordem_adicao"].append({"nome": nome_t, "tecla": t_val})
                reconstruir_perfil(nome, cfg)
                msg_ok(f"'{nome_t}' adicionada!")
                print()
                print("  Adicionar outra?  [S] Sim   [N] Não")
                print()
                if tecla() != "s":
                    idx_mod = None
                    break

        # ── REMOVER ───────────────────────────────────────────
        elif opt == "2":
            if not entradas:
                pausa_erro("Nenhuma tecla para remover.")
                continue
            cls()
            with Box("REMOVER TECLA", nome) as b:
                b.sep("─")
                b.br()
                for i, e in enumerate(entradas, 1):
                    b.row(f"   {i:>2}.   {e['nome']:<28}  {e['tecla']}")
                b.br()
                b.sep()
                b.br()
                b.row("  Número   ou   [C] Cancelar")
                b.br()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c":
                continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(entradas):
                    e = entradas[idx]
                    cls()
                    print()
                    print(f"  Remover  '{e['nome']}'  ({e['tecla']})?  [S] Sim   [N] Não")
                    print()
                    if tecla() == "s":
                        rem = entradas.pop(idx)
                        dados["ordem_adicao"] = [
                            x for x in dados.get("ordem_adicao", [])
                            if x["tecla"] != rem["tecla"]
                        ]
                        reconstruir_perfil(nome, cfg)
                        msg_ok(f"'{e['nome']}' removida.")
                        aguardar_ou_timeout(2)
                    else:
                        msg_info("Cancelado.")
                        aguardar_ou_timeout(1)
                else:
                    pausa_erro("Número fora do intervalo.")
            except ValueError:
                pausa_erro("Entrada inválida.")

        # ── EDITAR ────────────────────────────────────────────
        elif opt == "3":
            if not entradas:
                pausa_erro("Nenhuma tecla para editar.")
                continue
            cls()
            with Box("EDITAR TECLA", nome) as b:
                b.sep("─")
                b.br()
                for i, e in enumerate(entradas, 1):
                    b.row(f"   {i:>2}.   {e['nome']:<28}  {e['tecla']}")
                b.br()
                b.sep()
                b.br()
                b.row("  Número   ou   [C] Cancelar")
                b.br()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c":
                continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(entradas):
                    e        = entradas[idx]
                    alterado = False
                    cls()
                    print()
                    print(f"  Editando:  '{e['nome']}'  ({e['tecla']})")
                    print()
                    print("─" * W)
                    print()
                    novo_nome = input(f"  Novo nome  (Enter=manter '{e['nome']}'): ").strip()
                    if novo_nome and novo_nome != e["nome"]:
                        e["nome"] = novo_nome
                        alterado  = True
                        msg_ok(f"Nome → '{novo_nome}'")
                    print()
                    print("  Mudar tecla?  [S] Sim   [N] Não")
                    print()
                    if tecla() == "s":
                        usadas_sem = teclas_em_uso_global(cfg)
                        usadas_sem.discard(e["tecla"])
                        t_val, _ = configurar_tecla(usadas_sem)
                        if t_val and t_val != e["tecla"]:
                            old_tecla = e["tecla"]
                            e["tecla"] = t_val
                            # Sincronizar ordem_adicao com a nova chave de tecla
                            for _oa in dados.get("ordem_adicao", []):
                                if _oa["tecla"] == old_tecla:
                                    _oa["tecla"] = t_val
                                    break
                            alterado   = True
                            msg_ok(f"Tecla → '{t_val}'")
                        else:
                            msg_info("Tecla não alterada.")
                    if alterado:
                        reconstruir_perfil(nome, cfg)
                        msg_ok("Alterações salvas!")
                    else:
                        msg_info("Nenhuma alteração.")
                    aguardar_ou_timeout(2)
                else:
                    pausa_erro("Número fora do intervalo.")
            except ValueError:
                pausa_erro("Entrada inválida.")

        elif opt == "4":
            cfg = menu_configuracoes_perfil(nome, cfg)

        elif opt == "v":
            break

        else:
            pausa_erro("Opção inválida.")

    return cfg

# ── TESTE DE TECLAS ───────────────────────────────────────────
def menu_teste_teclas():
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    FLAG  = os.path.join(FKB_DIR, "fkb_test.flag")
    parar = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                n     = int(self.headers.get("Content-Length", 0))
                corpo = self.rfile.read(n).decode("utf-8").strip()
                ts    = time.strftime("%H:%M:%S")
                print(f"\r  ◉  [{ts}]  {corpo:<36}  [V] voltar", end="", flush=True)
                self.send_response(200); self.end_headers()
            except Exception:
                self.send_response(500); self.end_headers()
        def log_message(self, *a): pass

    def rodar():
        try:
            srv = HTTPServer(("localhost", TEST_PORT), Handler)
        except OSError as _e:
            print(f"\n  ✕  Porta {TEST_PORT} ocupada: {_e}")
            parar.set()
            return
        srv.timeout = 0.5
        while not parar.is_set():
            srv.handle_request()

    try: open(FLAG, "w").close()
    except Exception: pass

    cls()
    with Box("TESTE DE TECLAS") as b:
        b.sep()
        b.br()
        b.row("  Pressione teclas no celular — o nome aparece aqui em tempo real.")
        b.br()
        b.sep()
        b.br()
        b.row("  [V] Voltar")
        b.br()
    print()
    print("  · · ·  aguardando  · · ·", end="", flush=True)

    threading.Thread(target=rodar, daemon=True).start()

    while True:
        try:
            ch = msvcrt.getwch() if _WINDOWS else input().strip().lower()
            if ch.lower() == "v":
                parar.set()
                print()
                break
        except (EOFError, KeyboardInterrupt):
            parar.set()
            break

    try: os.remove(FLAG)
    except Exception: pass

# ── MENU CONFIGURAÇÕES ────────────────────────────────────────
def menu_configuracoes(cfg):
    while True:
        cls()
        with Box(f"CONFIGURAÇÕES  ·  FKB Remote  v{VERSION}") as b:
            b.sep()
            b.br()
            for k, desc in [
                ("1", "Backup de tudo"),
                ("2", "Backup de perfil específico"),
                ("3", "Restaurar backup"),
                ("4", "Reiniciar servidor"),
                ("5", "Desinstalar"),
                ("6", "Testar teclas"),
                ("V", "Voltar"),
            ]:
                b.row(f"   [{k}]  {desc}")
            b.br()
        print()
        opt = tecla()

        if opt == "1":
            fazer_backup_tudo(cfg, pedir_pasta_destino())

        elif opt == "2":
            perfis = list(cfg["perfis"].keys())
            if not perfis:
                pausa_erro("Nenhum perfil criado.")
                continue
            cls()
            with Box("BACKUP DE PERFIL") as b:
                b.sep("─")
                b.br()
                for i, p in enumerate(perfis, 1):
                    b.row(f"   {i}.   {p}")
                b.br()
                b.sep()
                b.br()
                b.row("  Número   ou   [C] Cancelar")
                b.br()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c": continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(perfis):
                    fazer_backup_perfil(perfis[idx], cfg, pedir_pasta_destino())
                else:
                    pausa_erro("Número fora do intervalo.")
            except ValueError:
                pausa_erro("Entrada inválida.")

        elif opt == "3":
            cfg = restaurar_backup(cfg)

        elif opt == "4":
            reiniciar_servidor_ur()
            msg_ok("Comando de reinício enviado.")
            aguardar_ou_timeout(2)

        elif opt == "5":
            cls()
            with Box("DESINSTALAR FKB REMOTE") as b:
                b.sep("─")
                b.br()
                _lim = W - 18  # W-2 - len("  AppData :  ") - 1
                b.row(f"  AppData :  {FKB_DIR[:_lim] + ('…' if len(FKB_DIR) > _lim else '')}")
                _rem = REMOTES_DIR + '\\FKB-*'
                b.row(f"  Perfis  :  {_rem[:_lim] + ('…' if len(_rem) > _lim else '')}")
                b.br()
                b.row("  O arquivo .py e backups NÃO serão removidos.")
                b.br()
            print()
            if input("  Digite CONFIRMAR para prosseguir: ").strip() == "CONFIRMAR":
                erros = []
                itens = ([FKB_DIR] if os.path.exists(FKB_DIR) else []) + \
                        glob.glob(os.path.join(REMOTES_DIR, "FKB-*"))
                total = max(len(itens), 1)
                print()
                for i, p in enumerate(itens):
                    try: shutil.rmtree(p)
                    except Exception as ex: erros.append(str(ex))
                    _barra((i + 1) * 100 / total)
                _barra(100)
                print()
                if erros:
                    msg_aviso(f"Concluído com erros: {'; '.join(erros)}")
                else:
                    msg_ok("FKB Remote desinstalado com sucesso!")
                print()
                print("  Pressione qualquer tecla para sair...")
                if _WINDOWS: msvcrt.getch()
                else: input()
                sys.exit()
            else:
                msg_info("Desinstalação cancelada.")
                aguardar_ou_timeout(2)

        elif opt == "6":
            menu_teste_teclas()

        elif opt == "v":
            break

        else:
            pausa_erro("Opção inválida.")

    return cfg

# ── MENU INICIAL ──────────────────────────────────────────────
def menu_inicial(cfg):
    while True:
        cls()
        perfis = list(cfg["perfis"].keys())

        _box_topo()
        _box_row(f"  FKB REMOTE  ·  v{VERSION}  ·  {AUTHOR}")
        _box_sep()
        _box_br()

        if perfis:
            _box_row(f"   {'#':<5}{'PERFIL':<24}{'TECLAS':>6}   MODIFICADO")
            _box_row(f"   {'─'*4}  {'─'*22}  {'─'*6}   {'─'*16}")
            _box_br()
            for i, nome in enumerate(perfis, 1):
                d   = cfg["perfis"][nome]
                qtd = len(d.get("teclas", []))
                mod = d.get("modificado", "—")[:16]
                _box_row(f"   {i:<5}{nome:<24}{qtd:>5} tk   {mod}")
                _box_br()
        else:
            _box_row("   Nenhum perfil criado.   [C] para começar.")
            _box_br()

        _box_sep()
        _box_br()
        _box_row("   [C] Criar    [R] Renomear    [E] Excluir    [O] Config    [S] Sair")
        if perfis:
            _box_row("   Digite o número do perfil para abrir")
        _box_br()
        _box_fim()
        # Nota: menu_inicial usa primitivos diretamente pois intercala lógica
        # de exibição condicional que o Box não simplifica neste caso
        print()
        opt = input("  › ").strip().lower()
        if not opt:
            continue

        try:
            idx = int(opt) - 1
            if 0 <= idx < len(perfis):
                cfg = menu_perfil(perfis[idx], cfg)
            else:
                pausa_erro("Número fora do intervalo.")
            continue
        except ValueError:
            pass

        if opt == "c":
            cls()
            print()
            padrao = proximo_nome_padrao(cfg)
            nome   = input(f"  Nome  (Enter={padrao!r}, C=cancelar): ").strip()
            if nome.lower() == "c":
                msg_info("Cancelado.")
                aguardar_ou_timeout(1)
                continue
            nome = _sanitizar_nome(nome) or padrao
            if nome in cfg["perfis"]:
                pausa_erro(f"Já existe um perfil '{nome}'.")
                continue
            cfg["perfis"][nome] = {
                "teclas": [], "ordem_adicao": [], "ordem": ORDEM_ALFABETICA,
                "criado":    time.strftime("%Y-%m-%d %H:%M:%S"),
                "modificado": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            os.makedirs(perfil_dir(nome), exist_ok=True)
            reconstruir_perfil(nome, cfg)
            msg_ok(f"Perfil '{nome}' criado!")
            print()
            print(f"  Abrir '{nome}' agora?  [S] Sim   [N] Não")
            print()
            if tecla() == "s":
                cfg = menu_perfil(nome, cfg)

        elif opt == "r":
            if not perfis:
                pausa_erro("Nenhum perfil para renomear.")
                continue
            cls()
            print()
            for i, p in enumerate(perfis, 1):
                print(f"  {i}.  {p}")
            print()
            print("─" * W)
            print()
            raw = input("  Número  (C=cancelar): ").strip().lower()
            if raw == "c": continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(perfis):
                    nome_atual = perfis[idx]
                    print()
                    novo = _sanitizar_nome(input(f"  Novo nome para '{nome_atual}'  (Enter=cancelar): ").strip()) or ""
                    if not novo:
                        msg_info("Cancelado.")
                        aguardar_ou_timeout(1)
                        continue
                    if novo == nome_atual:
                        msg_info("Nome igual, nada alterado.")
                        aguardar_ou_timeout(1)
                        continue
                    if novo in cfg["perfis"]:
                        pausa_erro(f"Já existe um perfil '{novo}'.")
                        continue
                    cfg["perfis"][novo] = cfg["perfis"].pop(nome_atual)
                    pa, pn = perfil_dir(nome_atual), perfil_dir(novo)
                    if os.path.exists(pa):
                        try: os.rename(pa, pn)
                        except Exception: pass
                    reconstruir_perfil(novo, cfg)
                    msg_ok(f"Renomeado para '{novo}'.")
                    aguardar_ou_timeout(2)
                else:
                    pausa_erro("Número fora do intervalo.")
            except ValueError:
                pausa_erro("Entrada inválida.")

        elif opt == "e":
            if not perfis:
                pausa_erro("Nenhum perfil para excluir.")
                continue
            if len(perfis) == 1:
                pausa_erro("Não é possível excluir o único perfil.")
                continue
            cls()
            print()
            for i, p in enumerate(perfis, 1):
                print(f"  {i}.  {p}")
            print()
            print("─" * W)
            print()
            raw = input("  Número  (C=cancelar): ").strip().lower()
            if raw == "c": continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(perfis):
                    nome = perfis[idx]
                    cls()
                    print()
                    print(f"  Fazer backup de '{nome}' antes?  [S] Sim   [N] Não")
                    print()
                    if tecla() == "s":
                        fazer_backup_perfil(nome, cfg, pedir_pasta_destino())
                    print()
                    print(f"  ⚠  Excluir '{nome}'?  [S] Sim   [N] Não")
                    print()
                    if tecla() == "s":
                        del cfg["perfis"][nome]
                        p = perfil_dir(nome)
                        if os.path.exists(p): shutil.rmtree(p)
                        salvar_config(cfg)
                        reiniciar_servidor_ur()
                        msg_ok(f"Perfil '{nome}' excluído.")
                        aguardar_ou_timeout(2)
                    else:
                        msg_info("Cancelado.")
                        aguardar_ou_timeout(1)
                else:
                    pausa_erro("Número fora do intervalo.")
            except ValueError:
                pausa_erro("Entrada inválida.")

        elif opt == "o":
            cfg = menu_configuracoes(cfg)

        elif opt == "s":
            cls()
            print()
            print("  Até mais! 👋")
            print()
            break

        else:
            pausa_erro("Opção inválida.")

# ── ENTRY POINT ───────────────────────────────────────────────
if __name__ == "__main__":
    try:
        verificar_ur_instalado()
        verificar_ur_rodando()
        os.makedirs(FKB_DIR, exist_ok=True)
        motor_instalado = verificar_motor()
        if motor_instalado:
            print("\n  Instalação concluída! Iniciando...\n")
            time.sleep(1)
        cfg = carregar_config()
        menu_inicial(cfg)
    except Exception:
        import traceback
        cls()
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
