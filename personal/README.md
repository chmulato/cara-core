# Builder de Site Estático (DOCX → HTML)

Este repositório fornece um único script Python (`convert_docx_to_html.py`) que atua como um builder determinístico: a cada execução ele (1) limpa saídas anteriores, (2) reconstrói integralmente todo o site a partir dos `.docx` em `docx/` e (3) produz artefatos prontos para deploy em `html/`.

> Pense nele como um “mini Make” especializado em artigos: entrada = documentos Word; saída = site completo com SEO, feeds, tags e código destacado.

## Visão de Builder

O pipeline é composto por fases encadeadas. Cada fase recebe o estado produzido pela anterior e gera artefatos específicos:

| Ordem | Fase                       | Função / Responsabilidade                          | Artefatos / Side Effects                                                |
|:-----:|----------------------------|----------------------------------------------------|-------------------------------------------------------------------------|
| 01    | Pré‑Limpeza                | `pre_clean_articles`                               | Remove HTML antigos, imagens derivadas e SVGs; reinicia manifesto       |
| 02    | Descoberta                 | Listagem e hashing de `.docx`                      | Lista ordenada de entradas                                              |
| 03    | Conversão                  | `convert_file` + `mammoth` + pós‑processo          | `<slug>.html`, imagens extraídas, blocos `<pre><code>` normalizados     |
| 04    | Indexação de Conteúdo      | Coleta de metadados                                | Estrutura em memória p/ index, tags e feeds                             |
| 05    | Geração de Páginas Globais | `generate_index`, `generate_tag_pages`, `generate_about` | `index.html`, `tag-*.html`, `about.html`                           |
| 06    | Assets Sociais             | Geração de SVG OG                                  | `html/og/<slug>.svg`                                                    |
| 07    | Feeds & Descoberta         | `generate_sitemap_and_feeds`                       | `sitemap.xml`, `robots.txt`, `feed.xml`, `atom.xml`                     |
| 08    | Consolidação Visual        | `enforce_author_photo`                             | Bloco de autor consistente (se ausente)                                |
| 09    | Higiene Final              | Limpeza de imagens órfãs                           | Remoção de arquivos não referenciados                                   |

Características de builder:

- Idempotente: duas execuções consecutivas produzem o mesmo conjunto de artefatos (salvo timestamps de feeds e ordem natural de arquivos). 
- Declarativo implícito: a árvore `docx/` é a “fonte da verdade”; não há edição manual em `html/`.
- Full rebuild rápido: evita estados intermediários inconsistentes e elimina necessidade de invalidar cache manual.
- Facilmente extensível: novas fases podem ser inseridas após a conversão (ex.: minificação, geração de PDF, index de busca).

Para adicionar uma nova fase, localize o `main()` e insira a chamada após a fase mais semanticamente próxima, mantendo a sequência determinística.

## Principais Funcionalidades

- Conversão DOCX → HTML usando a biblioteca `mammoth`.
- Layout responsivo, tipografia fluida, dark mode automático e barra de progresso de leitura.
- Extração automática de imagens embutidas no DOCX para `html/img/` com nomes derivados do arquivo de origem.
- Foto única de autor reutilizada em todos os artigos (bloco de autor e imagem social) localizada em `html/img/photo_autor/christian.jpg` (configurável).
- Normalização de blocos de código, detecção heurística de linguagem (Java, Python, VBA, Bash, JSON, XML, diagramas ASCII) e syntax highlighting via Highlight.js (CDN).
- Botão de "copiar" e numeração de linhas em cada bloco de código (`<pre><code>`).
- Geração de metadados SEO: `<meta>` (description, keywords, author), Open Graph, Twitter Cards e JSON‑LD Article Schema.
- Geração de imagem social (Open Graph) dinâmica em SVG por artigo em `html/og/`.
- Indexação cronológica agrupada (ano → mês) em `html/index.html` com título: "Artigos de Christian V. U. Mulato.".
- Derivação de palavras‑chave (keywords) simples com filtro de stopwords em português.
- Sistema de tags: páginas individuais `tag-<slug>.html` listando artigos associados.
- Página "Sobre" (`about.html`) com JSON‑LD Person.
- Feeds e descoberta: `sitemap.xml`, `robots.txt`, RSS (`feed.xml`) e Atom (`atom.xml`).
- Cache incremental via hash SHA‑1 por arquivo DOCX armazenado em `html/_manifest.json` (evita reconversões desnecessárias).
- Limpeza automática de imagens órfãs (não referenciadas em nenhum HTML) dentro de `html/img/` preservando a foto do autor.
- Limpeza PRÉVIA completa a cada execução: remove todos os HTML de artigos anteriores, imagens derivadas e SVGs OG antes de regenerar (preserva apenas a foto do autor).
- Força de reconstrução opcional via variável de ambiente (hoje o rebuild já é sempre completo devido à limpeza prévia; variável mantida por compatibilidade).

## Estrutura de Pastas

Antes da execução:
```
project/
  docx/                # Coloque aqui seus arquivos .docx
  convert_docx_to_html.py
  requirements.txt
```
Após a execução típica:
```
project/
  docx/
  html/
    index.html
    about.html
    *.html
    img/
      photo_autor/
        christian.jpg   # Foto única do autor (ou outro nome configurado)
      <slug>-01.png
      ...
    og/
      <slug>.svg
    tag-*.html
    sitemap.xml
    robots.txt
    feed.xml
    atom.xml
    _manifest.json
  convert_docx_to_html.py
  requirements.txt
  README.md
```

## Requisitos

- Python 3.10+ (desenvolvido/testado em 3.13).
- Dependências listadas em `requirements.txt`:
  - `mammoth`
  - `beautifulsoup4`
- Acesso à internet (para carregar o CSS/JS do Highlight.js via CDN).

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

```powershell
python convert_docx_to_html.py
```

## Variáveis de Ambiente (Configuração)

| Variável                | Descrição                                                                                                        | Padrão Atual                       |
|-------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `ARTICLES_BASE_URL`     | URL pública raiz (canônicos, sitemap, og:image)                                                                  | `https://example.com`              |
| `ARTICLES_AUTHOR_NAME`  | Nome do autor (meta, JSON‑LD)                                                                                    | `Christian Vladimir Uhdre Mulato`  |
| `ARTICLES_SITE_TITLE`   | Título geral do site (feeds, about, OG)                                                                           | `Artigos`                          |
| `ARTICLES_FORCE_REBUILD`| `1` força reconverter todos os DOCX (hoje redundante)                                                            | `0`                                |
| `ARTICLES_AUTHOR_PHOTO` | Caminho local ou URL da foto do autor (copiada para `html/img/photo_autor/` se estiver fora de `html/`)          | `author.jpg`                       |

Exemplo:
```powershell
$env:ARTICLES_BASE_URL = "https://meusite.com"
$env:ARTICLES_AUTHOR_NAME = "Christian Vladimir Uhdre Mulato"
$env:ARTICLES_AUTHOR_PHOTO = "html/img/photo_autor/christian.jpg"
python convert_docx_to_html.py
```

## Convenção de Datas

Prefixo `YYYY_MM_DD_` no nome define a data (ordenando índice e feeds). Sem prefixo → seção "Sem Data".

## Imagem do Autor

- A mesma imagem é usada em todos os artigos como `og:image` e exibida em um bloco de autor padrão no fim do conteúdo.
- Se `ARTICLES_AUTHOR_PHOTO` for uma URL, ela é usada diretamente sem cópia.
- Se for um caminho local externo à pasta `html/`, a imagem é copiada para `html/img/photo_autor/` preservando o nome.

## Ciclo de Build (Atualização / Rebuild)

Desde a introdução da limpeza prévia completa:

1. Ao iniciar, o script remove TODOS os HTML de artigos previamente gerados, todas as imagens em `html/img/` (exceto a foto do autor) e todos os SVGs em `html/og/`.
2. O manifesto `_manifest.json` é reiniciado (`files` esvaziado), garantindo reconversão integral de todos os `.docx` em cada execução.
3. Cada DOCX é convertido novamente (não há reaproveitamento de cache neste modo).
4. Em seguida são regenerados: `index.html`, páginas de tag, `about.html` (se ausente), `sitemap.xml`, `robots.txt`, `feed.xml`, `atom.xml`.
5. Após a geração ocorre uma segunda limpeza de imagens órfãs (geralmente nada a remover porque tudo já foi recém-gerado).
6. A foto única do autor (padrão `html/img/photo_autor/christian.jpg` ou a configurada) é sempre preservada.

Observações:
- A variável `ARTICLES_FORCE_REBUILD` tornou-se redundante porque todo rebuild já é completo; ela permanece sem causar efeitos adicionais relevantes.
- Se desejar reativar um modo incremental no futuro, basta remover ou condicionar a rotina de limpeza prévia (função `pre_clean_articles`).

Execução simples continua igual:
```powershell
python convert_docx_to_html.py
```

## Limpeza de Imagens Órfãs

Após a geração o script remove imagens em `html/img/` não referenciadas por nenhum HTML, exceto as localizadas em `photo_autor/` ou a foto configurada.

## Tags e Keywords

- Keywords: frequência filtrada por stopwords; top 12 → base para tags.
- Tags: primeiras até 8 keywords (ajustável) viram tags e geram páginas `tag-<slug>.html`.

## Geração de Imagens Open Graph

- Cada artigo gera um SVG em `html/og/`.
- A imagem `og:image` usada nas meta tags foi padronizada para a foto do autor (não a primeira imagem do corpo).

## Cache Incremental (Estado Atual)

O código ainda gera `_manifest.json`, porém a limpeza prévia zera sua utilidade prática porque todos os arquivos são sempre reconvertidos. Caso queira voltar ao comportamento incremental, remova a chamada da função `pre_clean_articles` em `main()` e então o manifesto voltará a poupar conversões.

## Personalização Rápida

1. `CUSTOM_CSS` para estilos.
2. `MAX_TAGS_PER_ARTICLE` para limite de tags.
3. Heurística em `detect_lang` para linguagens de código.
4. Divisor de palavras por minuto (200) para tempo de leitura.
5. Adicionar/ajustar stopwords no set `STOPWORDS`.

## Limitações Conhecidas

- Detecção de linguagem heurística.
- Sem otimização/compressão de imagens.
- Dependência de CDN para Highlight.js.
- Sem minificação de assets.
- Tags potencialmente numerosas (sem filtro mínimo de frequência ainda).
- Cache incremental desativado de fato pela limpeza prévia (pode ser reativado manualmente removendo a limpeza).

## Próximas Melhorias Possíveis

- Filtro mínimo de frequência para tags.
- Minificação de HTML/CSS/JS.
- Conversão das imagens para WebP/AVIF.
- Busca full‑text / indexação.
- Botões de compartilhamento social.

## Fluxo de Trabalho (Build Loop)

1. Adicione/atualize `.docx` em `docx/`.
2. (Opcional) Ajuste variáveis de ambiente.
3. Execute o script.
4. Faça deploy do conteúdo de `html/`.

## Troubleshooting (Diagnóstico de Build)

| Sintoma                 | Causa                       | Solução                                      |
|-------------------------|-----------------------------|----------------------------------------------|
| Artigo ausente          | Nome / extensão incorreta   | Verifique se é `.docx` e reexecute           |
| Código sem highlight    | Heurística falhou           | Ajuste `detect_lang` ou adicione classes     |
| OG não aparece em redes | Plataforma não suporta SVG  | Converter SVG para PNG                       |
| CSS não atualiza        | Cache do navegador          | Hard refresh ou limpar cache                 |
| Foto autor ausente      | Caminho incorreto / não copiou | Verifique `ARTICLES_AUTHOR_PHOTO` e permissões |

## Licença

Projeto sob Licença MIT. Veja `LICENSE`.

Copyright (c) 2025 Christian Vladimir Uhdre Mulato.

---
Documentação atualizada do pipeline de conversão de artigos.
