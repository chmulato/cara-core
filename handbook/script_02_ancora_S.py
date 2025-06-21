#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir os links de âncora internos do arquivo SERVICEGUIDE.html,
garantindo que os hrefs do sumário apontem para os IDs reais dos títulos.

Funcionalidades:
- Mapeia títulos para seus IDs reais no HTML.
- Ajusta os links de âncora para compatibilidade e navegação correta.

Autor: Christian Vladimir Uhdre Mulato
Data: 21/06/2025
Licença: MIT
"""
import re
import unicodedata

def pandoc_slugify(text):
    # Remove acentos
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Minúsculas
    text = text.lower()
    # Remove tudo que não é letra, número, espaço ou hífen
    text = re.sub(r'[^\w\s-]', '', text)
    # Substitui espaços e underscores por hífen
    text = re.sub(r'[\s_]+', '-', text)
    # Remove hífens duplicados
    text = re.sub(r'-+', '-', text)
    # Remove hífens do início/fim
    text = text.strip('-')
    return text

with open('SERVICEGUIDE.html', encoding='utf-8') as f:
    html = f.read()

# Mapeia slug do título para o id real do HTML
slug_to_id = {}
for match in re.finditer(r'<h([1-6])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', html, re.DOTALL):
    real_id = match.group(2)
    title = re.sub('<[^<]+?>', '', match.group(3)).strip()
    slug = pandoc_slugify(title)
    slug_to_id[slug] = real_id

def replace_anchor(match):
    anchor = match.group(1)
    # Se já está correto, mantém
    if anchor in slug_to_id.values():
        return f'href="#{anchor}"'
    # Tenta corrigir slug duplo para slug simples
    anchor_slug = pandoc_slugify(anchor)
    if anchor_slug in slug_to_id:
        return f'href="#{slug_to_id[anchor_slug]}"'
    return f'href="#{anchor}"'

html_corrigido = re.sub(r'href="#([^"]+)"', replace_anchor, html)

with open('SERVICEGUIDE.html', 'w', encoding='utf-8') as f:
    f.write(html_corrigido)

print('Links de âncora corrigidos!')