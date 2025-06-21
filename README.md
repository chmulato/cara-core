# Cara-Core Informática

Este repositório contém o site institucional da **Cara-Core Informática**, empresa especializada em soluções Microsoft 365, automação com Python, desenvolvimento de sites, suporte técnico, treinamentos em TI e segurança da informação.

---

## 📋 Índice

- [Cara-Core Informática](#cara-core-informática)
  - [📋 Índice](#-índice)
  - [🚀 Serviços Oferecidos](#-serviços-oferecidos)
  - [🔒 Área de Segurança](#-área-de-segurança)
    - [Monitoramento de Conexões de Rede](#monitoramento-de-conexões-de-rede)
    - [Listagem de Redes Wi-Fi Salvas e Senhas](#listagem-de-redes-wi-fi-salvas-e-senhas)
  - [📂 Estrutura do Projeto](#-estrutura-do-projeto)
  - [💻 Como Visualizar](#-como-visualizar)
  - [📄 Como Gerar o PDF do Folder](#-como-gerar-o-pdf-do-folder)
  - [💡 Observações](#-observações)
  - [📞 Contato](#-contato)
  - [Adendo: Como Compilar Scripts Python em Executáveis](#adendo-como-compilar-scripts-python-em-executáveis)
    - [Compilando `monitor_exe.py`](#compilando-monitor_exepy)
    - [Compilando `get_wi_fi.py`](#compilando-get_wi_fipy)

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

Ferramentas para monitoramento e auditoria de conexões de rede e redes Wi-Fi em ambientes Windows, auxiliando na identificação de acessos suspeitos, análise forense e documentação de atividades.

### Monitoramento de Conexões de Rede

- **Script:** `security/monitor_exe.py`
- **Descrição:** Monitora em tempo real as conexões de rede de todos os processos em execução no Windows.
- **Funcionalidades:** Interface gráfica, filtro por processo, destaque para portas sensíveis, exportação CSV, log automático.
- **Requisitos:** Python 3, bibliotecas `psutil`, `tkinter`, `csv`.

### Listagem de Redes Wi-Fi Salvas e Senhas

- **Script:** `wi_fi/get_wi_fi.py`
- **Descrição:** Lista todas as redes Wi-Fi salvas no Windows e suas respectivas senhas.
- **Funcionalidades:** Gera `wi_fi_pwd.log` com SSIDs e senhas. Compatível com sistemas em português e inglês.
- **Requisitos:** Python 3, utilitário `netsh` disponível no Windows.

---

## 📂 Estrutura do Projeto

```text
cara-core/
├── index.html                  # Página principal do site
├── planos.html                 # Página de planos de desenvolvimento de sites
├── folders/
│   ├── folder_py.html          # Folder digital com opção de exportar para PDF
│   └── apresentacao.md         # Apresentação institucional em Markdown
├── images/                     # Imagens e logotipos utilizados no site
├── fonts/                      # Fontes utilizadas no site
├── js/                         # Scripts JavaScript utilizados no site
├── security/
│   └── monitor_exe.py          # Script de monitoramento de conexões de rede (área de segurança)
├── wi_fi/
│   └── get_wi_fi.py            # Script para listar redes Wi-Fi salvas e senhas (área de segurança)
├── handbook/                   # Apostilas, manuais e scripts de conversão para HTML
│   ├── HANDBOOK.md             # Apostila Microsoft 365 em Markdown (editável)
│   ├── HANDBOOK.html           # Apostila convertida para HTML responsivo
│   ├── HANDBOOK.py             # Script Python para converter e ajustar a apostila
│   ├── SERVICEGUIDE.md         # Manual de serviços em Markdown (editável)
│   ├── SERVICEGUIDE.html       # Manual de serviços convertido para HTML responsivo
│   ├── SERVICEGUIDE.py         # Script Python para converter e ajustar o manual de serviços
│   ├── images/                 # Imagens e anexos utilizados na apostila/manual
│   └── README.md               # Documentação específica da pasta handbook
├── README.md                   # Este arquivo de documentação principal
└── LICENSE                     # Licença de uso do material
```

**Descrição dos principais arquivos e pastas:**

- `index.html`: Página inicial do site institucional.
- `planos.html`: Detalhamento dos planos de desenvolvimento de sites.
- `folders/folder_py.html`: Folder digital interativo, com opção de exportação para PDF.
- `folders/apresentacao.md`: Apresentação institucional em Markdown.
- `images/`: Imagens, logotipos e recursos visuais.
- `fonts/`: Fontes utilizadas no site.
- `js/`: Scripts JavaScript para funcionalidades do site.
- `security/monitor_exe.py`: Script para monitoramento de conexões de rede.
- `wi_fi/get_wi_fi.py`: Script para listar redes Wi-Fi e senhas salvas.
- `README.md`: Documentação do projeto.
- `LICENSE`: Licença de uso.
- `handbook/HANDBOOK.md`: Apostila principal sobre Microsoft 365 (editável em Markdown).
- `handbook/HANDBOOK.html`: Apostila convertida para HTML responsivo.
- `handbook/HANDBOOK.py`: Script Python para converter e ajustar a apostila.
- `handbook/SERVICEGUIDE.md`: Manual de serviços e processos (editável em Markdown).
- `handbook/SERVICEGUIDE.html`: Manual de serviços convertido para HTML responsivo.
- `handbook/SERVICEGUIDE.py`: Script Python para converter e ajustar o manual de serviços.
- `handbook/images/`: Imagens e anexos usados na apostila e no manual.
- `handbook/README.md`: Documentação específica da pasta handbook. 

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

Se desejar transformar os scripts Python deste projeto em executáveis para Windows, siga os passos abaixo:

### Compilando `monitor_exe.py`

1. Instale o PyInstaller  
   ```sh
   pip install pyinstaller
   ```
2. Compile o arquivo Python  
   ```sh
   pyinstaller --onefile monitor_exe.py
   ```
   - Para ocultar o console:
     ```sh
     pyinstaller --onefile --noconsole monitor_exe.py
     ```
3. O executável estará em `dist/monitor_exe.exe`.

### Compilando `get_wi_fi.py`

1. Instale o PyInstaller  
   ```sh
   pip install pyinstaller
   ```
2. Compile o arquivo Python  
   ```sh
   pyinstaller --onefile get_wi_fi.py
   ```
   - Para ocultar o console:
     ```sh
     pyinstaller --onefile --noconsole get_wi_fi.py
     ```
3. O executável estará em `dist/get_wi_fi.exe`.
4. Execute como administrador para listar as senhas das redes Wi-Fi.

> Consulte a [documentação do PyInstaller](https://pyinstaller.org/en/stable/) para opções avançadas.

---

Cara-Core Informática — Soluções em tecnologia para o seu negócio.