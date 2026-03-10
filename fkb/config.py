import os, json, re, time, glob, shutil, html

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    _WINDOWS = False

from .constants import (
    W, FKB_DIR, CONFIG_PATH, BACKUP_CONFIG_PATH, REMOTES_DIR,
    ORDEM_ALFABETICA, ORDEM_NUMERICA, ORDEM_ADICAO,
    TECLAS_BASE, MODIFICADORES, MAX_TECLAS_POR_PERFIL,
    MAX_PERFIS_VAZIOS, MIN_TECLAS_PERFIL,
)
from .ui import cls


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
        # Trunca teclas que excedem o limite — avisa no terminal
        if len(d["teclas"]) > MAX_TECLAS_POR_PERFIL:
            excesso = len(d["teclas"]) - MAX_TECLAS_POR_PERFIL
            print(f"  ⚠  Perfil '{nome}': {excesso} tecla(s) removida(s) por exceder o limite de {MAX_TECLAS_POR_PERFIL}.")
            d["teclas"] = d["teclas"][:MAX_TECLAS_POR_PERFIL]
        if not isinstance(d.get("ordem_adicao"), list):
            d["ordem_adicao"] = list(d["teclas"])
        else:
            # Sincroniza ordem_adicao com as teclas que sobraram após truncamento
            teclas_validas = {e["tecla"] for e in d["teclas"]}
            d["ordem_adicao"] = [e for e in d["ordem_adicao"] if e.get("tecla") in teclas_validas]
        if d.get("ordem") not in ORDENS_VALIDAS:
            d["ordem"] = ORDEM_ALFABETICA
        if not isinstance(d.get("criado"), str):
            d["criado"] = "desconhecido"
        if not isinstance(d.get("modificado"), str):
            d["modificado"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return cfg


def perfis_vazios_count(cfg):
    """Retorna o número de perfis considerados vazios (menos de MIN_TECLAS_PERFIL teclas
    e com data de criação conhecida). Perfis 'desconhecido' sem teclas já foram removidos
    em _validar_cfg, portanto não aparecem aqui.
    """
    return sum(
        1 for d in cfg["perfis"].values()
        if len(d.get("teclas", [])) < MIN_TECLAS_PERFIL
        and d.get("criado", "desconhecido") != "desconhecido"
    )


def _limpar_perfis_vazios(cfg):
    """Remove perfis que violam as regras de perfis vazios:
      - Perfis com criado='desconhecido' e sem teclas → excluir sempre
      - Perfis com data real e sem teclas suficientes → manter só os 2 mais antigos,
        excluir o resto por ordem de criação (mais novos primeiro)
    Avisa no terminal sobre cada remoção.
    Retorna cfg modificado.
    """
    import shutil as _shutil

    # 1. Excluir perfis desconhecidos sem teclas
    for nome in list(cfg["perfis"].keys()):
        d = cfg["perfis"][nome]
        if d.get("criado", "desconhecido") == "desconhecido" and not d.get("teclas"):
            print(f"  ⚠  Perfil '{nome}' removido (sem data e sem teclas).")
            del cfg["perfis"][nome]
            pasta = os.path.join(
                os.environ.get('PROGRAMDATA', r'C:\ProgramData'),
                "Unified Remote", "Remotes", "Custom", f"FKB-{nome}"
            )
            if os.path.exists(pasta):
                try: _shutil.rmtree(pasta)
                except Exception: pass

    # 2. Checar perfis com data real mas abaixo do mínimo de teclas
    vazios = [
        (nome, d) for nome, d in cfg["perfis"].items()
        if len(d.get("teclas", [])) < MIN_TECLAS_PERFIL
        and d.get("criado", "desconhecido") != "desconhecido"
    ]

    if len(vazios) <= MAX_PERFIS_VAZIOS:
        return cfg

    # Ordena por data de criação — mais antigos primeiro
    vazios.sort(key=lambda x: x[1].get("criado", ""))
    # Mantém os MAX_PERFIS_VAZIOS mais antigos, exclui o resto
    excluir = vazios[MAX_PERFIS_VAZIOS:]
    for nome, _ in excluir:
        print(f"  ⚠  Perfil '{nome}' removido (excesso de perfis vazios — limite: {MAX_PERFIS_VAZIOS}).")
        del cfg["perfis"][nome]
        pasta = os.path.join(
            os.environ.get('PROGRAMDATA', r'C:\ProgramData'),
            "Unified Remote", "Remotes", "Custom", f"FKB-{nome}"
        )
        if os.path.exists(pasta):
            try: _shutil.rmtree(pasta)
            except Exception: pass

    cfg = _limpar_perfis_vazios(cfg)
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
    Exibe aviso APENAS se havia perfis no disco (corrupção real).
    Na primeira execução limpa retorna config vazio silenciosamente.
    """
    cfg    = config_vazio()
    pastas = [p for p in glob.glob(os.path.join(REMOTES_DIR, "FKB-*"))
              if os.path.isdir(p)]

    # Primeira execução limpa — nada foi corrompido, ainda não existe nada
    if not pastas:
        salvar_config(cfg)
        return cfg

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


def ordenar_teclas(entradas, modo, ordem_adicao):
    from .constants import numero_global
    if modo == ORDEM_ALFABETICA:
        return sorted(entradas, key=lambda e: e["nome"].lower())
    elif modo == ORDEM_NUMERICA:
        return sorted(entradas, key=lambda e: numero_global(e["tecla"]))
    elif modo == ORDEM_ADICAO:
        idx = {e["tecla"]: i for i, e in enumerate(ordem_adicao)}
        return sorted(entradas, key=lambda e: idx.get(e["tecla"], 9999))
    return list(entradas)
