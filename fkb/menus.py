import os, sys, shutil, glob, time, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    import msvcrt
    _WINDOWS = True
except ImportError:
    _WINDOWS = False

from .constants import (
    W, VERSION, BUILD, AUTHOR, FKB_DIR, REMOTES_DIR,
    TECLAS_BASE, MODIFICADORES,
    ORDEM_ALFABETICA, ORDEM_NUMERICA, ORDEM_ADICAO,
    TEST_PORT, numero_global,
    MAX_TECLAS_POR_PERFIL, MAX_PERFIS, MAX_PERFIS_VAZIOS, MIN_TECLAS_PERFIL,
)
from .ui import (
    cls, Box, _box_topo, _box_fim, _box_sep, _box_row, _box_br,
    msg_ok, msg_info, msg_aviso, pausa_erro,
    tecla, aguardar_ou_timeout, br,
)
from .config import (
    salvar_config, teclas_em_uso_global,
    _sanitizar_nome, proximo_nome_padrao, ordenar_teclas,
    perfis_vazios_count,
)
from .perfil import perfil_dir, reconstruir_perfil, aplicar_icone
from .backup import (
    pedir_pasta_destino, fazer_backup_perfil,
    fazer_backup_tudo, restaurar_backup,
)
from .motor import reiniciar_servidor_ur, ur_esta_rodando


# ── UTILITÁRIOS VISUAIS ───────────────────────────────────────
def _fmt_data(iso):
    """Converte 'AAAA-MM-DD HH:MM:SS' para 'DD/MM/AAAA HH:MM'."""
    try:
        d, h = iso.split(" ")
        a, m, dia = d.split("-")
        return f"{dia}/{m}/{a}  {h[:5]}"
    except Exception:
        return iso[:16] if iso != "desconhecido" else "—"


def _barra_progresso(qtd, maximo, largura=16):
    """Retorna barra de progresso Unicode."""
    preenchido = int(largura * qtd / maximo) if maximo else 0
    return "█" * preenchido + "░" * (largura - preenchido)


def _decodificar_tecla(tecla_str):
    """Retorna (modificador_label, tecla_nome) de uma string como '^!{F13}'."""
    for pref, label in sorted(MODIFICADORES, key=lambda x: -len(x[0])):
        if tecla_str.startswith(pref):
            cod = tecla_str[len(pref):].strip("{}")
            return label, cod
    return "Simples", tecla_str.strip("{}")


_ur_cache        = None   # True | False
_ur_cache_expira = 0.0    # timestamp de expiração
_UR_CACHE_TTL    = 10     # segundos entre verificações

def _status_ur():
    global _ur_cache, _ur_cache_expira
    agora = time.time()
    if _ur_cache is None or agora >= _ur_cache_expira:
        _ur_cache        = ur_esta_rodando()
        _ur_cache_expira = agora + _UR_CACHE_TTL
    return "● Online" if _ur_cache else "○ Offline"


def _icone_status(nome_perfil):
    pasta = perfil_dir(nome_perfil)
    if os.path.exists(os.path.join(pasta, "icon.png")):
        return "✓ ícone definido"
    return "○ sem ícone"


# ── SELEÇÃO DE TECLA ──────────────────────────────────────────
def _exibir_grade_teclas(pref, usadas_global):
    livres  = 0
    celulas = []
    for i, tec in enumerate(TECLAS_BASE, 1):
        em_uso = (pref + "{" + tec + "}") in usadas_global
        if em_uso:
            celulas.append(f"  {i:>2}. ⚠ [{tec} · EM USO]  ")
        else:
            celulas.append(f"  {i:>2}. {tec:<18}  ")
            livres += 1
    col_w = (W - 2) // 3
    for i in range(0, len(celulas), 3):
        grupo = celulas[i:i+3]
        txt   = "".join(f"{g:<{col_w}}" for g in grupo)
        print(f"║{txt:<{W-2}}║")
    return livres


def _tela_teclas(idx_mod, usadas_global):
    pref, label = MODIFICADORES[idx_mod]
    em_uso_cnt  = sum(1 for tec in TECLAS_BASE if (pref+"{"+tec+"}") in usadas_global)
    livres_cnt  = len(TECLAS_BASE) - em_uso_cnt
    cls()
    _box_topo()
    _box_row(f"  FKB Remote  ›  Selecionar Tecla  ›  Passo 2 de 2  ·  {label}")
    _box_sep()
    _box_row(f"  {livres_cnt} livre(s)   ·   {em_uso_cnt} em uso")
    _box_sep("─")
    _box_br()
    livres = _exibir_grade_teclas(pref, usadas_global)
    _box_br()
    _box_sep()
    _box_br()
    if livres == 0:
        _box_row("  Todas as teclas deste modificador estão em uso.")
        _box_br()
        _box_fim()
        aguardar_ou_timeout(3)
        return None, idx_mod
    _box_row("  Número (1–45)                                          [V]  Voltar")
    _box_br()
    _box_fim()
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
            _box_topo()
            _box_row("  FKB Remote  ›  Selecionar Tecla  ›  Passo 1 de 2  ·  Modificador")
            _box_sep("─")
            _box_br()
            mods = list(enumerate(MODIFICADORES, 1))
            for i in range(0, len(mods), 2):
                par = mods[i:i+2]
                linha = "".join(f"   [{n}]  {lbl:<30}" for n, (_, lbl) in par)
                _box_row(linha)
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [V]  Voltar")
            _box_br()
            _box_fim()
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


# ── MENU CONFIGURAÇÕES DO PERFIL ─────────────────────────────
def menu_configuracoes_perfil(nome, cfg):
    while True:
        cls()
        icone = _icone_status(nome)
        _box_topo()
        _box_row(f"  FKB Remote  ›  {nome}  ›  Configurações")
        _box_sep()
        _box_row(f"  {icone}")
        _box_sep("─")
        _box_br()
        _box_row("   [1]  Alterar ícone          [2]  Remover ícone        [3]  Ordenar teclas")
        _box_br()
        _box_row("   [4]  Backup")
        _box_br()
        _box_sep()
        _box_br()
        _box_row("   [V]  Voltar")
        _box_br()
        _box_fim()
        print()
        opt = tecla()

        if opt == "1":
            aplicar_icone(nome)

        elif opt == "2":
            # remover ícone
            pasta_ic = perfil_dir(nome)
            icon_p   = os.path.join(pasta_ic, "icon.png")
            tray_p   = os.path.join(pasta_ic, "tray.png")
            if not os.path.exists(icon_p):
                pausa_erro("Este perfil não possui ícone definido.")
            else:
                for p in (icon_p, tray_p):
                    try:
                        if os.path.exists(p): os.remove(p)
                    except Exception: pass
                reiniciar_servidor_ur()
                msg_ok("Ícone removido.")
                aguardar_ou_timeout(2)

        elif opt == "3":
            dados_p = cfg["perfis"][nome]
            while True:
                cls()
                ordem_atual = dados_p.get("ordem", ORDEM_ALFABETICA)
                _box_topo()
                _box_row(f"  FKB Remote  ›  {nome}  ›  Ordenar Teclas")
                _box_sep()
                _box_row(f"  Ordem atual: {ordem_atual}")
                _box_sep("─")
                _box_br()
                if dados_p["teclas"]:
                    for i, e in enumerate(dados_p["teclas"], 1):
                        ml, tn = _decodificar_tecla(e["tecla"])
                        _box_row(f"   {i:>2}.  {e['nome']:<24}  {ml:<20}  {tn}")
                else:
                    _box_row("   (nenhuma tecla cadastrada)")
                _box_br()
                _box_sep()
                _box_br()
                _box_row("   [1]  Alfabética     [2]  Numérica     [3]  Ordem de adição     [V]  Voltar")
                _box_br()
                _box_fim()
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
                _box_topo()
                _box_row(f"  FKB Remote  ›  {nome}  ›  Preview  ·  {modo_escolhido}")
                _box_sep("─")
                _box_br()
                for i, e in enumerate(preview, 1):
                    ml, tn = _decodificar_tecla(e["tecla"])
                    _box_row(f"   {i:>2}.  {e['nome']:<24}  {ml:<20}  {tn}")
                _box_br()
                _box_sep()
                _box_br()
                _box_row("   [S]  Confirmar                                    [N]  Escolher outra")
                _box_br()
                _box_fim()
                print()
                if tecla() == "s":
                    dados_p["ordem"] = modo_escolhido
                    reconstruir_perfil(nome, cfg)
                    msg_ok(f"Ordenação → '{modo_escolhido}'")
                    aguardar_ou_timeout(2)
                    break

        elif opt == "4":
            fazer_backup_perfil(nome, cfg, pedir_pasta_destino())

        elif opt == "v":
            break
        else:
            pausa_erro("Opção inválida.")

    return cfg


# ── MENU DO PERFIL ────────────────────────────────────────────
def menu_perfil(nome, cfg):
    ultimo_status = ""
    while True:
        dados       = cfg["perfis"][nome]
        entradas    = dados["teclas"]
        qtd         = len(entradas)
        livres_g    = len(TECLAS_BASE) * 8 - len(teclas_em_uso_global(cfg))
        ordem_atual = dados.get("ordem", ORDEM_ALFABETICA)
        icone       = _icone_status(nome)
        cheio       = qtd >= MAX_TECLAS_POR_PERFIL

        cls()
        _box_topo()
        _box_row(f"  FKB Remote  ›  {nome}")
        _box_sep()
        barra = _barra_progresso(qtd, MAX_TECLAS_POR_PERFIL)
        _box_row(f"  {barra}  {qtd}/{MAX_TECLAS_POR_PERFIL} teclas   ·   ordem: {ordem_atual}   ·   {icone}")
        _box_sep("─")
        _box_br()
        if entradas:
            for i, e in enumerate(entradas, 1):
                ml, tn = _decodificar_tecla(e["tecla"])
                _box_row(f"   {i:>2}.  {e['nome']:<24}  {ml:<20}  {tn}")
        else:
            _box_row("   (nenhuma tecla cadastrada)")
        _box_br()
        if ultimo_status:
            _box_sep()
            _box_row(f"  {ultimo_status}")
        _box_sep()
        _box_br()
        label_add = "Perfil cheio  " if cheio else "Adicionar     "
        _box_row(f"   [1]  {label_add}   [2]  Remover        [3]  Editar")
        _box_br()
        _box_row(f"   [4]  Configurações                                    [V]  Voltar")
        _box_br()
        _box_row(f"   {livres_g} tecla(s) disponíveis globalmente")
        _box_br()
        _box_fim()
        print()
        opt = tecla()

        # ── ADICIONAR ─────────────────────────────────────────
        if opt == "1":
            if cheio:
                pausa_erro(f"Limite de {MAX_TECLAS_POR_PERFIL} teclas por perfil atingido.")
                continue
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
                ultimo_status = f"✓  '{nome_t}' adicionada com sucesso"
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
            _box_topo()
            _box_row(f"  FKB Remote  ›  {nome}  ›  Remover Tecla")
            _box_sep("─")
            _box_br()
            for i, e in enumerate(entradas, 1):
                ml, tn = _decodificar_tecla(e["tecla"])
                _box_row(f"   {i:>2}.  {e['nome']:<24}  {ml:<20}  {tn}")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [C]  Cancelar")
            _box_br()
            _box_fim()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c":
                continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(entradas):
                    e = entradas[idx]
                    cls()
                    _box_topo()
                    _box_row(f"  FKB Remote  ›  {nome}  ›  ⚠  Confirmar Remoção")
                    _box_sep("─")
                    _box_br()
                    ml, tn = _decodificar_tecla(e["tecla"])
                    _box_row(f"  Nome:    {e['nome']}")
                    _box_row(f"  Tecla:   {ml}  ·  {tn}")
                    _box_br()
                    _box_sep()
                    _box_br()
                    _box_row("   [S]  Confirmar remoção                           [N]  Cancelar")
                    _box_br()
                    _box_fim()
                    print()
                    if tecla() == "s":
                        nome_removido = e["nome"]
                        rem = entradas.pop(idx)
                        dados["ordem_adicao"] = [
                            x for x in dados.get("ordem_adicao", [])
                            if x["tecla"] != rem["tecla"]
                        ]
                        reconstruir_perfil(nome, cfg)
                        ultimo_status = f"✓  '{nome_removido}' removida com sucesso"
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
            _box_topo()
            _box_row(f"  FKB Remote  ›  {nome}  ›  Editar Tecla")
            _box_sep("─")
            _box_br()
            for i, e in enumerate(entradas, 1):
                ml, tn = _decodificar_tecla(e["tecla"])
                _box_row(f"   {i:>2}.  {e['nome']:<24}  {ml:<20}  {tn}")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [C]  Cancelar")
            _box_br()
            _box_fim()
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
                    ml, tn = _decodificar_tecla(e["tecla"])
                    _box_topo()
                    _box_row(f"  FKB Remote  ›  {nome}  ›  Editando: {e['nome']}")
                    _box_sep("─")
                    _box_br()
                    _box_row(f"  Tecla atual:  {ml}  ·  {tn}")
                    _box_br()
                    _box_fim()
                    print()
                    novo_nome = input(f"  Novo nome  (Enter = manter '{e['nome']}'): ").strip()
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
                            for _oa in dados.get("ordem_adicao", []):
                                if _oa["tecla"] == old_tecla:
                                    _oa["tecla"] = t_val
                                    break
                            alterado = True
                            m2, t2 = _decodificar_tecla(t_val)
                            msg_ok(f"Tecla → {m2}  ·  {t2}")
                        else:
                            msg_info("Tecla não alterada.")
                    if alterado:
                        reconstruir_perfil(nome, cfg)
                        ultimo_status = f"✓  '{e['nome']}' editada com sucesso"
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
            ultimo_status = ""
            break

        else:
            pausa_erro("Opção inválida.")

    return cfg


# ── MENU TESTE DE TECLAS ──────────────────────────────────────
def menu_teste_teclas():
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
    _box_topo()
    _box_row("  FKB Remote  ›  Configurações  ›  Teste de Teclas")
    _box_sep("─")
    _box_br()
    _box_row("  Pressione teclas no celular — o nome aparece aqui em tempo real.")
    _box_br()
    _box_sep()
    _box_br()
    _box_row("   [V]  Voltar")
    _box_br()
    _box_fim()
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
        _box_topo()
        _box_row(f"  FKB Remote  ›  Configurações  ·  v{VERSION}  ({BUILD})")
        _box_sep()
        _box_row("  BACKUP")
        _box_sep("─")
        _box_br()
        _box_row("   [1]  Backup de tudo          [2]  Backup de perfil     [3]  Restaurar")
        _box_br()
        _box_sep()
        _box_row("  SISTEMA")
        _box_sep("─")
        _box_br()
        _box_row("   [4]  Reiniciar servidor      [5]  Desinstalar          [6]  Testar teclas")
        _box_br()
        _box_sep()
        _box_br()
        _box_row("   [V]  Voltar")
        _box_br()
        _box_fim()
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
            _box_topo()
            _box_row("  FKB Remote  ›  Configurações  ›  Backup de Perfil")
            _box_sep("─")
            _box_br()
            for i, p in enumerate(perfis, 1):
                _box_row(f"   {i}.   {p}")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [C]  Cancelar")
            _box_br()
            _box_fim()
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

        elif opt == "6":
            menu_teste_teclas()

        elif opt == "5":
            cls()
            _box_topo()
            _box_row("  FKB Remote  ›  Configurações  ›  ⚠  Desinstalar")
            _box_sep("─")
            _box_br()
            _lim = W - 18
            _box_row(f"  AppData :  {FKB_DIR[:_lim] + ('…' if len(FKB_DIR) > _lim else '')}")
            _rem = REMOTES_DIR + '\\FKB-*'
            _box_row(f"  Perfis  :  {_rem[:_lim] + ('…' if len(_rem) > _lim else '')}")
            _box_br()
            _box_row("  Os arquivos de backup NÃO serão removidos.")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("   Digite CONFIRMAR para prosseguir ou qualquer outra coisa para cancelar")
            _box_br()
            _box_fim()
            print()
            if input("  › ").strip() == "CONFIRMAR":
                from .motor import _barra
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

        elif opt == "v":
            break

        else:
            pausa_erro("Opção inválida.")

    return cfg


# ── MENU INICIAL ──────────────────────────────────────────────
def menu_inicial(cfg):
    while True:
        cls()
        perfis        = list(cfg["perfis"].keys())
        n_perfis      = len(perfis)
        ur_status     = _status_ur()
        teclas_livres = len(TECLAS_BASE) * 8 - len(teclas_em_uso_global(cfg))

        _box_topo()
        # Cabeçalho com status UR alinhado à direita
        titulo = f"  FKB Remote  ·  v{VERSION}  ({BUILD})  ·  {AUTHOR}"
        status = ur_status
        espaco = W - 2 - len(titulo) - len(status)
        _box_row(f"{titulo}{' ' * max(espaco, 1)}{status}")
        _box_sep()
        # Linha de contadores
        cont = f"  PERFIS  ·  {n_perfis} de {MAX_PERFIS}"
        disp = f"{teclas_livres} teclas disponíveis  "
        espaco2 = W - 2 - len(cont) - len(disp)
        _box_row(f"{cont}{' ' * max(espaco2, 1)}{disp}")
        _box_sep("─")
        _box_br()

        if perfis:
            _box_row(f"   {'#':<4}  {'PERFIL':<18}  {'PROGRESSO':<20}  {'QTD':>5}  MODIFICADO")
            _box_row(f"   {'─'*3}  {'─'*18}  {'─'*20}  {'─'*5}  {'─'*16}")
            _box_br()
            for i, nome in enumerate(perfis, 1):
                d     = cfg["perfis"][nome]
                qtd   = len(d.get("teclas", []))
                mod   = _fmt_data(d.get("modificado", "—"))
                barra = _barra_progresso(qtd, MAX_TECLAS_POR_PERFIL)
                flag  = "  ⚠" if qtd < MIN_TECLAS_PERFIL else "   "
                nome_t = nome[:18]
                _box_row(f"   {i:<4}  {nome_t:<18}  {barra}  {qtd:>3}/{MAX_TECLAS_POR_PERFIL}{flag}  {mod}")
            _box_br()
        else:
            _box_row("   Nenhum perfil criado ainda.   Pressione [C] para começar.")
            _box_br()

        _box_sep()
        _box_row("  AÇÕES")
        _box_sep("─")
        _box_br()

        if n_perfis >= MAX_PERFIS:
            _label_c = "Limite atingido   "
        elif perfis_vazios_count(cfg) >= MAX_PERFIS_VAZIOS:
            _label_c = "Complete um perfil"
        else:
            _label_c = "Criar             "

        _box_row(f"   [C]  {_label_c}   [R]  Renomear        [E]  Excluir")
        _box_br()
        _box_row("   [O]  Configurações                                    [S]  Sair")
        if perfis:
            _box_br()
            _box_row("   ⚠ = perfil incompleto (menos de 6 teclas)")
        _box_br()
        _box_fim()
        print()
        opt = input("  › ").strip().lower()
        if not opt:
            continue

        try:
            idx = int(opt) - 1
            if 0 <= idx < n_perfis:
                cfg = menu_perfil(perfis[idx], cfg)
            else:
                pausa_erro("Número fora do intervalo.")
            continue
        except ValueError:
            pass

        if opt == "c":
            if n_perfis >= MAX_PERFIS:
                pausa_erro(f"Limite de {MAX_PERFIS} perfis atingido.")
                continue
            if perfis_vazios_count(cfg) >= MAX_PERFIS_VAZIOS:
                pausa_erro(f"{MAX_PERFIS_VAZIOS} perfis incompletos — atribua ao menos {MIN_TECLAS_PERFIL} teclas a um deles.")
                continue
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
            _box_topo()
            _box_row("  FKB Remote  ›  Renomear Perfil")
            _box_sep("─")
            _box_br()
            for i, p in enumerate(perfis, 1):
                _box_row(f"   {i}.   {p}")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [C]  Cancelar")
            _box_br()
            _box_fim()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c": continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < n_perfis:
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
            if n_perfis == 1:
                pausa_erro("Não é possível excluir o único perfil.")
                continue
            cls()
            _box_topo()
            _box_row("  FKB Remote  ›  Excluir Perfil")
            _box_sep("─")
            _box_br()
            for i, p in enumerate(perfis, 1):
                _box_row(f"   {i}.   {p}")
            _box_br()
            _box_sep()
            _box_br()
            _box_row("  Número                                                 [C]  Cancelar")
            _box_br()
            _box_fim()
            print()
            raw = input("  › ").strip().lower()
            if raw == "c": continue
            try:
                idx = int(raw) - 1
                if 0 <= idx < n_perfis:
                    nome = perfis[idx]
                    cls()
                    _box_topo()
                    _box_row("  FKB Remote  ›  ⚠  Confirmar Exclusão")
                    _box_sep("─")
                    _box_br()
                    _box_row(f"  Perfil:  {nome}")
                    _box_row( "  Esta ação não pode ser desfeita.")
                    _box_br()
                    _box_sep()
                    _box_br()
                    _box_row("   [S]  Excluir     [B]  Backup e excluir              [N]  Cancelar")
                    _box_br()
                    _box_fim()
                    print()
                    opt_e = tecla()
                    if opt_e == "b":
                        fazer_backup_perfil(nome, cfg, pedir_pasta_destino())
                        opt_e = "s"
                    if opt_e == "s":
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
