import os, time
from io import BytesIO

from .constants import (
    W, AUTHOR, EXE_PATH, REMOTES_DIR, FORMATOS_IMAGEM,
    ORDEM_ALFABETICA,
)
from .ui import msg_ok, pausa_erro, aguardar_ou_timeout
from .config import ordenar_teclas, salvar_config
from .motor import reiniciar_servidor_ur


def perfil_dir(nome):
    return os.path.join(REMOTES_DIR, f"FKB-{nome}")


def _xml_escape(txt):
    """Escapa caracteres especiais para uso seguro em atributos XML."""
    return (txt.replace("&", "&amp;")
               .replace('"', "&quot;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))


def reconstruir_perfil(nome, cfg, _reiniciar=True):
    dados = cfg["perfis"][nome]
    modo  = dados.get("ordem", ORDEM_ALFABETICA)

    if not isinstance(dados.get("teclas"), list):
        dados["teclas"] = []
    if not isinstance(dados.get("ordem_adicao"), list):
        dados["ordem_adicao"] = []

    exibir = ordenar_teclas(dados["teclas"], modo, dados["ordem_adicao"])
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


def aplicar_icone(nome_perfil):
    import requests
    from PIL import Image

    pasta    = perfil_dir(nome_perfil)
    formatos = ", ".join(sorted(FORMATOS_IMAGEM))
    from .ui import cls, br
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
