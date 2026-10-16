#!/usr/bin/env python3
"""Gera o PDF "[Requisitos] {projeto}" a partir de um markdown restrito,
usando o template do NTec (capa, logo, cores e marcadores do ValeDOC).

Uso:
    python gerar_pdf.py conteudo.md [--saida PASTA] [--forcar]

Sem --saida, usa /mnt/user-data/outputs se ela existir (claude.ai); senão, a
pasta do markdown. Precisa do LibreOffice instalado para converter em PDF.

Formato do markdown: ver seção "Formato do markdown" no SKILL.md. O que estiver
fora desse dialeto é recusado, porque sairia literal no anexo de contrato.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AQUI, "..", "assets", "template.docx")
SOFFICE_WRAPPER = "/mnt/skills/public/docx/scripts/office/soffice.py"

NAVY = "1B3A6B"

# Marcadores internos que nunca podem chegar a um anexo de contrato.
MARCADORES_PROIBIDOS = [
    (r"⚠", "símbolo de alerta"),
    (r"(?i)\ba confirmar\b", "'a confirmar'"),
    # Tags de fonte: o formato do Passo 7 ([Fathom · ...], [Granola · ...],
    # [transcrição · ...], [chat], [doc: ...]) e o da validação técnica ([AT ...], [Aprof ...]).
    (r"(?i)\[(?:Fathom|Granola|transcri|chat\]|doc:|AT\b|Aprof)", "tag de fonte"),
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
    # devolve também quantas linhas o front matter ocupa, para as mensagens
    # de erro apontarem a linha do arquivo, não a do corpo
    return meta, texto[m.end():], texto[:m.end()].count("\n")


def checar_marcadores(corpo, inicio=1):
    achados = []
    for n, linha in enumerate(corpo.splitlines(), inicio):
        for padrao, nome in MARCADORES_PROIBIDOS:
            if re.search(padrao, linha):
                achados.append(f"  linha {n}: {nome} → {linha.strip()[:90]}")
    return achados


# Sintaxe fora do dialeto. Não há --forcar para isto: asterisco, barra ou
# cerquilha literal num anexo de contrato nunca é o que se quer.
SINTAXE_FORA_DO_DIALETO = [
    (r"^#{4,}", "título com 4+ '#': o dialeto vai até '###'"),
    (r"^#+[^#\s]", "título sem espaço depois de '#'"),
    (r"^[*+]\s", "item com '*' ou '+': use '- '"),
    (r"^\d+[.)]\s", "lista numerada: use '- ' (as Exclusões são numeradas sozinhas)"),
    (r"^\|", "tabela: não suportada"),
    (r"^>", "citação com '>': escreva como parágrafo"),
    (r"^(-{3,}|\*{3,}|_{3,})\s*$", "linha horizontal: não suportada"),
    (r"`", "crase ou bloco de código: não suportado"),
    (r"\[[^\]]*\]\([^)]*\)", "link markdown: não suportado"),
    (r"<[A-Za-z/][^>]*>", "tag HTML: não suportada"),
    (r"(^|[\s(])_[^_\s][^_]*_(?=$|[\s).,;:!?])", "itálico com '_': não suportado"),
]


def checar_dialeto(corpo, inicio=1):
    erros = []
    for n, linha in enumerate(corpo.splitlines(), inicio):
        if not linha.strip():
            continue
        if linha[0] in " \t" and not re.match(r"^(\t| {2,})- ", linha):
            erros.append(f"  linha {n}: linha indentada que não é sub-item ('  - ') → {linha.strip()[:80]}")
            continue
        conteudo = linha.strip()
        for padrao, nome in SINTAXE_FORA_DO_DIALETO:
            if re.search(padrao, conteudo):
                erros.append(f"  linha {n}: {nome} → {conteudo[:80]}")
        if conteudo.count("**") % 2:
            erros.append(f"  linha {n}: '**' sem par → {conteudo[:80]}")
        elif "*" in re.sub(r"\*\*[^*]+\*\*", "", conteudo):
            erros.append(f"  linha {n}: asterisco solto (itálico não é suportado) → {conteudo[:80]}")
    return erros


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
        elif re.match(r"^(\t| {2,})- ", linha):
            xml.append(p_bullet(linha.strip()[2:], nivel=1))
        elif linha.startswith("- "):
            xml.append(p_bullet(linha[2:].strip(), numerado=em_exclusoes))
        else:
            xml.append(p_corpo(linha.strip()))
    return "".join(xml)


def localizar_soffice():
    """Devolve o comando do LibreOffice disponível neste ambiente, ou None."""
    if os.path.exists(SOFFICE_WRAPPER):  # sandbox do claude.ai
        return [sys.executable, SOFFICE_WRAPPER]
    for nome in ("soffice", "libreoffice"):
        achado = shutil.which(nome)
        if achado:
            return [achado]
    candidatos = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return [c]
    return None


def converter_pdf(docx, pasta):
    base = localizar_soffice()
    if base is None:
        return None
    try:
        subprocess.run(
            base + ["--headless", "--convert-to", "pdf", "--outdir", pasta, docx],
            check=True, capture_output=True, timeout=180,
            cwd=os.path.dirname(SOFFICE_WRAPPER) if base[0] == sys.executable else None,
        )
    except Exception as e:
        sys.exit(f"Erro na conversão para PDF ({base[0]}): {e}")
    pdf = os.path.splitext(docx)[0] + ".pdf"
    return pdf if os.path.exists(pdf) else None


def contar_paginas(pdf):
    try:
        out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
        return int(re.search(r"Pages:\s+(\d+)", out).group(1))
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf).pages)
    except Exception:
        pass
    try:
        dados = open(pdf, "rb").read()
        return len(re.findall(rb"/Type\s*/Page(?![s\w])", dados)) or None
    except Exception:
        return None


def saida_padrao(markdown):
    """Pasta que o usuário vê: outputs no claude.ai; senão, a pasta do markdown."""
    if os.path.isdir("/mnt/user-data/outputs"):
        return "/mnt/user-data/outputs"
    return os.path.dirname(os.path.abspath(markdown))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("--saida", default=None,
                    help="pasta do PDF (padrão: /mnt/user-data/outputs se existir; senão, a do markdown)")
    ap.add_argument("--forcar", action="store_true",
                    help="gera mesmo com marcadores internos no texto")
    args = ap.parse_args()

    meta, corpo, linhas_cabecalho = ler_markdown(args.markdown)
    inicio = linhas_cabecalho + 1
    saida = args.saida or saida_padrao(args.markdown)

    erros = checar_dialeto(corpo, inicio)
    if erros:
        print("Sintaxe fora do dialeto. Sairia literal no PDF:")
        print("\n".join(erros))
        print("Reescreva essas linhas no formato do SKILL.md e rode de novo.")
        sys.exit(3)

    achados = checar_marcadores(corpo, inicio)
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

    pasta_md = os.path.dirname(os.path.abspath(args.markdown))
    # guarda o .docx ao lado do markdown: é sobre ele que se fazem ajustes visuais depois
    docx_guardado = os.path.join(pasta_md, nome + ".docx")
    shutil.copy(docx_out, docx_guardado)

    pdf = converter_pdf(docx_out, trabalho)
    if pdf is None:
        print("LibreOffice não encontrado neste computador, então o PDF não foi gerado.")
        print(f"O .docx está em: {docx_guardado}")
        print("Instale o LibreOffice (libreoffice.org) e rode de novo, ou exporte o .docx para PDF pelo Word.")
        sys.exit(4)

    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, nome + ".pdf")
    shutil.copy(pdf, destino)

    paginas = contar_paginas(destino)
    print(f"PDF: {destino}")
    print(f"DOCX: {docx_guardado}")
    print(f"Páginas: {paginas} (inclui a capa)")
    if paginas and paginas > 10:
        print("ATENÇÃO: passou de 10 páginas. Corte densidade (RNs e detalhes de SID), nunca funcionalidade discutida.")

if __name__ == "__main__":
    main()
