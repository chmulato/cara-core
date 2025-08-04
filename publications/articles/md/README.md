# Artigos em Markdown - Cara Core Informática

Esta pasta contém os arquivos de origem em Markdown dos artigos publicados no site da Cara Core Informática.

## 📁 Estrutura e Organização

### Finalidade
- **Arquivos .md**: Versões de origem dos artigos em formato Markdown
- **Processo**: Os arquivos Markdown são convertidos para HTML otimizado usando o SEO Article Builder
- **Versionamento**: Mantém histórico das versões originais dos artigos

### Convenções de Nomenclatura

#### Para arquivos Markdown:
```
{tema_principal}_{subtema}.md
```

**Exemplos:**
- `zeca_delivery.md` → Case do Zeca sobre automação de delivery
- `seo_builder.md` → Artigo sobre SEO Article Builder  
- `sending_cv.md` → Artigo sobre automação de busca por emprego

#### Para artigos HTML finais:
```
YYYY_MM_DD_article_XX.html
```

**Exemplos:**
- `2025_07_06_article_38.html` → Artigo 38 (SEO Article Builder)
- `2025_07_16_article_39.html` → Artigo 39 (Sending_CV)
- `2025_08_04_article_40.html` → Artigo 40 (Case Zeca Delivery)

## 🔄 Fluxo de Trabalho

### 1. Criação
1. Escrever o artigo em Markdown nesta pasta (`md/`)
2. Usar nomenclatura descritiva baseada no tema
3. Incluir metadados necessários no cabeçalho

### 2. Conversão
1. Usar o **SEO Article Builder** para converter .md → .html
2. O sistema automaticamente:
   - Gera meta tags SEO otimizadas
   - Aplica formatação responsiva
   - Adiciona estrutura semântica
   - Inclui links de navegação

### 3. Publicação
1. Arquivo HTML final é salvo em `publications/articles/`
2. Referência é adicionada em `articles.html`
3. Imagens são organizadas em `media/`

## 📝 Mapeamento Atual

| Arquivo Markdown | Artigo HTML | Tema Principal |
|------------------|-------------|----------------|
| `zeca_delivery.md` | `2025_08_04_article_40.html` | Automação de Logística |

## ⚠️ Importante

### Não Confundir:
- **Esta pasta (`md/`)**: Arquivos de origem em Markdown
- **Pasta principal (`articles/`)**: Artigos HTML publicados
- **Pasta `media/`**: Imagens e recursos dos artigos

### Regras:
1. **Sempre manter** a versão Markdown como fonte da verdade
2. **Nunca editar** diretamente os arquivos HTML (usar o builder)
3. **Sincronizar** alterações: MD → HTML via SEO Article Builder
4. **Commit** sempre os dois arquivos (MD e HTML) juntos

## 🛠️ Ferramentas

### SEO Article Builder
- **Função**: Conversão automatizada MD → HTML
- **Benefícios**: SEO otimizado, estrutura padronizada, meta tags automáticas
- **Uso**: Executar após qualquer alteração no Markdown

### Controle de Versão
- **Git**: Rastrear mudanças tanto em MD quanto HTML
- **Commits**: Incluir sempre contexto das alterações
- **Branches**: Usar para experimentos ou grandes modificações

## 📞 Suporte

Para dúvidas sobre a estrutura de artigos ou uso do SEO Article Builder:
- **E-mail**: suporte@caracore.com.br
- **Documentação**: Consultar handbook interno
- **Issues**: Criar issue no repositório para melhorias

---

*Última atualização: 4 de agosto de 2025*  
*Cara Core Informática - Organização de Conteúdo Técnico*
