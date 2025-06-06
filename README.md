# Cara-Core Informática

Este repositório contém o site institucional da **Cara-Core Informática**, empresa especializada em soluções Microsoft 365, automação com Python, desenvolvimento de sites, suporte técnico, treinamentos em TI e segurança da informação.

---

## 📋 Índice

1. [Serviços Oferecidos](#-serviços-oferecidos)
2. [Área de Segurança](#-área-de-segurança)
   - [Monitoramento de Conexões de Rede](#monitoramento-de-conexões-de-rede)
3. [Como Compilar o Arquivo `monitor_exe.py`](#-como-compilar-o-arquivo-monitor_exepy-em-um-executável-no-windows)
4. [Estrutura do Projeto](#-estrutura-do-projeto)
5. [Como Visualizar o Site](#-como-visualizar)
6. [Como Gerar o PDF do Folder](#-como-gerar-o-pdf-do-folder)
7. [Observações](#-observações)
8. [Contato](#-contato)

---

## 🚀 Serviços Oferecidos

- **Consultoria Microsoft 365:** Implantação, configuração, migração e treinamento.
- **Automação com Python:** Integração de sistemas, geração de relatórios e otimização de processos.
- **Desenvolvimento de Sites:** Criação de sites institucionais, portfólios, blogs e landing pages responsivas.
- **Suporte Técnico:** Backup, antivírus, segurança da informação e orientação tecnológica.
- **Segurança Digital:** Backup em nuvem, proteção de dados, firewall e monitoramento de conexões.
- **Treinamentos:** Cursos em Microsoft 365, Excel, Python e produtividade digital.

---

## 🔒 Área de Segurança

O projeto inclui ferramentas para monitoramento e auditoria de conexões de rede em ambientes Windows, auxiliando na identificação de acessos suspeitos, análise forense e documentação de atividades.

### Monitoramento de Conexões de Rede

- **Descrição:** Script Python que monitora em tempo real as conexões de rede de todos os processos em execução no Windows.
- **Funcionalidades:**
  - Interface gráfica (Tkinter) com relatório ao vivo das conexões.
  - Filtro dinâmico por nome do processo.
  - Destaque visual para conexões em portas sensíveis (FTP, SSH, RDP, etc).
  - Exportação do relatório em formato CSV, incluindo timestamp detalhado.
  - Log automático das conexões detectadas e das interações do usuário.
- **Relatórios Possíveis:**
  - Relatório global (todas as conexões).
  - Relatório filtrado por processo.
  - Relatório por porta.
  - Relatório temporal (com timestamp).
  - Relatório de segurança (destaque para portas sensíveis).
- **Local do log:** O arquivo de log (`monitor.log`) é salvo automaticamente na mesma pasta onde o script Python é executado (raiz do diretório atual do terminal/IDE).

> **Requisitos:**  
> - Python 3  
> - Bibliotecas: `psutil`, `tkinter`, `csv`

---

## 🛠️ Como Compilar o Arquivo `monitor_exe.py` em um Executável no Windows

Para compilar o arquivo `monitor_exe.py` em um executável no Windows, siga os passos abaixo:

1. **Instale o PyInstaller**  
   Certifique-se de que o PyInstaller está instalado. Caso não esteja, você pode instalá-lo usando o seguinte comando no terminal:
   ```bash
   pip install pyinstaller
   ```

2. **Compile o arquivo Python**  
   No terminal, navegue até o diretório onde o arquivo `monitor_exe.py` está localizado e execute o seguinte comando:
   ```bash
   pyinstaller --onefile monitor_exe.py
   ```

   - A opção `--onefile` cria um único arquivo executável.
   - Você pode adicionar outras opções, como `--noconsole`, se não quiser que o console seja exibido ao executar o programa.

3. **Localize o executável gerado**  
   Após a execução do comando, o executável será gerado na pasta `dist`. Você pode encontrá-lo em:
   ```
   dist/monitor_exe.exe
   ```

4. **Teste o executável**  
   Execute o arquivo gerado para garantir que ele funciona como esperado:
   ```bash
   dist\monitor_exe.exe
   ```

### Observações
- Certifique-se de que todas as dependências do script Python estejam instaladas no ambiente antes de compilar.
- Caso precise incluir arquivos adicionais (como arquivos de configuração ou recursos), consulte a [documentação do PyInstaller](https://pyinstaller.org/en/stable/) para saber como configurá-los.

---

## 📂 Estrutura do Projeto

- `index.html` — Página principal do site.
- `planos.html` — Página de planos de desenvolvimento de sites.
- `folders/folder_py.html` — Folder digital com opção de exportar para PDF.
- `folders/apresentacao.md` — Apresentação da Cara-Core Informática.
- `images/` — Imagens e logotipos utilizados no site.
- `fonts/` — Fontes utilizadas no site.
- `js/` — Scripts JavaScript utilizados no site.
- `security/monitor_exe.py` — Script de monitoramento de conexões de rede (área de segurança).
- `README.md` — Este arquivo de documentação.

---

## 💻 Como Visualizar

1. Clone este repositório:
   ```sh
   git clone https://github.com/chmulato/cara-core.git
   ```
2. Abra a pasta no VS Code ou outro editor.
3. Abra o arquivo `index.html` ou qualquer outro arquivo `.html` em seu navegador.

---

## 📄 Como Gerar o PDF do Folder

1. Abra o arquivo `folders/folder_py.html` em seu navegador.
2. Clique no botão **"Baixar PDF"** para exportar o conteúdo do folder para um arquivo PDF em formato A4.

---

## 💡 Observações

- Para uso comercial da fonte Bellerose, adquira a licença em [harristype.com](http://www.harristype.com/fontstore.html).
- Os valores dos planos de sites são sugestões e podem ser ajustados conforme a necessidade do projeto.

---

## 📞 Contato

- WhatsApp: [41 9 9909-7797](https://wa.me/5541999097797)
- E-mail: [suporte@caracore.com.br](mailto:suporte@caracore.com.br)
- [Facebook](https://www.facebook.com/caracoreinformatica/)
- [YouTube](https://www.youtube.com/@caracoreinformatica7704)
- [LinkedIn](https://pt.linkedin.com/company/cara-core)
- [GitHub](https://github.com/chmulato)

---

Cara-Core Informática — Soluções em tecnologia para o seu negócio.