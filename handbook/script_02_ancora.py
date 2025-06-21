#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir os links de âncora internos do arquivo HANDBOOK.html,
garantindo que os hrefs do sumário apontem para os IDs reais dos títulos.

Funcionalidades:
- Mapeia títulos para seus IDs reais no HTML.
- Ajusta os links de âncora para compatibilidade e navegação correta.

Autor: Christian Vladimir Uhdre Mulato
Data: 20/06/2025
Licença: MIT
"""
import re
import unicodedata

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    return text

with open('HANDBOOK.html', encoding='utf-8') as f:
    html = f.read()

# Mapeia slug do título para o id real do HTML
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

html_corrigido = re.sub(r'href="#([^"]+)"', replace_anchor, html)

with open('HANDBOOK.html', 'w', encoding='utf-8') as f:
    f.write(html_corrigido)

print('Links de âncora corrigidos!')