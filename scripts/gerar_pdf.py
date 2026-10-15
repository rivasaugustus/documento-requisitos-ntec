#!/usr/bin/env python3
"""Gera o PDF "[Requisitos] {projeto}" a partir de um markdown restrito,
usando o template do NTec (capa, logo, cores e marcadores do ValeDOC).

Uso:
    python gerar_pdf.py conteudo.md [--saida /mnt/user-data/outputs] [--forcar]

Formato do markdown: ver seção "Formato do markdown" no SKILL.md.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AQUI, "..", "assets", "template.docx")
SOFFICE_WRAPPER = "/mnt/skills/public/docx/scripts/office/soffice.py"

NAVY = "1B3A6B"

# Marcadores internos que nunca podem chegar a um anexo de contrato.
MARCADORES_PROIBIDOS = [
    (r"⚠", "símbolo de alerta"),
    (r"(?i)\ba confirmar\b", "'a confirmar'"),
    # Tags de fonte: o formato do Passo 7 ([Fathom · ...], [Granola · ...], [chat],
    # [doc: ...]) e o da validação técnica ([AT ...], [Aprof ...]).
    (r"\[(?:Fathom|Granola|chat\]|doc:|AT\b|Aprof)", "tag de fonte"),
    # Sensível a maiúsculas de propósito: "Todo usuário" é palavra inteira em
    # português, então só o limite de palavra não basta para evitar o falso positivo.
    (r"\bTODO\b|\bTBD\b", "pendência (TODO/TBD)"),
]


def inline_runs(texto, base_rpr=""):
    """Converte **negrito** em runs do Word."""
    partes = re.split(r"(\*\*[^*]+\*\*)", texto)
    runs = []
    for parte in partes:
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**"):
            conteudo = parte[2:-2]
            # o template separa o rótulo do texto com um espaço dentro do run em negrito
            runs.append(
                f'<w:r><w:rPr><w:b/><w:bCs/>{base_rpr}</w:rPr>'
                f'<w:t xml:space="preserve">{escape(conteudo)}</w:t></w:r>'
            )
        else:
            rpr = f"<w:rPr>{base_rpr}</w:rPr>" if base_rpr else ""
            runs.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(runs)


def p_h1(t):
    return (
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:keepNext/><w:keepLines/>'
        '<w:spacing w:after="180" w:before="320"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="{NAVY}"/><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(t)}</w:t></w:r></w:p>'
    )


def p_h2(t):
    return (
        '<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:keepLines/>'
        '<w:spacing w:after="120" w:before="240"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="{NAVY}"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(t)}</w:t></w:r></w:p>'
    )


def p_h3(t):
    if t.strip().lower() == "notas e abreviaturas":
        return (
            '<w:p><w:pPr><w:keepNext/><w:spacing w:after="120" w:before="200"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r></w:p>'
        )
    return (
        '<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:after="80" w:before="130"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="{NAVY}"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(t)}</w:t></w:r></w:p>'
    )


def p_corpo(t):
    return (
        '<w:p><w:pPr><w:keepLines/><w:spacing w:after="140" w:line="300"/><w:jc w:val="both"/></w:pPr>'
        f"{inline_runs(t)}</w:p>"
    )


def p_bullet(t, nivel=0, numerado=False):
    num_id = "3" if numerado and nivel == 0 else "2"
    depois = "110" if numerado else ("60" if nivel else "90")
    return (
        '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:keepLines/>'
        f'<w:numPr><w:ilvl w:val="{nivel}"/><w:numId w:val="{num_id}"/></w:numPr>'
        f'<w:spacing w:after="{depois}" w:line="290"/><w:jc w:val="both"/></w:pPr>'
        f"{inline_runs(t)}</w:p>"
    )


def ler_markdown(caminho):
    texto = open(caminho, encoding="utf-8").read()
    meta = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", texto, re.S)
    if not m:
        sys.exit("Erro: o markdown precisa começar com front matter (projeto e subtitulo).")
    for linha in m.group(1).splitlines():
        if ":" in linha:
            k, v = linha.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    for chave in ("projeto", "subtitulo"):
        if not meta.get(chave):
            sys.exit(f"Erro: front matter sem '{chave}'.")
    return meta, texto[m.end():]


def checar_marcadores(corpo):
    achados = []
    for n, linha in enumerate(corpo.splitlines(), 1):
        for padrao, nome in MARCADORES_PROIBIDOS:
            if re.search(padrao, linha):
                achados.append(f"  linha {n}: {nome} → {linha.strip()[:90]}")
    return achados


def montar_xml(corpo):
    xml = []
    em_exclusoes = False
    for linha in corpo.splitlines():
        if not linha.strip():
            continue
        if linha.startswith("# "):
            titulo = linha[2:].strip()
            em_exclusoes = "exclus" in titulo.lower()
            xml.append(p_h1(titulo))
        elif linha.startswith("## "):
            xml.append(p_h2(linha[3:].strip()))
        elif linha.startswith("### "):
            xml.append(p_h3(linha[4:].strip()))
        elif re.match(r"^\s{2,}- ", linha):
            xml.append(p_bullet(linha.strip()[2:], nivel=1))
        elif linha.startswith("- "):
            xml.append(p_bullet(linha[2:].strip(), numerado=em_exclusoes))
        else:
            xml.append(p_corpo(linha.strip()))
    return "".join(xml)


def converter_pdf(docx, pasta):
    cmds = []
    ultimo = None
    if os.path.exists(SOFFICE_WRAPPER):
        cmds.append([sys.executable, SOFFICE_WRAPPER])
    cmds.append(["soffice"])
    for base in cmds:
        try:
            subprocess.run(
                base + ["--headless", "--convert-to", "pdf", "--outdir", pasta, docx],
                check=True, capture_output=True, timeout=180,
                cwd=os.path.dirname(SOFFICE_WRAPPER) if base[0] == sys.executable else None,
            )
            pdf = os.path.splitext(docx)[0] + ".pdf"
            if os.path.exists(pdf):
                return pdf
        except Exception as e:  # tenta o próximo caminho
            ultimo = e
    sys.exit(f"Erro na conversão para PDF: {ultimo}")


def contar_paginas(pdf):
    try:
        out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
        return int(re.search(r"Pages:\s+(\d+)", out).group(1))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("--saida", default="/mnt/user-data/outputs")
    ap.add_argument("--forcar", action="store_true",
                    help="gera mesmo com marcadores internos no texto")
    args = ap.parse_args()

    meta, corpo = ler_markdown(args.markdown)
    achados = checar_marcadores(corpo)
    if achados and not args.forcar:
        print("Marcadores internos encontrados. Documento de contrato não pode levá-los:")
        print("\n".join(achados))
        print("Resolva no texto (ou pergunte ao usuário) e rode de novo.")
        sys.exit(2)

    projeto = meta["projeto"]
    nome = f"[Requisitos] {projeto}".replace("/", "-")
    trabalho = tempfile.mkdtemp(prefix="req_")
    docx_out = os.path.join(trabalho, nome + ".docx")

    with zipfile.ZipFile(TEMPLATE) as zin, zipfile.ZipFile(docx_out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            dados = zin.read(item.filename)
            if item.filename == "word/document.xml":
                doc = dados.decode("utf-8")
                doc = doc.replace("{{PROJETO}}", escape(projeto))
                doc = doc.replace("{{SUBTITULO}}", escape(meta["subtitulo"]))
                doc = doc.replace("<!--CONTEUDO-->", montar_xml(corpo))
                dados = doc.encode("utf-8")
            zout.writestr(item, dados)

    pdf = converter_pdf(docx_out, trabalho)
    os.makedirs(args.saida, exist_ok=True)
    destino = os.path.join(args.saida, nome + ".pdf")
    shutil.copy(pdf, destino)
    # guarda o .docx ao lado do markdown para a etapa de estilização
    shutil.copy(docx_out, os.path.join(os.path.dirname(os.path.abspath(args.markdown)), nome + ".docx"))

    paginas = contar_paginas(destino)
    print(f"PDF: {destino}")
    print(f"Páginas: {paginas} (inclui a capa)")
    if paginas and paginas > 10:
        print("ATENÇÃO: passou de 10 páginas. Corte densidade (RNs e detalhes de SID), nunca funcionalidade discutida.")


if __name__ == "__main__":
    main()
