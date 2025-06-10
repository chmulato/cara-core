"""
Script para listar todas as redes Wi-Fi salvas no Windows e suas respectivas senhas.

Este script utiliza o comando 'netsh' para obter os perfis de Wi-Fi e extrair as senhas salvas,
salvando o resultado em um arquivo 'wi_fi_pwd.txt' no mesmo diretório.

Requisitos:
- Execute o script como administrador para garantir acesso às senhas.
- Funciona em sistemas Windows com o utilitário netsh disponível.

Autor: Chritian Vladimir Uhdre Mulato
Data: Campo Largo, segunda-feira, 09 de Junho de 2025.
"""

import subprocess
import re

def get_wifi_passwords():
    # Executa o comando para listar todos os perfis de Wi-Fi salvos
    profiles_output = subprocess.check_output(
        ['netsh', 'wlan', 'show', 'profiles'],
        encoding='utf-8', errors='ignore'
    )
    # Expressão regular para encontrar os nomes dos perfis (SSID) em português ou inglês
    profiles = re.findall(r"Todos os Perfis de Usuários\s*:\s*(.*)", profiles_output)
    if not profiles:
        profiles = re.findall(r"All User Profile\s*:\s*(.*)", profiles_output)

    wifi_list = []
    for profile in profiles:
        profile = profile.strip()
        try:
            # Executa o comando para mostrar detalhes do perfil, incluindo a senha
            profile_info = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profile', f'name={profile}', 'key=clear'],
                encoding='utf-8', errors='ignore'
            )
            # Procura a senha na saída do comando (português ou inglês)
            password_match = re.search(r"Conteúdo da Chave\s*:\s*(.*)", profile_info)
            if not password_match:
                password_match = re.search(r"Key Content\s*:\s*(.*)", profile_info)
            password = password_match.group(1).strip() if password_match else "(Senha não encontrada)"
        except subprocess.CalledProcessError:
            # Caso ocorra erro ao acessar o perfil
            password = "(Erro ao acessar o perfil)"
        wifi_list.append({'SSID': profile, 'Senha': password})
    return wifi_list

if __name__ == "__main__":
    wifi_list = get_wifi_passwords()
    # Ordena a lista de redes pelo nome (SSID)
    wifi_list_sorted = sorted(wifi_list, key=lambda x: x['SSID'].lower())
    # Salva o resultado em um arquivo de texto
    with open("wi_fi_pwd.log", "w", encoding="utf-8") as f:
        f.write("Redes Wi-Fi e Senhas:\n\n")
        for wifi in wifi_list_sorted:
            f.write(f"SSID: {wifi['SSID']}\nSenha: {wifi['Senha']}\n{'-'*30}\n")
    print('Arquivo wi_fi_pwd.log gerado com sucesso!')