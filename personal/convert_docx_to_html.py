"""convert_docx_to_html.py

Gerador estático de artigos a partir de arquivos DOCX.

Resumo
======
Converte todos os arquivos `.docx` localizados na pasta `docx/` em páginas HTML
modernas dentro de `html/`, aplicando layout responsivo, SEO, blocos de código
com highlight, geração de páginas auxiliares (índice cronológico, páginas de
tag, about, feeds RSS/Atom, sitemap/robots) e uma imagem social (OG) em SVG.

Características Principais
--------------------------
1. Limpeza prévia completa: remove HTML antigos, imagens derivadas e SVGs OG
    (preserva somente a foto única do autor) antes de cada execução, garantindo
    rebuild determinístico.
2. Extração de imagens incorporadas em DOCX para `html/img/<slug>-NN.ext`.
3. Foto única do autor (configurável) injetada no final de cada artigo e usada
    como `og:image` / Twitter Card / JSON-LD.
4. Heurísticas para normalizar e unir fragmentos de código em blocos
    `<pre><code>` + detecção simples de linguagem (Java, Python, VBA, Bash,
    JSON, XML, diagramas ASCII) + highlight via CDN (Highlight.js) + botão
    "copiar" e numeração de linhas.
5. SEO: meta description, keywords derivadas (stopwords pt), Open Graph,
    Twitter, JSON-LD Article e canonical links.
6. Páginas de tag: geradas a partir das primeiras N keywords (limite
    `MAX_TAGS_PER_ARTICLE`).
7. Índice cronológico agrupado (Ano → Mês) usando prefixo de data no nome do
    arquivo: `YYYY_MM_DD_Titulo.docx`.
8. Feeds & descoberta: `sitemap.xml`, `robots.txt`, `feed.xml` (RSS),
    `atom.xml` (Atom) com timestamps timezone-aware (UTC).
9. Limpeza pós-geração de imagens órfãs preservando a foto do autor.
10. Poda de artigos cujo DOCX foi removido (em conjunto com rebuild completo).

Variáveis de Ambiente
---------------------
ARTICLES_BASE_URL      URL pública base (ex: https://meusite.com)
ARTICLES_AUTHOR_NAME   Nome do autor (meta/JSON-LD/feeds)
ARTICLES_SITE_TITLE    Título geral (feeds / OG SVG)
ARTICLES_FORCE_REBUILD (Legado) Força reconversão; atualmente redundante pois
                                o rebuild já é completo após limpeza prévia.
ARTICLES_AUTHOR_PHOTO  Caminho local ou URL da foto única do autor. Se local e
                                fora de `html/`, será copiada para
                                `html/img/photo_autor/`.

Fluxo de Execução (main)
------------------------
1. Verifica pasta `docx/` e prepara `html/`.
2. Resolve foto do autor (copiando se necessário).
3. Carrega manifesto `_manifest.json` (mantido para futura reutilização, mas
    limpo pela etapa seguinte).
4. Poda registros de DOCX inexistentes.
5. Limpeza prévia total (`pre_clean_articles`).
6. Para cada DOCX: converte com Mammoth → pós-processa com BeautifulSoup:
    - Ajusta título, descrições, tempo de leitura.
    - Normaliza tabelas, blocos de código e une fragmentos.
    - Detecta linguagem e aplica classes highlight.
    - Gera meta tags + JSON-LD.
    - Anexa bloco padronizado de autor.
    - Gera imagem OG (SVG) individual.
7. Gera index, páginas de tag, about.
8. Gera sitemap / robots / feeds.
9. Limpa imagens órfãs não referenciadas.
10. Enforce da foto de autor em cada artigo.

Principais Funções
------------------
convert_file()                Converte DOCX → HTML fragment + pós-processamento.
generate_index()              Cria página inicial agrupada.
build_tag_pages()             Gera páginas `tag-*.html`.
create_og_image_svg()         Produz SVG para compartilhamento.
generate_sitemap_and_feeds()  Cria sitemap, RSS e Atom.
clean_unused_images()         Remove imagens não referenciadas.
enforce_author_photo()        Garante bloco de autor unificado.
pre_clean_articles()          Limpa geração anterior (exceto foto autor).

Extensões Futuras Sugeridas
---------------------------
- Reativar modo incremental removendo a limpeza prévia ou tornando-a opcional.
- Minificação de HTML/CSS/JS, otimização e conversão de imagens (WebP/AVIF).
- Filtro de frequência mínima para tags.
- Geração de versões AMP / PDF.

Licença: MIT (ver arquivo LICENSE).
"""

import os
import re
import unicodedata
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import mammoth
from bs4 import BeautifulSoup
from bs4.element import NavigableString

DOCX_DIR = Path("docx")
HTML_DIR = Path("html")
IMG_SUBDIR_NAME = "img"  # Dentro da pasta HTML
BASE_URL = os.environ.get("ARTICLES_BASE_URL", "https://example.com")  # Ajuste conforme o domínio real
AUTHOR_NAME = os.environ.get("ARTICLES_AUTHOR_NAME", "Christian Vladimir Uhdre Mulato")
SITE_TITLE = os.environ.get("ARTICLES_SITE_TITLE", "Artigos")
FORCE_REBUILD = os.environ.get("ARTICLES_FORCE_REBUILD", "0") == "1"
MANIFEST_FILE = "_manifest.json"
MAX_TAGS_PER_ARTICLE = 8
AUTHOR_PHOTO_INPUT = os.environ.get("ARTICLES_AUTHOR_PHOTO", "author.jpg")  # Pode ser URL absoluta ou caminho local
AUTHOR_PHOTO_REL = ""  # Caminho relativo dentro de html/ (ex: img/author.jpg)
AUTHOR_PHOTO_URL = ""  # URL completa para JSON-LD
AUTHOR_PHOTO_SUBDIR = "photo_autor"  # subpasta dentro de img para armazenar a foto do autor

# Stopwords básicas PT para geração de keywords simples
STOPWORDS = set("a o os as um uma umas uns de da do das dos e em para por com sem sob sobre entre após antes contra se que quem cujo cuja cujo cujo cujo este esta isso isso isto aquele aquela aqueles aquelas ao aos às à mais menos muito muita muitos muitas já também como quando onde porque porquê qual quais portanto porém todavia contudo além ainda ser ter estar são foi foram era eram será serão sua seu seus suas eu você voces voces nós nos eles elas ele ela isto isso aquele aquela aqui aí ali lá mesmo mesma mesmos mesmas cada todo toda todos todas dentro fora frente trás atrás ante desde até enquanto cuja cujo cujos cujas cuja".split())

CUSTOM_CSS = """
/* Reset & base */
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin:0; font-family: system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif; line-height:1.6; background: var(--bg); color: var(--text); scroll-behavior:smooth; }

:root { --bg:#f8f9fb; --bg-alt:#ffffff; --text:#1f2329; --text-soft:#4a5565; --border:#d9dde3; --brand:#0b63c5; --brand-accent:#084f9d; --code-bg:#f3f5f7; --radius:12px; --shadow:0 2px 4px rgba(0,0,0,.04),0 8px 24px -8px rgba(0,0,0,.08); color-scheme: light dark; }
@media (prefers-color-scheme: dark) { :root { --bg:#0f141a; --bg-alt:#1b232c; --text:#e6ebf0; --text-soft:#a5b3c2; --border:#2d3b47; --brand:#5aa4ff; --brand-accent:#2d7dd3; --code-bg:#1f2730; --shadow:0 2px 4px rgba(0,0,0,.6),0 8px 24px -8px rgba(0,0,0,.6);} }

header.site { backdrop-filter: blur(12px); background: linear-gradient(90deg,var(--bg-alt),var(--bg)); position:sticky; top:0; z-index:10; border-bottom:1px solid var(--border); padding:.75rem 1rem; display:flex; gap:1rem; align-items:center; }
header.site a.brand { font-weight:600; font-size:1rem; color:var(--brand); text-decoration:none; }
header.site a.brand:hover { color:var(--brand-accent); }
header.site .meta { margin-left:auto; font-size:.75rem; color:var(--text-soft); white-space:nowrap; }

main { max-width: 74ch; margin: clamp(1rem,4vw,3rem) auto 4rem; padding:0 1rem; }
article { background: var(--bg-alt); border:1px solid var(--border); border-radius: var(--radius); padding: clamp(1.25rem,2.5vw,2.5rem); box-shadow: var(--shadow); }
article h1 { font-size: clamp(1.9rem,4vw,2.6rem); line-height:1.15; margin:0 0 1.25rem; letter-spacing:-.5px; }
article h2 { margin:2.4rem 0 1rem; font-size: clamp(1.35rem,2.3vw,1.85rem); line-height:1.25; }
article h3 { margin:2rem 0 .75rem; font-size: clamp(1.15rem,2vw,1.4rem); }
article h4 { margin:1.5rem 0 .5rem; font-size:1.05rem; letter-spacing:.5px; }
article p { margin:0 0 1.15rem; text-wrap:pretty; }
article p + p { text-indent:0; }

article a { color:var(--brand); text-decoration:none; }
article a:hover { text-decoration:underline; color:var(--brand-accent); }

blockquote { margin:2rem 0; padding:1rem 1.25rem; border-left:5px solid var(--brand); background: linear-gradient(135deg,var(--code-bg),var(--bg)); border-radius:0 var(--radius) var(--radius) 0; font-style:italic; }

code, pre { font-family: ui-monospace, SFMono-Regular, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'Courier New', monospace; font-size:.9rem; }
pre { background: var(--code-bg); padding:1rem 1.25rem; border-radius: var(--radius); overflow-x:auto; line-height:1.4; position:relative; }
pre code { background:transparent; padding:0; }
code { background: var(--code-bg); padding:.25rem .5rem; border-radius:6px; }

img, video { max-width:100%; height:auto; border-radius:6px; }
figure { margin:2rem 0; }
figcaption { text-align:center; font-size:.8rem; color:var(--text-soft); margin-top:.5rem; }

table { border-collapse: collapse; width:100%; font-size:.95rem; }
table thead th { background: var(--code-bg); }
th, td { border:1px solid var(--border); padding:.6rem .75rem; text-align:left; vertical-align:top; }
.table-wrapper { overflow-x:auto; margin:2rem 0; border:1px solid var(--border); border-radius:8px; }

ul, ol { padding-left:1.4rem; margin:1.25rem 0 1.25rem; }
li { margin:.4rem 0; }

hr { border:none; border-top:1px solid var(--border); margin:3rem 0; }

footer.site { margin:3rem auto 0; max-width:74ch; padding:2rem 1rem 4rem; font-size:.8rem; color:var(--text-soft); }
footer.site a { color:inherit; text-decoration:none; }
footer.site a:hover { color:var(--brand); }

.reading-progress { position:fixed; top:0; left:0; height:4px; background:linear-gradient(90deg,var(--brand),var(--brand-accent)); width:0; z-index:999; box-shadow:0 0 0 1px rgba(0,0,0,.05); }

/* Author box */
.author-box{display:flex;align-items:center;gap:1rem;margin:2.5rem 0 0;padding:1rem 1.1rem;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);}
.author-box .author-photo{width:68px;height:68px;border-radius:50%;object-fit:cover;border:2px solid var(--border);background:var(--bg-alt);}
.author-box .author-meta{font-size:.8rem;color:var(--text-soft);}
.author-box .author-meta strong{display:block;color:var(--text);font-size:.85rem;}

@media (max-width: 640px) {
    article { padding:1.25rem 1.1rem; }
    header.site { padding:.55rem .85rem; }
    header.site a.brand { font-size:.9rem; }
}
""".strip()

PROGRESS_SCRIPT = ("<script>\"use strict\";" 
                                     "const rp=document.getElementById('rp');const h=document.documentElement;" 
                                     "addEventListener('scroll',()=>{const st=h.scrollTop;const sh=h.scrollHeight-h.clientHeight;" 
                                     "const p=sh?(st/sh)*100:0;rp.style.width=p+'%';},{passive:true});" 
                                     "</script>")

HIGHLIGHT_HEAD = """
<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css\" media=\"(prefers-color-scheme: light)\">
<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark-dimmed.min.css\" media=\"(prefers-color-scheme: dark)\">
<style>
pre code { display:block; counter-reset: line; white-space: pre; }
pre code span.ln { display:block; padding-left:.5rem; position:relative; }
pre code span.ln:before { counter-increment: line; content: counter(line); position:absolute; left:-3.2rem; width:2.8rem; text-align:right; color:var(--text-soft); font-size:.7rem; user-select:none; }
pre { position:relative; }
pre .copy-btn { position:absolute; top:.4rem; right:.5rem; background:var(--bg-alt); border:1px solid var(--border); font-size:.65rem; padding:.25rem .5rem; border-radius:6px; cursor:pointer; opacity:.75; }
pre:hover .copy-btn { opacity:1; }
</style>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/java.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/xml.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/json.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/bash.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/python.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/vba.min.js\"></script>
<script>
document.addEventListener('DOMContentLoaded',()=>{
    document.querySelectorAll('pre code').forEach(block=>{ hljs.highlightElement(block); addCopy(block); addLineNumbers(block); });
    function addCopy(block){
        if(block.parentElement.querySelector('.copy-btn')) return; const btn=document.createElement('button');btn.textContent='copiar';btn.className='copy-btn';btn.addEventListener('click',()=>{navigator.clipboard.writeText(block.innerText.trim());btn.textContent='copiado!';setTimeout(()=>btn.textContent='copiar',1600);});block.parentElement.appendChild(btn);}
    function addLineNumbers(block){
        const html = block.innerHTML.split(/\n/).map(l=>'<span class="ln">'+(l||'\u00A0')+'</span>').join('\n');
        block.innerHTML = html; }
});
</script>
""".strip()

HTML_SHELL = """<!DOCTYPE html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<meta name=\"color-scheme\" content=\"light dark\" />
<title>{title}</title>
<meta name=\"description\" content=\"{description}\" />
<style>{css}</style>
{extra_head}
</head><body>
<div class=reading-progress id=rp></div>
<header class=site><a class=brand href=\"index.html\">Início</a><span class=meta>{reading_time}</span></header>
<main><article>
{body}
</article></main>
<footer class=site>Gerado automaticamente. Leitura estimada: {reading_time}. &middot; <a href=\"index.html\">Voltar ao índice</a></footer>
{script}
</body></html>"""

def slugify(text: str) -> str:
    text_norm = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text_norm = re.sub(r'[^a-zA-Z0-9]+', '-', text_norm).strip('-').lower()
    return text_norm or 'artigo'


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def convert_file(docx_path: Path, out_dir: Path):
    """Converte um arquivo DOCX e retorna (out_path, title)."""
    global AUTHOR_PHOTO_URL, AUTHOR_PHOTO_REL
    img_dir = out_dir / IMG_SUBDIR_NAME
    img_dir.mkdir(exist_ok=True)

    slug_base = slugify(docx_path.stem)
    image_counter = {"n": 0}

    def image_handler(image):  # mammoth image callback
        content_type = getattr(image, 'content_type', 'image/png')
        ext = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/bmp': '.bmp',
            'image/webp': '.webp'
        }.get(content_type.lower(), '.bin')
        image_counter['n'] += 1
        fname = f"{slug_base}-{image_counter['n']:02d}{ext}"
        target = img_dir / fname
        try:
            with image.open() as img_bytes:  # type: ignore[attr-defined]
                data = img_bytes.read()
            with target.open('wb') as out:
                out.write(data)
        except Exception as e:  # fallback: skip saving
            return {"src": f"data:image/png;base64,", "alt": f"(erro imagem {e})"}
        return {"src": f"{IMG_SUBDIR_NAME}/{fname}", "alt": docx_path.stem}

    with docx_path.open('rb') as f:
        result = mammoth.convert_to_html(f, convert_image=mammoth.images.img_element(image_handler))
    html_fragment = result.value  # type: ignore

    soup = BeautifulSoup(html_fragment, 'html.parser')

    # Use first h1/h2 or filename as title
    heading = soup.find(['h1', 'h2'])
    title = heading.get_text(strip=True) if heading else docx_path.stem

    # Ensure only one h1 at top
    if heading and heading.name != 'h1':
        heading.name = 'h1'

    # Descrição breve (primeiros ~30 palavras)
    text_words = soup.get_text(" ").split()
    description = " ".join(text_words[:30]) if text_words else title
    # Tempo de leitura (200 wpm)
    word_count = len(text_words)
    minutes = max(1, round(word_count / 200))
    reading_time = f"{minutes} min"

    # Envelopa tabelas em .table-wrapper
    for table in soup.find_all('table'):
        wrapper = soup.new_tag('div', **{'class': 'table-wrapper'})
        table.replace_with(wrapper)
        wrapper.append(table)

    # Normaliza blocos de código: garante <pre><code>
    for pre in soup.find_all('pre'):
        if pre.code:
            continue
        code_tag = soup.new_tag('code')
        code_tag.string = pre.get_text('\n')
        pre.clear()
        pre.append(code_tag)

    # Heurística para criar blocos de código de parágrafos monoespaçados (simples)
    candidate_paragraphs = []
    for p in list(soup.find_all('p')):
        txt = p.get_text()
        if len(txt) < 12:
            continue
        signals = sum(s in txt for s in [';', '{', '}', 'public ', 'private ', 'class ', 'def ', 'import ', 'package ', 'System.out', '->'])
        if signals >= 2 and ' ' in txt:
            candidate_paragraphs.append(p)
    for p in candidate_paragraphs:
        code_tag = soup.new_tag('code')
        code_tag.string = p.get_text()
        pre = soup.new_tag('pre')
        pre.append(code_tag)
        p.replace_with(pre)

    # Mescla sequências de linhas de código fragmentadas dentro de cada <article>
    def is_code_line(text: str) -> bool:
        t = text.rstrip('\n').rstrip()
        if not t:
            return False
        if len(t) > 160:  # muito longo para ser linha de código típica
            return False
        starters = ("//", "#", "/*", "function ", "const ", "let ", "var ", "if ", "for ", "while ", "return", "class ", "public ", "private ", "import ", "package ", "def ")
        if t.startswith(starters):
            return True
        if t in ("}", "};", ");", "{", "})", "]}"):
            return True
        if t.endswith('{') and len(t.split()) < 14:
            return True
        if re.match(r'^\s*[A-Za-z_][\w\.]*\s*=\s*.+;', t):  # atribuição ;
            return True
        if re.match(r'^\s*"[A-Za-z0-9_]+"\s*:\s*', t):  # linha JSON chave:
            return True
        # Linha indentada que parece código (4+ espaços + caractere típico)
        if re.match(r'^ {4,}(if |for |while |return|const |let |var |[A-Za-z_][\w\.]*\s*=)', t):
            return True
        # Linha que contém somente chaves com indentação
        if re.match(r'^\s*[{}]\s*$', t):
            return True
        return False

    for article_tag in soup.find_all('article') or [soup]:
        # Filtra fora nós de texto vazios
        children = [c for c in article_tag.children if not (isinstance(c, NavigableString) and not str(c).strip())]
        i = 0
        while i < len(children):
            node = children[i]
            if not getattr(node, 'name', None) in ('p', 'pre'):
                i += 1
                continue
            text_line = node.get_text().strip('\n')
            if not is_code_line(text_line):
                i += 1
                continue
            seq = [node]
            j = i + 1
            while j < len(children):
                nxt = children[j]
                # pula nós de texto vazios intermediários sem quebrar sequência
                if isinstance(nxt, NavigableString) and not str(nxt).strip():
                    j += 1
                    continue
                if not getattr(nxt, 'name', None) in ('p', 'pre'):
                    break
                nxt_text = nxt.get_text().strip('\n')
                if not is_code_line(nxt_text):
                    break
                seq.append(nxt)
                j += 1
            if len(seq) >= 2:  # monta bloco único
                lines = []
                for ln in seq:
                    ln_txt = ln.get_text().rstrip('\n')
                    lines.append(ln_txt)
                code_block_text = "\n".join(lines)
                new_pre = soup.new_tag('pre')
                new_code = soup.new_tag('code')
                new_code.string = code_block_text
                new_pre.append(new_code)
                seq[0].replace_with(new_pre)
                for extra in seq[1:]:
                    extra.extract()
                # recomputa
                children = list(article_tag.children)
                i = children.index(new_pre) + 1
            else:
                i += 1
        # Segunda passada: expande blocos JSON que ficaram com linhas fora
        children = [c for c in article_tag.children if not (isinstance(c, NavigableString) and not str(c).strip())]
        for idx, node in enumerate(children):
            if getattr(node, 'name', None) == 'pre' and node.code:
                code_txt = node.code.get_text()
                if code_txt.rstrip().endswith('{'):
                    # Coleta parágrafos seguintes até encontrar linha com apenas } ou primeiro parágrafo não JSON-like
                    collect = []
                    j = idx + 1
                    while j < len(children):
                        nxt = children[j]
                        if isinstance(nxt, NavigableString) and not str(nxt).strip():
                            j += 1
                            continue
                        if getattr(nxt, 'name', None) != 'p':
                            break
                        line = nxt.get_text().rstrip('\n')
                        if re.match(r'^\s*"[A-Za-z0-9_]+"\s*:\s*.+', line) or re.match(r'^\s*}', line):
                            collect.append((nxt, line))
                            j += 1
                            if line.strip() == '}':
                                break
                        else:
                            break
                    if collect:
                        # Anexa linhas ao bloco existente
                        new_text = code_txt.rstrip('\n') + '\n' + '\n'.join(l for _, l in collect)
                        node.code.string.replace_with(new_text)
                        for tag_obj, _ in collect:
                            tag_obj.extract()
        # Fim segunda passada

    # Detecta linguagem e adiciona classes highlight.js
    def detect_lang(code_text: str) -> str:
        t = code_text.strip()
        lower = t.lower()
        # Java
        if ('public class' in t or 'System.out.' in t or 'import java.' in t or t.startswith('package ')):
            return 'java'
        # Python
        if t.startswith('def ') or t.startswith('class ') and ':' in t or ' import ' in t and '\n' in t or ' if __name__ == "__main__":' in t:
            return 'python'
        # VBA (use vba) patterns
        if re.search(r'\b(Sub|Function|Dim|Option\s+Explicit|End Sub|End Function)\b', t):
            return 'vba'
        # Bash / shell
        if t.startswith('#!/bin') or t.startswith('echo ') or re.search(r'\b(chmod|sudo|apt-get|ls -|cd )\b', lower):
            return 'bash'
        # JSON (simple heuristic: starts with { or [ and has : )
        if (t.startswith('{') and ':' in t) or (t.startswith('[') and '{' in t and ':' in t):
            return 'json'
        # XML / HTML snippet
        if t.startswith('<') and '</' in t and '>' in t:
            return 'xml'
        # Plaintext diagrams (ASCII art): presence of +-- or |  and multiple lines
        if ('+--' in t or '|  ' in t or '|' in t) and '\n' in t and sum(ch in t for ch in '+-|') > 4:
            return 'plaintext'
        return ''
    for code in soup.find_all('code'):
        lang = detect_lang(code.get_text())
        if lang and f'language-{lang}' not in code.get('class', []):
            existing = code.get('class', [])
            code['class'] = existing + ['hljs', f'language-{lang}']

    # Palavras-chave simples: filtra stopwords, pega as mais frequentes
    from collections import Counter
    tokens = [t.strip('.,;:!?()[]{}"\'').lower() for t in text_words]
    tokens = [t for t in tokens if len(t) > 2 and t not in STOPWORDS and t.isalpha()]
    freq = Counter(tokens)
    keywords = [w for w, _ in freq.most_common(12)]
    keywords_meta = ", ".join(keywords)

    # Imagem principal/og:image: força uso da foto única do autor se configurada
    if AUTHOR_PHOTO_URL:
        img_url = AUTHOR_PHOTO_URL
    else:
        first_img = soup.find('img')
        img_url = f"{BASE_URL}/{first_img['src']}" if first_img and first_img.get('src') else f"{BASE_URL}/default-og-image.png"

    # Data publicação (se presente no nome)
    published_iso = ""
    stem = docx_path.stem
    if len(stem) >= 10 and stem[4] == '_' and stem[7] == '_':
        try:
            published_iso = f"{stem[0:4]}-{stem[5:7]}-{stem[8:10]}"
        except Exception:
            published_iso = ""

    # JSON-LD Article
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "author": {"@type": "Person", "name": AUTHOR_NAME, **({"image": AUTHOR_PHOTO_URL} if AUTHOR_PHOTO_URL else {})},
        "datePublished": published_iso or None,
        "image": img_url,
        "wordCount": word_count,
        "url": None,  # preenchido após conhecer filename final
    }

    safe_name = docx_path.stem + '.html'
    base_url = BASE_URL.rstrip('/')
    canonical = f"{base_url}/{safe_name}"
    json_ld["url"] = canonical
    structured_data_script = f"<script type=\"application/ld+json\">{json.dumps(json_ld, ensure_ascii=False)}</script>"

    seo_head = (
        f"<meta name=\"author\" content=\"{AUTHOR_NAME}\" />\n"
        f"<meta name=\"keywords\" content=\"{keywords_meta}\" />\n"
        f"<link rel=\"canonical\" href=\"{canonical}\" />\n"
        f"<meta property=\"og:title\" content=\"{title}\" />\n"
        f"<meta property=\"og:description\" content=\"{description}\" />\n"
        f"<meta property=\"og:type\" content=\"article\" />\n"
        f"<meta property=\"og:url\" content=\"{canonical}\" />\n"
        f"<meta property=\"og:image\" content=\"{img_url}\" />\n"
        f"<meta property=\"article:author\" content=\"{AUTHOR_NAME}\" />\n" +
        (f"<meta property=\"article:published_time\" content=\"{published_iso}\" />\n" if published_iso else "") +
        # Twitter meta
        f"<meta name=\"twitter:card\" content=\"summary_large_image\" />\n"
        f"<meta name=\"twitter:title\" content=\"{title}\" />\n"
        f"<meta name=\"twitter:description\" content=\"{description}\" />\n"
        f"<meta name=\"twitter:image\" content=\"{img_url}\" />\n"
        f"<meta name=\"twitter:creator\" content=\"{AUTHOR_NAME}\" />\n"
        + structured_data_script
    )

    body_html = str(soup)
    # Insere bloco de autor padronizado no final do artigo
    if AUTHOR_PHOTO_REL or AUTHOR_PHOTO_URL:
        photo_src = AUTHOR_PHOTO_REL or AUTHOR_PHOTO_URL
        author_block = f"<section class=\"author-box\"><img src=\"{photo_src}\" alt=\"{AUTHOR_NAME}\" class=\"author-photo\" loading=\"lazy\"><div class=\"author-meta\"><strong>{AUTHOR_NAME}</strong>Autor</div></section>"
        body_html = body_html + author_block
    final_html = HTML_SHELL.format(title=title, css=CUSTOM_CSS, body=body_html, description=description, reading_time=reading_time, script=PROGRESS_SCRIPT, extra_head=HIGHLIGHT_HEAD + "\n" + seo_head)

    safe_name = docx_path.stem + '.html'
    out_path = out_dir / safe_name
    out_path.write_text(final_html, encoding='utf-8')
    return out_path, title, description, published_iso or "", keywords


def build_tag_pages(tag_map: dict[str, list[dict]], out_dir: Path):
    if not tag_map:
        return []
    base_url = BASE_URL.rstrip('/')
    tag_dir = out_dir
    extra_meta = []
    style_extra = """
    .tag-cloud{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.5rem 0 2rem}
    .tag-chip{background:var(--code-bg);padding:.4rem .75rem;border-radius:999px;font-size:.75rem;font-weight:600;text-decoration:none;color:var(--text);border:1px solid var(--border);}
    .tag-chip:hover{background:var(--bg-alt);}
    .tag-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.6rem}
    .tag-list li{display:flex;flex-direction:column;gap:.2rem;padding:.7rem .85rem;border:1px solid var(--border);border-radius:10px;background:var(--bg-alt)}
    .tag-list li a.title{font-weight:600;text-decoration:none;color:var(--brand)}
    .tag-list li a.title:hover{color:var(--brand-accent)}
    .article-meta{font-size:.65rem;color:var(--text-soft);letter-spacing:.5px}
    """.strip()
    for tag, items in sorted(tag_map.items()):
        slug = slugify(tag)
        items_sorted = sorted(items, key=lambda d: d.get('published') or '', reverse=True)
        lis = []
        for it in items_sorted:
            date_txt = it.get('published', '')
            lis.append(f"<li><a class='title' href='{it['filename']}'>{it['title']}</a><div class='article-meta'>{date_txt}</div><div class='desc'>{it['description'][:160]}</div></li>")
        html = ("<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
                f"<title>Tag: {tag} - {SITE_TITLE}</title>"
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<meta name='color-scheme' content='light dark'>"
                f"<meta name='description' content='Artigos marcados com {tag}'>"
                f"<style>{CUSTOM_CSS}\n{style_extra}</style></head><body><div class=reading-progress id=rp></div>"
                f"<header class='site'><a class='brand' href='index.html'>Início</a><span class='meta'>tag</span></header>"
                f"<main><article><h1>Tag: {tag}</h1><ul class='tag-list'>{''.join(lis)}</ul></article></main>"
                f"<footer class='site'><a href='index.html'>Voltar</a></footer>{PROGRESS_SCRIPT}</body></html>")
        (tag_dir / f"tag-{slug}.html").write_text(html, encoding='utf-8')
        extra_meta.append({'title': f'Tag: {tag}', 'filename': f'tag-{slug}.html', 'description': f'Artigos com tag {tag}', 'published': '', 'lastmod': datetime.now(timezone.utc).isoformat()})
    return extra_meta


def generate_about_page(out_dir: Path):
    about_path = out_dir / 'about.html'
    if about_path.exists():
        return {'title': 'Sobre', 'filename': 'about.html', 'description': f'Sobre {AUTHOR_NAME}', 'published': '', 'lastmod': datetime.fromtimestamp(about_path.stat().st_mtime, tz=timezone.utc).isoformat()}
    about_jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": AUTHOR_NAME,
        "url": BASE_URL.rstrip('/') + '/about.html',
        "description": f"Autor de {SITE_TITLE}",
    }
    about_html = f"""<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>
<title>Sobre - {SITE_TITLE}</title>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<meta name='description' content='Sobre o autor {AUTHOR_NAME}'>
<meta name='color-scheme' content='light dark'>
<style>{CUSTOM_CSS}</style>
<script type='application/ld+json'>{json.dumps(about_jsonld, ensure_ascii=False)}</script>
</head><body><div class=reading-progress id=rp></div><header class='site'><a class='brand' href='index.html'>Início</a><span class='meta'>sobre</span></header>
<main><article><h1>Sobre</h1><p>Este site reúne artigos convertidos automaticamente. Autor: {AUTHOR_NAME}.</p></article></main>
<footer class='site'><a href='index.html'>Voltar</a></footer>{PROGRESS_SCRIPT}</body></html>"""
    about_path.write_text(about_html, encoding='utf-8')
    return {'title': 'Sobre', 'filename': 'about.html', 'description': f'Sobre {AUTHOR_NAME}', 'published': '', 'lastmod': datetime.now(timezone.utc).isoformat()}


def create_og_image_svg(title: str, out_dir: Path, slug: str):
    og_dir = out_dir / 'og'
    og_dir.mkdir(exist_ok=True)
    safe_title = (title[:120] + '…') if len(title) > 120 else title
    # Escape XML special chars
    esc = safe_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#34;')
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#0b63c5'/><stop offset='100%' stop-color='#084f9d'/></linearGradient></defs>
<rect width='1200' height='630' fill='url(#g)'/>
<text x='60' y='200' fill='#fff' font-family='Segoe UI, Arial, sans-serif' font-size='60' font-weight='600'> {esc} </text>
<text x='60' y='300' fill='#e2e8f0' font-family='Segoe UI, Arial, sans-serif' font-size='34'>{AUTHOR_NAME}</text>
<text x='60' y='360' fill='#cbd5e1' font-family='Segoe UI, Arial, sans-serif' font-size='28'>{SITE_TITLE}</text>
</svg>"""
    path = og_dir / f"{slug}.svg"
    path.write_text(svg, encoding='utf-8')
    return path


def generate_index(pages: list[tuple[str, str, str]], out_dir: Path):
    """Gera um index.html.

    pages: lista de tuplas (data_prefix, title, filename)
    """
    # Agrupamento por ano->mes
    data_map: dict[int, dict[int, list[tuple[str, str, str, str]]]] = {}
    # Estrutura de cada item armazenado: (yyyy-mm-dd, dia, titulo, filename)
    no_date: list[tuple[str, str]] = []  # (titulo, filename)
    for date_prefix, title, filename in pages:
        if len(date_prefix) == 10 and date_prefix[4] == '_' and date_prefix[7] == '_':
            try:
                y = int(date_prefix[0:4])
                m = int(date_prefix[5:7])
                d = int(date_prefix[8:10])
                date_iso = f"{y:04d}-{m:02d}-{d:02d}"
                data_map.setdefault(y, {}).setdefault(m, []).append((date_iso, f"{d:02d}", title, filename))
            except ValueError:
                no_date.append((title, filename))
        else:
            no_date.append((title, filename))

    # Ordenação descendente de ano e mês
    years_sorted = sorted(data_map.keys(), reverse=True)
    month_names = [None, 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    parts: list[str] = []
    for y in years_sorted:
        parts.append(f"<section class='year-group'><h2 class='year-heading'>{y}</h2>")
        months_sorted = sorted(data_map[y].keys(), reverse=True)
        parts.append("<div class='months'>")
        for m in months_sorted:
            posts = sorted(data_map[y][m], key=lambda x: x[0], reverse=True)
            parts.append(f"<section class='month-block'><h3 class='month-heading'><span class='m-name'>{month_names[m]}</span> <span class='badge'>{len(posts)}</span></h3><ul class='post-list'>")
            for date_iso, day_txt, title, filename in posts:
                parts.append(f"<li><time datetime='{date_iso}'><span class='day'>{day_txt}</span></time><a href='{filename}'>{title}</a></li>")
            parts.append("</ul></section>")
        parts.append("</div></section>")

    if no_date:
        parts.append("<section class='year-group'><h2 class='year-heading'>Sem Data</h2><ul class='post-list'>")
        for title, filename in sorted(no_date, key=lambda x: x[0].lower()):
            parts.append(f"<li><a href='{filename}'>{title}</a></li>")
        parts.append("</ul></section>")

    content_html = ''.join(parts)

    css_extra = (
        ".year-heading{margin:3.5rem 0 1.25rem;font-size:clamp(1.8rem,3vw,2.2rem);letter-spacing:-1px;}"
        ".year-group:first-of-type .year-heading{margin-top:0;}"
        ".months{display:grid;gap:2.25rem;}@media(min-width:800px){.months{grid-template-columns:repeat(auto-fill,minmax(320px,1fr));}}"
        ".month-block{background:var(--bg-alt);border:1px solid var(--border);border-radius:14px;padding:1.1rem 1.1rem 1.25rem;box-shadow:var(--shadow);position:relative;}"
        ".month-heading{margin:0 0 .85rem;font-size:1.05rem;font-weight:600;display:flex;align-items:center;gap:.55rem;}"
        ".badge{background:var(--brand);color:#fff;border-radius:999px;padding:.15rem .55rem;font-size:.65rem;font-weight:600;letter-spacing:.5px;}"
        ".post-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.55rem;}"
        ".post-list li{display:grid;grid-template-columns:3.2rem 1fr;align-items:start;gap:.25rem;padding:.45rem .55rem;border:1px solid var(--border);border-radius:10px;background:var(--bg);transition:background .2s,border-color .2s;}"
        ".post-list li:hover{background:var(--code-bg);}"
        ".post-list time{font-size:.8rem;color:var(--text-soft);font-weight:600;letter-spacing:.5px;text-align:right;}"
        ".post-list a{font-weight:500;text-decoration:none;color:var(--text);}"
        ".post-list a:hover{color:var(--brand);}"
        "@media(max-width:620px){.post-list li{grid-template-columns:2.6rem 1fr;padding:.4rem .55rem;}.post-list time{font-size:.65rem;}}"
    )

    total = len(pages)
    index_script = ("<script>\"use strict\";const rp=document.getElementById('rp');const h=document.documentElement;"
                    "addEventListener('scroll',()=>{const st=h.scrollTop;const sh=h.scrollHeight-h.clientHeight;rp.style.width=(sh?(st/sh)*100:0)+'%';},{passive:true});</script>")
    html = (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><title>Artigos de Christian V. U. Mulato.</title>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='color-scheme' content='light dark'>"
        "<meta name='description' content='Índice de artigos convertidos agrupados por ano e mês'>"
        f"<style>{CUSTOM_CSS}\n{css_extra}</style></head>"
        f"<body><div class=reading-progress id=rp></div><header class='site'><a class='brand' href='index.html'>Início</a><span class='meta'>{total} artigos</span></header>"
    f"<main><article><h1>Artigos de Christian V. U. Mulato.</h1>{content_html}</article></main>"
        "<footer class='site'>Gerado automaticamente. <a href='index.html'>Topo</a></footer>"
        f"{index_script}</body></html>"
    )
    (out_dir / 'index.html').write_text(html, encoding='utf-8')


def generate_sitemap_and_feeds(items: list[dict], out_dir: Path):
    if not items:
        return
    base_url = BASE_URL.rstrip('/')
    # Ordena por data de publicação desc para feeds
    def sort_key(d):
        return d.get('published') or ''
    items_sorted = sorted(items, key=sort_key, reverse=True)

    # Sitemap XML
    sitemap_entries = []
    now_iso = datetime.now(timezone.utc).isoformat()
    # index
    sitemap_entries.append(f"  <url><loc>{base_url}/index.html</loc><lastmod>{now_iso}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    for it in items_sorted:
        loc = f"{base_url}/{it['filename']}"
        lastmod = it.get('lastmod') or now_iso
        sitemap_entries.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>")
    sitemap_xml = "<?xml version='1.0' encoding='UTF-8'?>\n" \
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + "\n".join(sitemap_entries) + "\n</urlset>"
    (out_dir / 'sitemap.xml').write_text(sitemap_xml, encoding='utf-8')

    # Robots.txt
    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
    (out_dir / 'robots.txt').write_text(robots_txt, encoding='utf-8')

    # RSS 2.0
    rss_items = []
    for it in items_sorted[:50]:
        pub = it.get('published')
        pub_rfc822 = ''
        if pub:
            try:
                dt = datetime.fromisoformat(pub)
                pub_rfc822 = dt.strftime('%a, %d %b %Y 00:00:00 +0000')
            except Exception:
                pub_rfc822 = ''
        desc = (it.get('description') or '')[:500]
        link = f"{base_url}/{it['filename']}"
        rss_items.append(
            f"<item><title><![CDATA[{it['title']}]]></title><link>{link}</link><guid>{link}</guid>" +
            (f"<pubDate>{pub_rfc822}</pubDate>" if pub_rfc822 else '') +
            f"<description><![CDATA[{desc}]]></description></item>"
        )
    rss_xml = (
        "<?xml version='1.0' encoding='UTF-8'?>\n" \
        f"<rss version='2.0'><channel><title>{SITE_TITLE}</title><link>{base_url}/</link><description>{SITE_TITLE} Feed</description>" \
        + "".join(rss_items) + "</channel></rss>"
    )
    (out_dir / 'feed.xml').write_text(rss_xml, encoding='utf-8')

    # Atom
    feed_updated = now_iso
    atom_entries = []
    for it in items_sorted[:50]:
        updated = it.get('lastmod') or feed_updated
        link = f"{base_url}/{it['filename']}"
        summary = (it.get('description') or '')[:280]
        atom_entries.append(
            f"<entry><title>{it['title']}</title><link href='{link}' /><id>{link}</id><updated>{updated}</updated><summary>{summary}</summary></entry>"
        )
    atom_xml = (
        "<?xml version='1.0' encoding='utf-8'?>\n" \
        f"<feed xmlns='http://www.w3.org/2005/Atom'><title>{SITE_TITLE}</title><id>{base_url}/</id><updated>{feed_updated}</updated>" \
        + ''.join(atom_entries) + "</feed>"
    )
    (out_dir / 'atom.xml').write_text(atom_xml, encoding='utf-8')


def clean_unused_images(out_dir: Path):
    """Remove arquivos dentro de html/img que não sejam referenciados por nenhum HTML.
    Preserva a foto do autor e estrutura de diretórios.
    """
    img_root = out_dir / IMG_SUBDIR_NAME
    if not img_root.exists():
        return
    # Coleta caminhos referenciados
    referenced: set[str] = set()
    for html_file in out_dir.glob('*.html'):
        try:
            soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
            for tag in soup.find_all(['img', 'source']):
                src = tag.get('src') or tag.get('data-src')
                if not src:
                    continue
                # Normaliza relativos que começam com img/
                if src.startswith(f"{IMG_SUBDIR_NAME}/"):
                    referenced.add(Path(src).as_posix())
        except Exception:
            continue
    # Garante preservação da foto do autor
    if AUTHOR_PHOTO_REL:
        referenced.add(Path(AUTHOR_PHOTO_REL).as_posix())
    removed = 0
    for file in img_root.rglob('*'):
        if file.is_dir():
            continue
        rel = file.relative_to(out_dir).as_posix()  # ex: img/slug-01.png
        if rel not in referenced:
            try:
                file.unlink()
                removed += 1
            except Exception:
                pass
    # Limpa diretórios vazios (exceto raiz img)
    for dirpath, dirnames, filenames in list(os.walk(img_root, topdown=False)):
        p = Path(dirpath)
        if p == img_root:
            continue
        if not any(p.iterdir()):
            try:
                p.rmdir()
            except Exception:
                pass
    if removed:
        print(f"Imagens órfãs removidas: {removed}")
    else:
        print("Nenhuma imagem órfã encontrada.")


def enforce_author_photo(out_dir: Path):
    """Garante que cada artigo *.html (exceto index/about/tag) contenha o bloco de autor
    com a mesma imagem (AUTHOR_PHOTO_REL ou URL). Se ausente ou divergente, corrige.
    """
    if not (AUTHOR_PHOTO_REL or AUTHOR_PHOTO_URL):
        return
    photo_src = AUTHOR_PHOTO_REL or AUTHOR_PHOTO_URL
    changed = 0
    for html_file in out_dir.glob('*.html'):
        name = html_file.name
        if name in ('index.html', 'about.html') or name.startswith('tag-'):
            continue
        try:
            html_txt = html_file.read_text(encoding='utf-8')
            soup = BeautifulSoup(html_txt, 'html.parser')
            article = soup.find('article')
            if not article:
                continue
            existing_block = soup.find('section', {'class': 'author-box'})
            needs_update = False
            if existing_block:
                img = existing_block.find('img', {'class': 'author-photo'})
                if not img or img.get('src') != photo_src:
                    needs_update = True
            else:
                needs_update = True
            if needs_update:
                new_html = BeautifulSoup(
                    f"<section class='author-box'><img src='{photo_src}' alt='{AUTHOR_NAME}' class='author-photo' loading='lazy'><div class='author-meta'><strong>{AUTHOR_NAME}</strong>Autor</div></section>",
                    'html.parser'
                )
                if existing_block:
                    existing_block.replace_with(new_html)
                else:
                    article.append(new_html)
                html_file.write_text(str(soup), encoding='utf-8')
                changed += 1
        except Exception:
            continue
    if changed:
        print(f"Bloco de autor verificado/atualizado em {changed} artigos.")
    else:
        print("Todos os artigos já possuem bloco de autor consistente.")

def pre_clean_articles(out_dir: Path, manifest: dict, author_photo_rel: str):
    """Remove todos os HTML de artigos previamente gerados e imagens, exceto a fotografia do autor.
    Mantém index/tag/about (serão regenerados) e preserva foto do autor.
    Limpa também og/*.svg.
    Zera seção 'files' do manifest para forçar reconstrução completa.
    """
    files_section = manifest.get('files') or {}
    removed_html = 0
    for rec in list(files_section.values()):
        html_name = rec.get('html')
        if not html_name:
            continue
        p = out_dir / html_name
        if p.exists():
            try:
                p.unlink()
                removed_html += 1
            except Exception:
                pass
    # Limpa imagens exceto foto autor
    img_root = out_dir / IMG_SUBDIR_NAME
    preserved = set()
    if author_photo_rel:
        preserved.add((out_dir / author_photo_rel).resolve())
    if img_root.exists():
        for f in img_root.rglob('*'):
            if f.is_file():
                if f.resolve() in preserved:
                    continue
                try:
                    f.unlink()
                except Exception:
                    pass
        # Remove diretórios vazios (exceto raiz img)
        for dirpath, dirnames, filenames in list(os.walk(img_root, topdown=False)):
            pdir = Path(dirpath)
            if pdir == img_root:
                continue
            try:
                next(pdir.iterdir())
            except StopIteration:
                try:
                    pdir.rmdir()
                except Exception:
                    pass
    # Limpa og images
    og_dir = out_dir / 'og'
    if og_dir.exists():
        for f in og_dir.glob('*.svg'):
            try:
                f.unlink()
            except Exception:
                pass
    manifest['files'] = {}
    if removed_html:
        print(f"Limpeza prévia: removidos {removed_html} HTML de artigos e imagens (exceto foto autor).")
    else:
        print("Limpeza prévia: nada para remover.")

def main():
    if not DOCX_DIR.exists():
        raise SystemExit(f"Pasta não encontrada: {DOCX_DIR}")
    HTML_DIR.mkdir(exist_ok=True)
    # Prepara foto única do autor (se local). Se for URL, apenas registra.
    global AUTHOR_PHOTO_REL, AUTHOR_PHOTO_URL
    try:
        input_lower = AUTHOR_PHOTO_INPUT.lower()
        # URL absoluta
        if input_lower.startswith(("http://", "https://")):
            AUTHOR_PHOTO_URL = AUTHOR_PHOTO_INPUT
            # Sem caminho relativo interno
        else:
            src_path = Path(AUTHOR_PHOTO_INPUT)
            # Caso especial: caminho já dentro de html/ (ex: html/img/photo_autor/christian.jpg)
            try:
                if src_path.is_absolute():
                    inside_html = HTML_DIR in src_path.parents
                else:
                    inside_html = str(src_path).startswith(str(HTML_DIR))
            except Exception:
                inside_html = False
            if inside_html and src_path.exists():
                # Computa caminho relativo a HTML_DIR
                rel = src_path.relative_to(HTML_DIR)
                AUTHOR_PHOTO_REL = rel.as_posix()
                AUTHOR_PHOTO_URL = f"{BASE_URL.rstrip('/')}/{AUTHOR_PHOTO_REL}"
            elif src_path.exists():
                img_root = HTML_DIR / IMG_SUBDIR_NAME
                photo_dir = img_root / AUTHOR_PHOTO_SUBDIR
                photo_dir.mkdir(parents=True, exist_ok=True)
                # Preserva nome original
                target = photo_dir / src_path.name
                if (not target.exists()) or src_path.stat().st_mtime > target.stat().st_mtime:
                    target.write_bytes(src_path.read_bytes())
                AUTHOR_PHOTO_REL = f"{IMG_SUBDIR_NAME}/{AUTHOR_PHOTO_SUBDIR}/{target.name}"
                AUTHOR_PHOTO_URL = f"{BASE_URL.rstrip('/')}/{AUTHOR_PHOTO_REL}"
            else:
                AUTHOR_PHOTO_REL = ""
                AUTHOR_PHOTO_URL = ""
    except Exception:
        AUTHOR_PHOTO_REL = ""
        AUTHOR_PHOTO_URL = ""

    docx_files = sorted([p for p in DOCX_DIR.iterdir() if p.suffix.lower() == '.docx'])
    if not docx_files:
        print('Nenhum arquivo .docx encontrado.')
        return

    # Carrega manifest existente
    manifest_path = HTML_DIR / MANIFEST_FILE
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception:
            manifest = {"files": {}}
    else:
        manifest = {"files": {}}

    # Poda de artigos removidos (DOCX que não existem mais)
    existing_docx_names = {p.name for p in docx_files}
    removed = []
    if 'files' in manifest:
        for docx_name in list(manifest['files'].keys()):
            if docx_name not in existing_docx_names:
                rec = manifest['files'][docx_name]
                html_name = rec.get('html')
                if html_name:
                    html_path = HTML_DIR / html_name
                    if html_path.exists():
                        try:
                            html_path.unlink()
                        except Exception:
                            pass
                # Remove imagens derivadas pelo slug
                stem = Path(docx_name).stem
                slug = slugify(stem)
                img_root = HTML_DIR / IMG_SUBDIR_NAME
                if img_root.exists():
                    for img_file in img_root.glob(f"{slug}-*.*"):
                        try:
                            img_file.unlink()
                        except Exception:
                            pass
                # Remove OG svg
                og_path = HTML_DIR / 'og' / f"{slug}.svg"
                if og_path.exists():
                    try:
                        og_path.unlink()
                    except Exception:
                        pass
                removed.append(docx_name)
                del manifest['files'][docx_name]
    if removed:
        print(f"Removidos {len(removed)} artigos órfãos: {', '.join(removed[:5])}{'...' if len(removed)>5 else ''}")

    # Limpeza total prévia dos artigos e imagens (exceto foto autor) para regeneração completa
    try:
        pre_clean_articles(HTML_DIR, manifest, AUTHOR_PHOTO_REL)
    except Exception as e:
        print(f"Aviso: falha na limpeza prévia: {e}")

    pages: list[tuple[str, str, str]] = []  # para índice (date_prefix, title, filename)
    meta_items = []  # lista de dict para feeds / sitemap
    tag_map: dict[str, list[dict]] = {}
    for path in docx_files:
        try:
            h = sha1_file(path)
            rec = manifest.get('files', {}).get(path.name)
            if rec and rec.get('hash') == h and not FORCE_REBUILD:
                # Reutiliza
                title = rec.get('title', path.stem)
                html_name = rec.get('html', path.stem + '.html')
                description = rec.get('description', title)
                published = rec.get('published', '')
                keywords = rec.get('keywords', [])
                print(f"(cache) {path.name} -> {html_name}")
            else:
                out, title, description, published, keywords = convert_file(path, HTML_DIR)
                html_name = out.name
                if 'files' not in manifest:
                    manifest['files'] = {}
                manifest['files'][path.name] = {
                    'hash': h,
                    'title': title,
                    'description': description,
                    'published': published,
                    'html': html_name,
                    'keywords': keywords,
                }
                print(f"Convertido: {path.name} -> {html_name}")

            stem = path.stem
            date_prefix = ""
            if len(stem) >= 10 and stem[4] == '_' and stem[7] == '_':
                date_prefix = stem[:10]
            pages.append((date_prefix, title, html_name))

            # lastmod: usa mtime do arquivo docx
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
            published_iso = ''
            if date_prefix:
                published_iso = f"{date_prefix[0:4]}-{date_prefix[5:7]}-{date_prefix[8:10]}"
            # Tags derivadas de keywords (limit)
            tags = keywords[:MAX_TAGS_PER_ARTICLE] if 'keywords' in locals() else []
            for tg in tags:
                tag_map.setdefault(tg, []).append({
                    'title': title,
                    'filename': html_name,
                    'description': description,
                    'published': published_iso,
                })

            # OG image dynamic
            try:
                slug = slugify(path.stem)
                og_path = create_og_image_svg(title, HTML_DIR, slug)
            except Exception:
                og_path = None

            meta_items.append({
                'title': title,
                'filename': html_name,
                'description': description,
                'published': published_iso,
                'lastmod': mtime,
                'tags': tags,
                'og': og_path.name if og_path else ''
            })
        except Exception as e:
            print(f"ERRO ao converter {path.name}: {e}")

    if pages:
        generate_index(pages, HTML_DIR)
        print("index.html gerado.")
        # Tag pages
        extra_meta = build_tag_pages(tag_map, HTML_DIR)
        if extra_meta:
            meta_items.extend(extra_meta)
            print(f"{len(extra_meta)} páginas de tag geradas.")
        about_meta = generate_about_page(HTML_DIR)
        if about_meta:
            meta_items.append(about_meta)
            print("about.html gerado.")
        # Salva manifest
        try:
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"Aviso: não foi possível salvar manifest: {e}")
        # Gera sitemap e feeds
        try:
            generate_sitemap_and_feeds(meta_items, HTML_DIR)
            print("sitemap.xml, robots.txt, feed RSS e Atom gerados.")
        except Exception as e:
            print(f"Aviso: erro ao gerar sitemap/feeds: {e}")
        # Limpa imagens não referenciadas
        try:
            clean_unused_images(HTML_DIR)
        except Exception as e:
            print(f"Aviso: erro ao limpar imagens órfãs: {e}")
        # Verifica foto de autor
        try:
            enforce_author_photo(HTML_DIR)
        except Exception as e:
            print(f"Aviso: erro ao validar foto do autor: {e}")

if __name__ == '__main__':
    main()
