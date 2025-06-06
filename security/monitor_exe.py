# monitor_exe.py
# Monitoramento de Conexões de Rede de Todos os Processos no Windows
#
# Este script monitora em tempo real as conexões de rede estabelecidas por
# todos os processos em execução no Windows, destacando o uso das portas mais comuns
# (e-mail, web, banco de dados, acesso remoto, etc).
#
# Funcionalidades:
# - Interface gráfica (Tkinter) com relatório ao vivo das conexões.
# - Filtro dinâmico por nome do processo (permite visualizar apenas conexões de processos específicos).
# - Destaque visual para conexões em portas sensíveis (ex: FTP, SSH, RDP).
# - Exportação do relatório em formato CSV, incluindo timestamp detalhado.
# - Log automático das conexões detectadas e das interações do usuário.
#
# Perspectivas e combinações possíveis de relatórios:
# - Relatório global: mostra todas as conexões de todos os processos monitorados.
# - Relatório filtrado: permite visualizar apenas conexões de um ou mais processos específicos (ex: "chrome", "outlook", "svchost").
# - Relatório por porta: ao filtrar por nome de processo e observar a coluna "Porta", é possível identificar quais serviços cada processo está utilizando.
# - Relatório temporal: cada exportação ou log inclui timestamp detalhado, permitindo análise histórica e comparação entre diferentes momentos.
# - Relatório de segurança: destaque automático para conexões em portas sensíveis, facilitando a identificação de possíveis riscos ou acessos remotos.
#
# Local do arquivo de log:
# - O arquivo de log (monitor.log) é salvo automaticamente na mesma pasta onde o script Python é executado.
#   Ou seja, ele ficará na raiz do diretório atual do terminal/IDE onde você rodar o monitor_exe.py.
#
# Útil para:
# - Diagnóstico de rede e segurança.
# - Auditoria de processos e conexões.
# - Suporte técnico e documentação de ambientes.
# - Análise forense e acompanhamento de atividades suspeitas.
#
# Autor: Christian Vladimir Mulato
# Data: Junho de 2025
# Requisitos: psutil, tkinter, csv

import csv
import psutil
import socket
import time
import datetime
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

LOG_FILE = "monitor.log"

PORTS_INFO = {
    25:   ("SMTP", "Sem criptografia ou STARTTLS (pode negociar TLS, mas não é obrigatório)"),
    26:   ("SMTP Alternativo", "Alguns ISPs usam para SMTP"),
    110:  ("POP3", "Sem criptografia ou STARTTLS (pode negociar TLS, mas não é obrigatório)"),
    143:  ("IMAP", "Sem criptografia ou STARTTLS (pode negociar TLS, mas não é obrigatório)"),
    465:  ("SMTP", "SSL/TLS (criptografia obrigatória desde o início da conexão)"),
    587:  ("SMTP", "STARTTLS (conexão começa sem criptografia e negocia TLS)"),
    993:  ("IMAP", "SSL/TLS (criptografia obrigatória desde o início da conexão)"),
    995:  ("POP3", "SSL/TLS (criptografia obrigatória desde o início da conexão)"),
    2525: ("SMTP Alternativo", "Usado por alguns provedores para evitar bloqueios"),
    80:   ("HTTP", "Sem criptografia (web)"),
    443:  ("HTTPS", "TLS/SSL (usada para webmail, APIs e conexões seguras)"),
    8080: ("HTTP Alternativo", "Proxy ou aplicações web"),
    8443: ("HTTPS Alternativo", "Proxy ou aplicações web seguras"),
    21:   ("FTP", "Transferência de arquivos"),
    22:   ("SSH", "Acesso remoto seguro"),
    1433: ("SQL Server", "Banco de dados Microsoft SQL"),
    3306: ("MySQL", "Banco de dados MySQL"),
    5432: ("PostgreSQL", "Banco de dados PostgreSQL"),
    3389: ("RDP", "Acesso remoto Windows"),
    389:  ("LDAP", "Serviço de diretório"),
    636:  ("LDAPS", "LDAP seguro"),
}

PORTS_INFO.update({
    23:    ("Telnet", "Acesso remoto não seguro"),
    53:    ("DNS", "Resolução de nomes"),
    161:   ("SNMP", "Gerenciamento de dispositivos de rede"),
    162:   ("SNMP Trap", "Alertas de dispositivos de rede"),
    137:   ("NetBIOS Name", "Compartilhamento de arquivos Windows"),
    138:   ("NetBIOS Datagram", "Compartilhamento de arquivos Windows"),
    139:   ("NetBIOS Session", "Compartilhamento de arquivos Windows"),
    445:   ("SMB", "Compartilhamento de arquivos Windows"),
    5900:  ("VNC", "Acesso remoto VNC"),
    8081:  ("HTTP Alternativo", "Serviços web"),
    8888:  ("HTTP Proxy", "Proxy ou aplicações web"),
    5000:  ("Web Server", "Aplicações web/dev"),
    6379:  ("Redis", "Banco de dados Redis"),
    11211: ("Memcached", "Cache distribuído"),
    27017: ("MongoDB", "Banco de dados MongoDB"),
    9200:  ("Elasticsearch", "Busca e analytics"),
    25565: ("Minecraft", "Servidor de jogos"),
})

# Defina as portas sensíveis para destaque
PORTAS_SENSIVEIS = {21, 22, 3389}

monitorando = False
monitor_thread = None

def log_interacao(acao):
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {acao}\n")

def ler_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Nenhum log encontrado ainda.\n"

def get_executavel_connections():
    relatorio = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            nome = proc.info['name']
            conns = proc.net_connections(kind='inet')
            for c in conns:
                if not c.raddr:
                    continue
                porta = c.raddr.port
                if porta not in PORTS_INFO:
                    continue  # só mostra portas conhecidas
                proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
                ip_servidor = c.raddr.ip
                protocolo, criptografia = PORTS_INFO.get(
                    porta,
                    ("Desconhecido", "Desconhecido (porta não padrão para e-mail)")
                )
                relatorio.append({
                    "Aplicativo": nome,
                    "IP": ip_servidor,
                    "Porta": porta,
                    "Protocolo": protocolo,
                    "Criptografia": criptografia,
                    "Proto": proto,
                    "Status": c.status
                })
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return relatorio

def formatar_relatorio(relatorio):
    if not relatorio:
        return "Nenhuma conexão relevante encontrada.\n", []
    # Defina larguras fixas para cada coluna
    colunas = [
        ("Aplicativo", 22),
        ("IP", 39),
        ("Porta", 6),
        ("Protocolo", 13),
        ("Criptografia", 38),
        ("Proto", 5),
        ("Status", 12)
    ]
    # Cabeçalho
    saida = "\nRelatório de conexões de rede dos processos em execução:\n"
    saida += "".join(f"{nome:<{largura}}" for nome, largura in colunas) + "\n"
    saida += "-" * sum(largura for _, largura in colunas) + "\n"
    linhas_destaque = []
    for idx, item in enumerate(relatorio):
        linha = (
            f"{item['Aplicativo']:<22.22}"
            f"{item['IP']:<39.39}"
            f"{str(item['Porta']):<6}"
            f"{item['Protocolo']:<13.13}"
            f"{item['Criptografia']:<38.38}"
            f"{item['Proto']:<5.5}"
            f"{item['Status']:<12.12}\n"
        )
        saida += linha
        if int(item['Porta']) in PORTAS_SENSIVEIS:
            linhas_destaque.append(idx + 3)  # +3 por causa do cabeçalho e separador
    saida += "\nEssas informações mostram quais processos estão utilizando portas comuns de rede.\n"
    return saida, linhas_destaque

def escrever_log(texto):
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {texto}\n")

def monitorar(text_widget, log_widget, filtro_var=None):
    global monitorando
    while monitorando:
        relatorio = get_executavel_connections()
        # Aplica filtro se houver texto
        filtro = filtro_var.get().strip().lower() if filtro_var else ""
        if filtro:
            relatorio = [item for item in relatorio if filtro in item['Aplicativo'].lower()]
        texto, linhas_destaque = formatar_relatorio(relatorio)
        # Atualiza relatório ao vivo
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, texto)
        # Destaca linhas suspeitas
        for linha in linhas_destaque:
            start = f"{linha}.0"
            end = f"{linha}.end"
            text_widget.tag_add("suspeito", start, end)
        text_widget.tag_config("suspeito", foreground="red")
        text_widget.config(state=tk.DISABLED)
        # Escreve no log e atualiza log na tela
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        escrever_log(f"[{timestamp}] {texto.strip()}")
        log_widget.config(state=tk.NORMAL)
        log_widget.delete(1.0, tk.END)
        log_widget.insert(tk.END, ler_log())
        log_widget.config(state=tk.DISABLED)
        time.sleep(5)

def iniciar_monitoramento(text_widget, log_widget, btn_iniciar, btn_parar, status_label, status_var, filtro_var):
    global monitorando, monitor_thread
    if not monitorando:
        monitorando = True
        btn_iniciar.config(state=tk.DISABLED)
        btn_parar.config(state=tk.NORMAL)
        status_var.set("Ativo")
        status_label.config(text="Monitoramento: Ativo", fg="green")
        log_interacao("Monitoramento ativado")
        monitor_thread = threading.Thread(
            target=monitorar,
            args=(text_widget, log_widget, filtro_var),
            daemon=True
        )
        monitor_thread.start()

def parar_monitoramento(btn_iniciar, btn_parar, status_label, status_var):
    global monitorando
    if monitorando:
        monitorando = False
        btn_iniciar.config(state=tk.NORMAL)
        btn_parar.config(state=tk.DISABLED)
        status_var.set("Desativado")
        status_label.config(text="Monitoramento: Desativado", fg="red")
        log_interacao("Monitoramento desativado")
        print("Monitoramento parado.")

def criar_interface():
    root = tk.Tk()
    root.title("Monitoramento de Conexões de Processos")
    root.geometry("1400x550")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Variável para status do monitoramento
    status_var = tk.StringVar(value="Desativado")
    status_label = tk.Label(root, text="Monitoramento: Desativado", font=("Arial", 12, "bold"), fg="red")
    status_label.pack(pady=2)

    # Campo de filtro por nome do processo
    filtro_var = tk.StringVar()
    filtro_frame = tk.Frame(root)
    filtro_frame.pack(pady=2)
    tk.Label(filtro_frame, text="Filtrar por nome do processo:", font=("Arial", 11)).pack(side=tk.LEFT)
    filtro_entry = tk.Entry(filtro_frame, textvariable=filtro_var, width=30)
    filtro_entry.pack(side=tk.LEFT, padx=5)

    # Divide a tela em duas partes lado a lado
    left_frame = tk.Frame(frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_frame = tk.Frame(frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="Relatório Atual de Conexões", font=("Arial", 12, "bold")).pack()
    text_widget = ScrolledText(left_frame, wrap=tk.WORD, height=25, width=80, state=tk.DISABLED)
    text_widget.pack(pady=5, fill=tk.BOTH, expand=True)

    tk.Label(right_frame, text="Arquivo de Log", font=("Arial", 12, "bold")).pack()
    log_widget = ScrolledText(right_frame, wrap=tk.WORD, height=25, width=80, state=tk.DISABLED)
    log_widget.pack(pady=5, fill=tk.BOTH, expand=True)
    log_widget.config(state=tk.NORMAL)
    log_widget.insert(tk.END, ler_log())
    log_widget.config(state=tk.DISABLED)

    # Botões de ativar/desativar monitoramento e exportação
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    def iniciar():
        iniciar_monitoramento(text_widget, log_widget, btn_iniciar, btn_parar, status_label, status_var, filtro_var)

    def parar():
        parar_monitoramento(btn_iniciar, btn_parar, status_label, status_var)

    def sair():
        log_interacao("Aplicação encerrada pelo usuário")
        root.destroy()

    def atualizar_relatorio(*args):
        # O monitoramento já atualiza periodicamente, mas pode forçar aqui se quiser
        pass

    filtro_var.trace_add("write", atualizar_relatorio)

    def exportar_relatorio():
        relatorio = get_executavel_connections()
        filtro = filtro_var.get().strip().lower() if filtro_var else ""
        if filtro:
            relatorio = [item for item in relatorio if filtro in item['Aplicativo'].lower()]
        if not relatorio:
            messagebox.showinfo("Exportar Relatório", "Não há relatório para exportar.")
            return

        # Cabeçalho CSV com timestamp
        cabecalho = [
            "Timestamp", "Aplicativo", "IP", "Porta", "Protocolo", "Criptografia", "Proto", "Status"
        ]
        linhas = []
        for item in relatorio:
            timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
            linha = [
                timestamp,
                str(item["Aplicativo"]),
                str(item["IP"]),
                str(item["Porta"]),
                str(item["Protocolo"]),
                str(item["Criptografia"]),
                str(item["Proto"]),
                str(item["Status"])
            ]
            linhas.append(linha)

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            title="Salvar Relatório Como"
        )
        if arquivo:
            # Adiciona BOM para garantir compatibilidade com Excel
            with open(arquivo, "w", encoding="utf-8-sig", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(cabecalho)
                writer.writerows(linhas)
            messagebox.showinfo("Exportar Relatório", f"Relatório exportado para:\n{arquivo}")
            log_interacao(f"Relatório exportado para {arquivo}")

    btn_iniciar = tk.Button(btn_frame, text="Ativar Monitoramento", width=22, command=iniciar)
    btn_iniciar.pack(side=tk.LEFT, padx=5)

    btn_parar = tk.Button(btn_frame, text="Desativar Monitoramento", width=22, command=parar, state=tk.DISABLED)
    btn_parar.pack(side=tk.LEFT, padx=5)

    btn_exportar = tk.Button(btn_frame, text="Exportar Relatório", width=22, command=exportar_relatorio)
    btn_exportar.pack(side=tk.LEFT, padx=5)

    btn_sair = tk.Button(btn_frame, text="Sair", width=10, command=sair)
    btn_sair.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()