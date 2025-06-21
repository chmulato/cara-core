#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter um arquivo Markdown (HANDBOOK.md) em HTML responsivo para leitura em tablets e dispositivos móveis.

Funcionalidades:
- Converte o arquivo HANDBOOK.md em HANDBOOK.html usando Pandoc.
- Corrige os links âncora do sumário para garantir compatibilidade.
- Insere CSS responsivo e meta viewport no HTML final.

Autor: Christian Vladimir Uhdre Mulato
Data: 20/06/2025
Licença: MIT
"""
import subprocess
import re

# Caminhos dos arquivos
md_file = "HANDBOOK.md"
html_file = "HANDBOOK.html"

# CSS responsivo para leitura em tablet
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

# 1. Converter o Markdown em HTML usando Pandoc
subprocess.run([
    "pandoc", md_file, "-o", html_file, "--standalone"
], check=True)

# 2. Ler o HTML gerado
with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

# 3. Corrigir âncoras do sumário (remover acentos, espaços, etc.)
def normalize_anchor(text):
    import unicodedata
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

html = fix_toc_anchors(html)

# 4. Inserir o CSS responsivo e a meta viewport antes do </head>
meta_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
style_block = f"{meta_viewport}<style>\n{css_content}\n</style>\n"

if "<head>" in html:
    html = html.replace("<head>", f"<head>\n{style_block}", 1)
else:
    html = html.replace("<body>", f"<head>\n{style_block}</head>\n<body>", 1)

# 5. Salvar o HTML final
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Arquivo HTML gerado com CSS responsivo: {html_file}")