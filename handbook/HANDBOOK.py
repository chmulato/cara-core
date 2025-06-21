#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HANDBOOK.py

Este script automatiza a conversão do arquivo HANDBOOK.md (em Markdown) para um arquivo HTML responsivo e moderno,
adequado para leitura em navegadores e dispositivos móveis. Ele também corrige e normaliza as âncoras internas
(links do sumário e títulos), garantindo que todos os links naveguem corretamente para as seções do documento.

Funcionalidades principais:
- Converte HANDBOOK.md em HANDBOOK.html usando Pandoc.
- Insere CSS responsivo e meta viewport para melhor visualização em tablets e smartphones.
- Normaliza e corrige âncoras do sumário e dos títulos para compatibilidade total.
- Gera um HTML pronto para publicação ou distribuição.

Pré-requisitos:
- Python 3.x
- Pandoc instalado e disponível no PATH do sistema operacional.
- O arquivo HANDBOOK.md deve estar no mesmo diretório deste script.

Autor: Christian Vladimir Uhdre Mulato
Data: 21/06/2025
Licença: MIT
"""
import subprocess
import re
import unicodedata

md_file = "HANDBOOK.md"
html_file = "HANDBOOK.html"

css_content = """
body {
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    background: #f4f6fb;
    color: #222;
    margin: 0;
    padding: 0 1.5em;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.7;
}
h1, h2, h3, h4 {
    color: #2b579a;
    font-weight: 700;
    margin-top: 2em;
    margin-bottom: 0.5em;
    line-height: 1.2;
}
h1 {
    font-size: 2.3em;
    border-bottom: 2px solid #e1e4ea;
    padding-bottom: 0.3em;
}
h2 {
    font-size: 1.7em;
    border-bottom: 1px solid #e1e4ea;
    padding-bottom: 0.2em;
}
h3 {
    font-size: 1.3em;
}
h4 {
    font-size: 1.1em;
}
a {
    color: #0078d4;
    text-decoration: none;
    transition: color 0.2s;
}
a:hover, a:focus {
    color: #005a9e;
    text-decoration: underline;
}
code, pre {
    background: #f1f3f7;
    color: #c7254e;
    font-family: 'Fira Mono', 'Consolas', monospace;
    border-radius: 4px;
    padding: 0.2em 0.4em;
}
pre {
    padding: 1em;
    overflow-x: auto;
    margin: 1em 0;
}
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.07);
}
ul, ol {
    margin-left: 2em;
    margin-bottom: 1em;
}
li {
    margin-bottom: 0.5em;
}
blockquote {
    border-left: 4px solid #b4c7e7;
    background: #f8fafc;
    color: #555;
    margin: 1.5em 0;
    padding: 0.8em 1.2em;
    border-radius: 4px;
}
hr {
    border: none;
    border-top: 1px solid #e1e4ea;
    margin: 2em 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
    background: #fff;
}
th, td {
    border: 1px solid #e1e4ea;
    padding: 0.6em 1em;
    text-align: left;
}
th {
    background: #f1f3f7;
    font-weight: 600;
}
@media (max-width: 900px) {
    body {
        padding: 0 0.5em;
        font-size: 1.07em;
    }
    h1 { font-size: 1.7em; }
    h2 { font-size: 1.3em; }
    h3 { font-size: 1.1em; }
    table, th, td {
        font-size: 0.97em;
    }
}
"""

def normalize_anchor(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-zA-Z0-9\-]', '', text)
    return text.lower()

def fix_toc_anchors(html):
    def repl(match):
        label = match.group(2)
        anchor = normalize_anchor(label)
        return f'{match.group(1)}#{anchor}{match.group(3)}'
    return re.sub(r'(<a href=")#([^"]+)(">)', repl, html)

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    return text

def corrige_ancoras_ids(html):
    slug_to_id = {}
    for match in re.finditer(r'<h([1-6])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', html, re.DOTALL):
        real_id = match.group(2)
        title = re.sub('<[^<]+?>', '', match.group(3)).strip()
        slug = slugify(title)
        slug_to_id[slug] = real_id

    def replace_anchor(match):
        anchor = match.group(1)
        if anchor in slug_to_id.values():
            return f'href="#{anchor}"'
        anchor_slug = slugify(anchor)
        if anchor_slug in slug_to_id:
            return f'href="#{slug_to_id[anchor_slug]}"'
        return f'href="#{anchor}"'

    return re.sub(r'href="#([^"]+)"', replace_anchor, html)

def main():
    # 1. Converter o Markdown em HTML usando Pandoc
    subprocess.run([
        "pandoc", md_file, "-o", html_file, "--standalone"
    ], check=True)

    # 2. Ler o HTML gerado
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    # 3. Corrigir âncoras do sumário (remover acentos, espaços, etc.)
    html = fix_toc_anchors(html)

    # 4. Inserir o CSS responsivo e a meta viewport antes do </head>
    meta_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    style_block = f"{meta_viewport}<style>\n{css_content}\n</style>\n"

    if "<head>" in html:
        html = html.replace("<head>", f"<head>\n{style_block}", 1)
    else:
        html = html.replace("<body>", f"<head>\n{style_block}</head>\n<body>", 1)

    # 5. Corrigir os links de âncora para os IDs reais dos títulos
    html = corrige_ancoras_ids(html)

    # 6. Salvar o HTML final
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Arquivo HTML gerado e âncoras corrigidas: {html_file}")

if __name__ == "__main__":
    main()