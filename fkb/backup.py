import os
import json
import glob
import time

import sys

from .constants import VERSION
from .ui import (
    cls, br, msg_ok, msg_info, msg_aviso, pausa_erro,
    tecla, aguardar_ou_timeout,
)
from .config import _sanitizar_nome
from .perfil import reconstruir_perfil
from .motor import reiniciar_servidor_ur

def pasta_exe():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


# ── DESTINO ───────────────────────────────────────────────────
def pedir_pasta_destino():
    """Pergunta ao usuário onde salvar o backup. Retorna caminho ou None se cancelado."""
    cls()
    br()
    pasta_padrao = pasta_exe()
    print("  Pasta de destino — arraste ou cole o caminho.")
    print(f"  Enter em branco = mesma pasta do executável:")
    print(f"  ({pasta_padrao})")
    br()
    print("  [C] Cancelar")
    br()
    pasta = input("  › ").strip('"').strip()
    if pasta.lower() == "c":
        msg_info("Backup cancelado.")
        aguardar_ou_timeout(1)
        return None
    if not pasta:
        return pasta_padrao
    if not os.path.isdir(pasta):
        msg_aviso("Pasta inválida. Usando pasta do executável.")
        aguardar_ou_timeout(2)
        return pasta_padrao
    return pasta

# ── BACKUP DE PERFIL ──────────────────────────────────────────
def fazer_backup_perfil(nome, cfg, pasta_destino):
    if pasta_destino is None:
        return False
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

# ── BACKUP COMPLETO ───────────────────────────────────────────
def _limpar_backups_completos(pasta):
    backups = sorted(glob.glob(os.path.join(pasta, "fkb-backup-completo-*.json")))
    while len(backups) > 3:
        try: os.remove(backups.pop(0))
        except Exception: pass

def fazer_backup_tudo(cfg, pasta_destino):
    if pasta_destino is None:
        return False
    ts      = time.strftime("%Y-%m-%d-%Hh%M")
    caminho = os.path.join(pasta_destino, f"fkb-backup-completo-{ts}.json")
    payload = {"versao": VERSION, "data": ts, "perfis": cfg["perfis"]}
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        msg_ok(f"Backup completo salvo: {caminho}")
        _limpar_backups_completos(pasta_destino)
        return True
    except Exception as e:
        pausa_erro(f"Erro ao salvar backup completo: {e}")
        return False

# ── RESTAURAÇÃO ───────────────────────────────────────────────
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
            cfg = _restaurar_perfil_unico(
                _sanitizar_nome(nome) or nome[:20], dados, cfg, reiniciar=False
            )
        reiniciar_servidor_ur()
    elif "perfil" in payload and "dados" in payload:
        cfg = _restaurar_perfil_unico(
            _sanitizar_nome(payload["perfil"]) or payload["perfil"][:20],
            payload["dados"], cfg, reiniciar=True
        )
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
