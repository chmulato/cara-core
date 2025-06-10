# Cara-Core Informática

Este repositório contém o site institucional da **Cara-Core Informática**, empresa especializada em soluções Microsoft 365, automação com Python, desenvolvimento de sites, suporte técnico, treinamentos em TI e segurança da informação.

---

## 📋 Índice

1. [Serviços Oferecidos](#-serviços-oferecidos)
2. [Área de Segurança](#-área-de-segurança)
   - [Monitoramento de Conexões de Rede](#monitoramento-de-conexões-de-rede)
   - [Listagem de Redes Wi-Fi Salvas e Senhas](#listagem-de-redes-wi-fi-salvas-e-senhas)
3. [Estrutura do Projeto](#-estrutura-do-projeto)
4. [Como Visualizar o Site](#-como-visualizar)
5. [Como Gerar o PDF do Folder](#-como-gerar-o-pdf-do-folder)
6. [Observações](#-observações)
7. [Contato](#-contato)
8. [Adendo: Como Compilar Scripts Python em Executáveis](#adendo-como-compilar-scripts-python-em-executáveis)

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

O projeto inclui ferramentas para monitoramento e auditoria de conexões de rede e redes Wi-Fi em ambientes Windows, auxiliando na identificação de acessos suspeitos, análise forense e documentação de atividades.

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

### Listagem de Redes Wi-Fi Salvas e Senhas

- **Descrição:** Script Python que lista todas as redes Wi-Fi salvas no Windows e suas respectivas senhas.
- **Funcionalidades:**
  - Gera um arquivo `wi_fi_pwd.log` com o nome das redes (SSID) e suas senhas.
  - Compatível com sistemas Windows (necessário executar como administrador).
  - Suporte a sistemas em português e inglês.
- **Como usar:**
  1. Execute o script `get_wi_fi.py` com privilégios de administrador:
     ```sh
     python wi_fi/get_wi_fi.py
     ```
  2. O arquivo `wi_fi_pwd.log` será gerado no mesmo diretório do script.
- **Requisitos:**
  - Python 3
  - Utilitário `netsh` disponível no Windows

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
- `wi_fi/get_wi_fi.py` — Script para listar redes Wi-Fi salvas e senhas (área de segurança).
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
- [Site](https://caracore.com.br)

---

## Adendo: Como Compilar Scripts Python em Executáveis

Se desejar transformar os scripts Python deste projeto em executáveis para Windows, siga os passos abaixo (curiosidade):

### Compilando `monitor_exe.py`

1. **Instale o PyInstaller**  
   ```bash
   pip install pyinstaller
   ```

2. **Compile o arquivo Python**  
   No terminal, navegue até o diretório onde está o arquivo `monitor_exe.py` e execute:
   ```bash
   pyinstaller --onefile monitor_exe.py
   ```
   - Para ocultar o console, adicione a opção `--noconsole`:
     ```bash
     pyinstaller --onefile --noconsole monitor_exe.py
     ```

3. **Localize o executável gerado**  
   O arquivo estará em:
   ```
   dist/monitor_exe.exe
   ```

4. **Teste o executável**  
   Execute o arquivo gerado para garantir que ele funciona como esperado:
   ```bash
   dist\monitor_exe.exe
   ```

> **Observações:**  
> - Certifique-se de que todas as dependências do script estejam instaladas.  
> - Consulte a [documentação do PyInstaller](https://pyinstaller.org/en/stable/) para opções avançadas.

---

### Compilando `get_wi_fi.py`

1. **Instale o PyInstaller**  
   ```bash
   pip install pyinstaller
   ```

2. **Compile o arquivo Python**  
   No terminal, navegue até o diretório onde está o arquivo `get_wi_fi.py` e execute:
   ```bash
   pyinstaller --onefile get_wi_fi.py
   ```
   - Para ocultar o console, adicione a opção `--noconsole`:
     ```bash
     pyinstaller --onefile --noconsole get_wi_fi.py
     ```

3. **Localize o executável gerado**  
   O arquivo estará em:
   ```
   dist/get_wi_fi.exe
   ```

4. **Execute como administrador**  
   Para listar as senhas das redes Wi-Fi, execute o `get_wi_fi.exe` como administrador (clique com o botão direito e escolha "Executar como administrador").

> **Observações:**  
> - Certifique-se de que o utilitário `netsh` está disponível no sistema.  
> - O arquivo de saída `wi_fi_pwd.log` será gerado no mesmo diretório do executável.  
> - Consulte a [documentação do PyInstaller](https://pyinstaller.org/en/stable/) para opções avançadas.

---

Cara-Core Informática — Soluções em tecnologia para o seu negócio.